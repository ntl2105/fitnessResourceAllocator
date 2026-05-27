from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from math import ceil
import re
from typing import Any

from src.models.availability import AvailabilityData
from src.models.schedule import CalendarRow, PersonalizedPlan, ScheduledTask, TaskInstance
from src.models.trace import ConstraintCheck, DecisionTrace
from src.scheduler.availability import check_required_resources
from src.scheduler.placement import candidate_slots, sort_tasks
from src.scheduler.policy import evaluate_policy
from src.scheduler.traces import provider_handoff_summary


@dataclass
class SchedulingResult:
    plan: PersonalizedPlan
    calendar_rows: list[CalendarRow]
    traces: list[DecisionTrace]
    rejection_summary: dict[str, Any]


def schedule_tasks(
    tasks: list[TaskInstance],
    activities: dict[str, dict[str, Any]],
    availability: AvailabilityData,
    run_id: str = "demo-run",
    travel_time_rules: list[Any] | None = None,
    goal_actions: list[dict[str, Any]] | None = None,
    weekly_goal_actions: list[dict[str, Any]] | None = None,
    source_artifact_paths: list[str] | None = None,
) -> SchedulingResult:
    plan = PersonalizedPlan(run_id=run_id, tasks=[], metadata={"scheduler": "simple_explainable"})
    rows: list[CalendarRow] = []
    traces: list[DecisionTrace] = []
    rejection_summary: dict[str, dict[str, int]] = {}
    weekly_actions = weekly_goal_action_map(goal_actions, weekly_goal_actions)
    scheduled_goal_units: Counter[tuple[str, str]] = Counter()
    goal_report_units: Counter[tuple[str, str]] = Counter()
    scheduled_primary_counts: Counter[tuple[str, str]] = Counter()
    trace_source_paths = source_artifact_paths or [
        "data/action_plan.json",
        "data/availability.json",
    ]

    for task_group in grouped_task_instances(tasks, activities):
        task_group, planned_variety_reason = order_group_for_planned_variety(
            task_group, activities, scheduled_primary_counts
        )
        scheduled_for_group: ScheduledTask | None = None
        scheduled_activity_title: str | None = None
        primary_attempted = planned_variety_reason is not None or not any(
            not task.is_substitution for task in task_group
        )
        primary_failure_summary: str | None = None

        for task in task_group:
            activity = activities.get(task.activity_id, {})
            if task.is_substitution and not primary_attempted:
                traces.append(
                    skipped_trace(
                        task,
                        activity,
                        "Skipped because substitutions are only considered after the primary activity in the same family occurrence has been attempted.",
                        trace_source_paths,
                    )
                )
                continue
            if scheduled_for_group is not None:
                traces.append(
                    skipped_trace(
                        task,
                        activity,
                        "Skipped because "
                        f"{scheduled_activity_title or scheduled_for_group.activity_id} "
                        "was already scheduled for this activity family occurrence.",
                        trace_source_paths,
                    )
                )
                continue
            if not task.is_substitution:
                primary_attempted = True

            scheduled = try_schedule_task(
                task,
                activity,
                availability,
                plan,
                rows,
                traces,
                rejection_summary,
                scheduled_goal_units,
                goal_report_units,
                weekly_actions,
                travel_time_rules or [],
                trace_source_paths,
                planned_variety_reason
                if task.is_substitution and planned_variety_reason
                else primary_failure_summary
                if task.is_substitution
                else None,
            )
            if not task.is_substitution and scheduled is None and traces:
                primary_failure_summary = failed_primary_summary(traces[-1], activity)
            if scheduled is not None:
                scheduled_for_group = scheduled
                scheduled_activity_title = activity.get("title", task.activity_id)
                if not task.is_substitution:
                    scheduled_primary_counts[
                        (task.activity_family_id, task.target_week or iso_week_id(task.target_date))
                    ] += 1

    plan.metadata["scheduled_count"] = len(plan.tasks)
    plan.metadata["unscheduled_count"] = sum(
        1 for trace in traces if trace.final_status == "unscheduled"
    )
    plan.metadata["skipped_count"] = sum(
        1 for trace in traces if trace.final_status == "skipped"
    )
    plan.goal_report = build_goal_report(
        weekly_actions,
        goal_report_units,
        availability.planning_start_date,
        availability.planning_months,
    )
    plan.goal_report["weekly_validation"] = build_weekly_validation(
        plan.tasks,
        activities,
        plan.goal_report.get("weekly", []),
    )
    return SchedulingResult(plan=plan, calendar_rows=rows, traces=traces, rejection_summary=rejection_summary)


def grouped_task_instances(
    tasks: list[TaskInstance],
    activities: dict[str, dict[str, Any]],
) -> list[list[TaskInstance]]:
    groups: dict[tuple[str, date | None, str], list[TaskInstance]] = defaultdict(list)
    for task in tasks:
        groups[task_group_key(task)].append(task)
    return sorted(
        (ordered_group_tasks(group) for group in groups.values()),
        key=lambda group: task_order_key(representative_task(group, activities)),
    )


def task_group_key(task: TaskInstance) -> tuple[str, date | None, str]:
    return (
        task.activity_family_id,
        task.target_date,
        occurrence_suffix(task.task_instance_id),
    )


def occurrence_suffix(task_instance_id: str) -> str:
    match = re.search(r"_(\d{3})$", task_instance_id)
    return match.group(1) if match else "001"


def ordered_group_tasks(tasks: list[TaskInstance]) -> list[TaskInstance]:
    return sorted(
        tasks,
        key=lambda task: (
            1 if task.is_substitution else 0,
            task.priority + (0.5 if task.is_substitution else 0),
            task.activity_id,
            task.task_instance_id,
        ),
    )


def order_group_for_planned_variety(
    tasks: list[TaskInstance],
    activities: dict[str, dict[str, Any]],
    scheduled_primary_counts: Counter[tuple[str, str]],
) -> tuple[list[TaskInstance], str | None]:
    primary_tasks = [task for task in tasks if not task.is_substitution]
    if not primary_tasks:
        return tasks, None
    primary_task = sort_tasks(primary_tasks)[0]
    primary_activity = activities.get(primary_task.activity_id, {})
    cap = primary_activity.get("weekly_primary_cap")
    if not isinstance(cap, int) or cap <= 0:
        return tasks, None
    week_id = primary_task.target_week or iso_week_id(primary_task.target_date)
    if scheduled_primary_counts[(primary_task.activity_family_id, week_id)] < cap:
        return tasks, None
    planned_variety_tasks = [
        task
        for task in tasks
        if task.is_substitution
        and activities.get(task.activity_id, {}).get("variety_role") == "planned_variety"
    ]
    if not planned_variety_tasks:
        return tasks, None
    planned_variety_ids = {task.task_instance_id for task in planned_variety_tasks}
    ordered = [
        *sorted(planned_variety_tasks, key=lambda task: (task.priority, task.activity_id)),
        *[task for task in tasks if task.task_instance_id not in planned_variety_ids],
    ]
    return (
        ordered,
        "Substitution used for planned variety after primary weekly cap was met.",
    )


def representative_task(
    tasks: list[TaskInstance],
    activities: dict[str, dict[str, Any]],
) -> TaskInstance:
    primary_tasks = [task for task in tasks if not task.is_substitution]
    if primary_tasks:
        return sort_tasks(primary_tasks)[0]
    return sort_tasks(tasks)[0]


def task_order_key(task: TaskInstance) -> tuple[float, date, str, str]:
    return (
        task.priority + (0.5 if task.is_substitution else 0),
        task.target_date or date.max,
        task.activity_id,
        task.task_instance_id,
    )


def try_schedule_task(
    task: TaskInstance,
    activity: dict[str, Any],
    availability: AvailabilityData,
    plan: PersonalizedPlan,
    rows: list[CalendarRow],
    traces: list[DecisionTrace],
    rejection_summary: dict[str, dict[str, int]],
    scheduled_goal_units: Counter[tuple[str, str]],
    goal_report_units: Counter[tuple[str, str]],
    weekly_actions: dict[str, dict[str, Any]],
    travel_time_rules: list[Any],
    trace_source_paths: list[str],
    substitution_context: str | None = None,
) -> ScheduledTask | None:
    cap_reason = weekly_goal_cap_reason(
        task, activity, scheduled_goal_units, weekly_actions
    )
    if cap_reason:
        traces.append(skipped_trace(task, activity, cap_reason, trace_source_paths))
        return None

    unlinked_support_reason = unlinked_support_skip_reason(task, activity)
    if unlinked_support_reason:
        traces.append(
            skipped_trace(task, activity, unlinked_support_reason, trace_source_paths)
        )
        return None

    trace = place_task(
        task,
        activity,
        availability,
        plan.tasks,
        travel_time_rules,
        trace_source_paths,
    )
    if task.is_substitution and substitution_context:
        if substitution_context.startswith("Substitution used for planned variety"):
            trace.substitution_reason = substitution_context
        else:
            base_reason = substitution_reason_summary(task, activity)
            trace.substitution_reason = (
                f"Substitution used after primary failed: {substitution_context}"
                + (f" {base_reason}" if base_reason else "")
            )
    traces.append(trace)

    if trace.final_status != "scheduled" or not trace.selected_slot:
        summary = rejection_summary.setdefault(
            task.activity_id,
            {"unscheduled_count": 0, "rejected_candidate_count": 0},
        )
        summary["unscheduled_count"] += 1
        summary["rejected_candidate_count"] += len(trace.rejected_candidates)
        return None

    selected = trace.selected_slot
    scheduled_activity_type = calendar_activity_type(activity)
    scheduled = ScheduledTask(
        task_id=task.task_instance_id,
        activity_id=task.activity_id,
        activity_family_id=task.activity_family_id,
        title=activity.get("title", task.activity_id),
        goal_tags=task.goal_tags,
        start=selected["start"],
        end=selected["end"],
        activity_type=scheduled_activity_type,
        load_level=activity.get("load_level", "unknown"),
        location_id=selected.get("location_id"),
        provider_ids=task.required_resources.get("provider_ids", []),
        equipment_ids=task.required_resources.get("equipment_ids", []),
        status="scheduled",
        trace_id=trace.trace_id,
    )
    plan.tasks.append(scheduled)
    rows.append(calendar_row(task, activity, scheduled, trace.trace_id))
    add_weekly_goal_units(task, activity, scheduled_goal_units, weekly_actions)
    add_goal_report_units(task, activity, goal_report_units, weekly_actions)
    return scheduled


def failed_primary_summary(trace: DecisionTrace, activity: dict[str, Any]) -> str | None:
    title = activity.get("title", activity.get("activity_id", "primary activity"))
    if trace.final_status == "scheduled":
        return None
    if trace.rejected_candidates:
        first_reasons = trace.rejected_candidates[0].get("reasons", [])
        reason = first_reasons[0] if first_reasons else "no candidate slot passed"
        return f"{title} could not be scheduled; first failed candidate reason: {reason}."
    if trace.policy_fit_summary:
        return f"{title} was not used: {trace.policy_fit_summary}"
    return f"{title} was not used."


def skipped_trace(
    task: TaskInstance,
    activity: dict[str, Any],
    reason: str,
    source_artifact_paths: list[str],
) -> DecisionTrace:
    return DecisionTrace(
        trace_id=f"trace_{task.task_instance_id}",
        task_instance_id=task.task_instance_id,
        activity_id=task.activity_id,
        final_status="skipped",
        selected_slot=None,
        policy_fit_summary=reason,
        resource_fit_summary="No placement attempted.",
        constraint_checks=[],
        rejected_candidates=[],
        substitution_reason=substitution_reason_summary(task, activity),
        dependency_checks=[],
        provider_handoff_summary=provider_handoff_summary(activity),
        source_artifact_paths=source_artifact_paths,
    )


def weekly_goal_cap_reason(
    task: TaskInstance,
    activity: dict[str, Any],
    scheduled_goal_units: Counter[tuple[str, str]],
    weekly_actions: dict[str, dict[str, Any]],
) -> str | None:
    if activity.get("activity_type") == "food" and activity.get("meal_slot"):
        return None
    contributions = counting_goal_contributions(activity, weekly_actions)
    if not contributions:
        return None
    week_id = task.target_week or iso_week_id(task.target_date)
    capped = []
    for contribution in contributions:
        action_id = goal_contribution_action_id(contribution)
        if action_id is None:
            continue
        target = weekly_goal_action_target(weekly_actions[action_id])
        if target <= 0:
            continue
        current = scheduled_goal_units[(action_id, week_id)]
        if current + contribution_value(contribution) > target:
            capped.append(weekly_actions[action_id].get("label", action_id))
    if len(capped) == len(contributions):
        return (
            "Skipped because weekly target coverage is already met for "
            f"{', '.join(capped)}."
        )
    return None


def add_weekly_goal_units(
    task: TaskInstance,
    activity: dict[str, Any],
    scheduled_goal_units: Counter[tuple[str, str]],
    weekly_actions: dict[str, dict[str, Any]],
) -> None:
    week_id = task.target_week or iso_week_id(task.target_date)
    for contribution in counting_goal_contributions(activity, weekly_actions):
        action_id = goal_contribution_action_id(contribution)
        if action_id is not None:
            scheduled_goal_units[(action_id, week_id)] += contribution_value(contribution)


def add_goal_report_units(
    task: TaskInstance,
    activity: dict[str, Any],
    goal_report_units: Counter[tuple[str, str]],
    actions: dict[str, dict[str, Any]],
) -> None:
    for contribution in counting_goal_contributions(activity, actions):
        action_id = goal_contribution_action_id(contribution)
        if action_id is None:
            continue
        period = goal_action_period(actions[action_id])
        if period == "weekly":
            period_key = task.target_week or iso_week_id(task.target_date)
            if activity.get("activity_type") == "food":
                target = weekly_goal_action_target(actions[action_id])
                if target > 0 and goal_report_units[(action_id, period_key)] >= target:
                    continue
        elif period == "3_month":
            period_key = "3_month"
        else:
            continue
        goal_report_units[(action_id, period_key)] += contribution_value(contribution)


def counting_goal_contributions(
    activity: dict[str, Any],
    weekly_actions: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    contributions = []
    for contribution in activity.get("goal_contributions", []):
        action_id = goal_contribution_action_id(contribution)
        action = weekly_actions.get(action_id)
        if not action or action.get("support_only"):
            continue
        if contribution.get("counts_toward_weekly_target") is False:
            continue
        contributions.append(contribution)
    return contributions


def weekly_goal_action_map(
    goal_actions: list[dict[str, Any]] | None,
    weekly_goal_actions: list[dict[str, Any]] | None,
) -> dict[str, dict[str, Any]]:
    actions: dict[str, dict[str, Any]] = {}
    for action in weekly_goal_actions or []:
        action_id = action.get("weekly_goal_action_id")
        if action_id:
            actions[action_id] = action
    for action in goal_actions or []:
        action_id = action.get("goal_action_id") or action.get("weekly_goal_action_id")
        if action_id:
            actions[action_id] = action
    return actions


def goal_contribution_action_id(contribution: dict[str, Any]) -> str | None:
    return contribution.get("goal_action_id") or contribution.get("weekly_goal_action_id")


def weekly_goal_action_target(action: dict[str, Any]) -> float:
    target = action.get("target")
    if isinstance(target, dict):
        if target.get("period") != "weekly":
            return 0.0
        value = target.get("units")
    else:
        value = action.get("target_per_week")
    return float(value) if isinstance(value, (int, float)) else 0.0


def goal_action_period(action: dict[str, Any]) -> str | None:
    target = action.get("target")
    if isinstance(target, dict):
        return target.get("period")
    if action.get("target_per_week") is not None:
        return "weekly"
    return None


def goal_action_target_units(action: dict[str, Any]) -> float:
    target = action.get("target")
    if isinstance(target, dict):
        value = target.get("units")
    else:
        value = action.get("target_per_week")
    return float(value) if isinstance(value, (int, float)) else 0.0


def goal_action_unit_label(action: dict[str, Any]) -> str:
    target = action.get("target")
    if isinstance(target, dict):
        return str(target.get("unit_label") or "units")
    return str(action.get("unit_label") or "units")


def build_goal_report(
    actions: dict[str, dict[str, Any]],
    goal_report_units: Counter[tuple[str, str]],
    horizon_start: date,
    planning_months: int,
) -> dict[str, Any]:
    horizon_end = add_months_for_report(horizon_start, planning_months)
    week_ids = iso_weeks_between(horizon_start, horizon_end)
    weekly: list[dict[str, Any]] = []
    three_month: list[dict[str, Any]] = []

    for action_id, action in sorted(actions.items()):
        if action.get("support_only"):
            continue
        period = goal_action_period(action)
        target_units = goal_action_target_units(action)
        common = {
            "goal_action_id": action_id,
            "label": action.get("label", action_id),
            "target_units": target_units,
            "unit_label": goal_action_unit_label(action),
        }
        if period == "weekly":
            for week_id in week_ids:
                scheduled_units = goal_report_units[(action_id, week_id)]
                weekly.append(
                    {
                        **common,
                        "period": "weekly",
                        "week": week_id,
                        "scheduled_units": scheduled_units,
                        "met": scheduled_units >= target_units if target_units > 0 else False,
                    }
                )
        elif period == "3_month":
            scheduled_units = goal_report_units[(action_id, "3_month")]
            three_month.append(
                {
                    **common,
                    "period": "3_month",
                    "scheduled_units": scheduled_units,
                    "met": scheduled_units >= target_units if target_units > 0 else False,
                }
            )

    return {
        "horizon_start": horizon_start.isoformat(),
        "horizon_end_exclusive": horizon_end.isoformat(),
        "weekly": weekly,
        "three_month": three_month,
        "summary": {
            "weekly_met_count": sum(1 for item in weekly if item["met"]),
            "weekly_total_count": len(weekly),
            "three_month_met_count": sum(1 for item in three_month if item["met"]),
            "three_month_total_count": len(three_month),
        },
    }


WEEKLY_VALIDATION_TARGETS = {
    "ga_structured_meals_weekly": (
        "countable_structured_meals_target",
        "Countable structured meals",
        "target",
        14.0,
    ),
    "ga_aerobic_conditioning_weekly": (
        "aerobic_sessions_target",
        "Aerobic sessions",
        "target",
        2.0,
    ),
    "ga_strength_sessions_weekly": (
        "strength_sessions_target",
        "Strength sessions",
        "target",
        2.0,
    ),
    "ga_sleep_recovery_weekly": (
        "recovery_actions_target",
        "Recovery actions",
        "target",
        4.0,
    ),
}


def build_weekly_validation(
    scheduled_tasks: list[ScheduledTask],
    activities: dict[str, dict[str, Any]],
    weekly_goal_report: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    validations: list[dict[str, Any]] = []

    for item in weekly_goal_report:
        goal_id = item.get("goal_action_id")
        if goal_id not in WEEKLY_VALIDATION_TARGETS:
            continue
        check_id, label, rule, expected_units = WEEKLY_VALIDATION_TARGETS[goal_id]
        actual_units = float(item.get("scheduled_units", 0))
        validations.append(
            weekly_validation_item(
                check_id,
                label,
                item["week"],
                actual_units,
                expected_units,
                rule,
            )
        )

    member_assembled_by_week: Counter[str] = Counter()
    chef_prepped_meals_by_week: Counter[str] = Counter()
    for task in scheduled_tasks:
        activity = activities.get(task.activity_id, {})
        if activity.get("activity_type") != "food":
            continue
        week_id = iso_week_id(task.start.date())
        source = activity.get("prep_source") or activity.get("dining_source")
        if source == "member_assembled":
            member_assembled_by_week[week_id] += 1
        if source == "chef_prepped":
            chef_prepped_meals_by_week[week_id] += 1

    weeks = sorted(
        {
            *[item["week"] for item in weekly_goal_report if item.get("week")],
            *member_assembled_by_week.keys(),
            *chef_prepped_meals_by_week.keys(),
        }
    )
    for week_id in weeks:
        validations.append(
            weekly_validation_item(
                "member_assembled_meals_cap",
                "Member-assembled meals",
                week_id,
                float(member_assembled_by_week[week_id]),
                2.0,
                "max",
            )
        )
        validations.append(
            weekly_validation_item(
                "chef_prep_sessions_cap",
                "Chef prep sessions",
                week_id,
                float(estimated_chef_prep_sessions(chef_prepped_meals_by_week[week_id])),
                2.0,
                "max",
                {"chef_prepped_meal_rows": chef_prepped_meals_by_week[week_id]},
            )
        )
    return sorted(validations, key=lambda item: (item["week"], item["check_id"]))


def weekly_validation_item(
    check_id: str,
    label: str,
    week: str,
    actual_units: float,
    expected_units: float,
    rule: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if rule == "max":
        met = actual_units <= expected_units
    else:
        met = actual_units == expected_units
    return {
        "check_id": check_id,
        "label": label,
        "week": week,
        "actual_units": actual_units,
        "expected_units": expected_units,
        "rule": rule,
        "met": met,
        **({"details": details} if details else {}),
    }


def estimated_chef_prep_sessions(chef_prepped_meal_rows: int) -> int:
    if chef_prepped_meal_rows <= 0:
        return 0
    return min(2, ceil(chef_prepped_meal_rows / 7))


def iso_weeks_between(horizon_start: date, horizon_end: date) -> list[str]:
    week_ids = []
    seen = set()
    current = horizon_start
    while current < horizon_end:
        week_id = iso_week_id(current)
        if week_id not in seen:
            seen.add(week_id)
            week_ids.append(week_id)
        current += timedelta(days=1)
    return week_ids


def add_months_for_report(value: date, months: int) -> date:
    month = value.month - 1 + months
    year = value.year + month // 12
    month = month % 12 + 1
    day = min(value.day, 28)
    return date(year, month, day)


def contribution_value(contribution: dict[str, Any]) -> float:
    value = contribution.get("value", 1)
    return float(value) if isinstance(value, (int, float)) else 1.0


def iso_week_id(value: date | None) -> str:
    if value is None:
        return "unknown-week"
    iso = value.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def unlinked_support_skip_reason(task: TaskInstance, activity: dict[str, Any]) -> str | None:
    contributions = activity.get("goal_contributions", [])
    non_counting = bool(contributions) and all(
        contribution.get("counts_toward_weekly_target") is False
        or contribution.get("value") == 0
        for contribution in contributions
    )
    if not non_counting:
        return None
    title = str(activity.get("title", "")).lower()
    goal_tags = {str(tag).lower() for tag in activity.get("goal_tags", [])}
    if "fasting_prep" in goal_tags or "fasting prep block" in title:
        return (
            "Skipped because fasting preparation is a passive lab dependency, "
            "not a standalone member calendar activity."
        )
    if activity.get("facilitator_type") == "chef" and not activity.get("dependencies"):
        return (
            "Skipped because chef prep is provider work and should be represented "
            "as meal preparation context, not as a member calendar activity."
        )
    if not activity.get("dependencies") and any(
        term in title for term in ["movement prep", "activation", "warm-up", "warmup"]
    ):
        return (
            "Skipped because prep or activation support must be linked to a "
            "concrete scheduled activity instead of appearing as a standalone task."
        )
    if task.is_substitution and not activity.get("dependencies"):
        return (
            "Skipped because this non-counting support substitution is not linked "
            "to a concrete scheduled activity."
        )
    return None


def place_task(
    task: TaskInstance,
    activity: dict[str, Any],
    availability: AvailabilityData,
    scheduled_tasks: list[ScheduledTask],
    travel_time_rules: list[Any] | None = None,
    source_artifact_paths: list[str] | None = None,
) -> DecisionTrace:
    rejected_candidates: list[dict[str, Any]] = []
    last_checks: list[ConstraintCheck] = []
    trace_id = f"trace_{task.task_instance_id}"

    for slot in candidate_slots(task, activity, availability):
        start = slot["start"]
        end = slot["end"]
        dependency_state = {
            "availability": availability,
            "travel_time_rules": travel_time_rules or [],
        }
        policy_passed, policy_checks = evaluate_policy(
            task,
            start,
            end,
            scheduled_tasks,
            activity,
            dependency_state,
            candidate_location_id=slot.get("location_id"),
        )
        resource_passed, resource_checks = check_required_resources(
            task, start, end, availability, slot.get("location_id")
        )
        checks = [*policy_checks, *resource_checks]
        last_checks = checks

        if policy_passed and resource_passed:
            return DecisionTrace(
                trace_id=trace_id,
                task_instance_id=task.task_instance_id,
                activity_id=task.activity_id,
                final_status="scheduled",
                selected_slot={
                    "start": start,
                    "end": end,
                    "location_id": slot.get("location_id"),
                },
                policy_fit_summary="All policy checks passed.",
                resource_fit_summary="Required resources are available.",
                constraint_checks=checks,
                rejected_candidates=rejected_candidates,
                substitution_reason=substitution_reason_summary(task, activity),
                dependency_checks=[
                    check.model_dump()
                    for check in policy_checks
                    if check.name.startswith("dependency:")
                    or check.name == "dependencies_acknowledged"
                ],
                provider_handoff_summary=provider_handoff_summary(activity),
                source_artifact_paths=source_artifact_paths or [],
            )

        rejected_candidates.append(
            {
                "start": start.isoformat(),
                "end": end.isoformat(),
                "location_id": slot.get("location_id"),
                "reasons": [check.reason for check in checks if not check.passed],
            }
        )

    return DecisionTrace(
        trace_id=trace_id,
        task_instance_id=task.task_instance_id,
        activity_id=task.activity_id,
        final_status="unscheduled",
        selected_slot=None,
        policy_fit_summary="No candidate satisfied all policy checks.",
        resource_fit_summary="No candidate satisfied all resource checks.",
        constraint_checks=last_checks,
        rejected_candidates=rejected_candidates,
        substitution_reason=substitution_reason_summary(task, activity),
        dependency_checks=[
            check.model_dump()
            for check in last_checks
            if check.name.startswith("dependency:")
            or check.name == "dependencies_acknowledged"
        ],
        provider_handoff_summary=provider_handoff_summary(activity),
        source_artifact_paths=source_artifact_paths or [],
    )


def calendar_row(
    task: TaskInstance, activity: dict[str, Any], scheduled: ScheduledTask, trace_id: str
) -> CalendarRow:
    activity_type = calendar_activity_type(activity)
    return CalendarRow(
        calendar_row_id=f"row_{task.task_instance_id}",
        date=scheduled.start.date(),
        start_time=scheduled.start.strftime("%H:%M"),
        end_time=scheduled.end.strftime("%H:%M"),
        title=activity.get("title", task.activity_id),
        activity_type=activity_type,
        goal_tags=task.goal_tags,
        load_level=activity.get("load_level", "unknown"),
        location_id=scheduled.location_id,
        mode=calendar_delivery_mode(activity, scheduled),
        substitution_status="substitution" if task.is_substitution else "primary",
        trace_id=trace_id,
        compact_group_key=f"{scheduled.start.date().isoformat()}:{activity_type}",
        original_target_date=task.target_date
        if task.target_date and task.target_date != scheduled.start.date()
        else None,
    )


def calendar_delivery_mode(activity: dict[str, Any], scheduled: ScheduledTask) -> str:
    if activity.get("activity_type") == "medication":
        return "in_person"
    provider_ids = scheduled.provider_ids or activity.get("required_provider_ids") or []
    if scheduled.location_id == "remote" and provider_ids:
        return "remote"
    if (
        scheduled.location_id == "travel_hotel"
        and activity.get("activity_type") == "consultation"
        and activity.get("remote_allowed")
        and provider_ids
    ):
        return "remote"
    return "in_person"


def substitution_reason_summary(task: TaskInstance, activity: dict[str, Any]) -> str | None:
    if not task.is_substitution:
        return None

    codes = activity.get("substitution_reason_codes") or []
    if isinstance(codes, str):
        codes = [codes]
    notes = activity.get("substitution_notes") or activity.get("substitution_reason")
    primary_id = activity.get("substitution_for_activity_id")

    parts = []
    if primary_id:
        parts.append(f"replaces {primary_id}")
    if codes:
        readable_codes = ", ".join(str(code).replace("_", " ") for code in codes)
        parts.append(f"reason: {readable_codes}")
    if notes:
        parts.append(str(notes))
    if not parts:
        return "Substitution used because it is an alternate activity in the same family."
    return "Substitution used: " + "; ".join(parts) + "."


def calendar_activity_type(activity: dict[str, Any]) -> str:
    activity_type = activity.get("activity_type", "consultation")
    title = str(activity.get("title", "")).lower()
    facilitator_type = str(activity.get("facilitator_type", "")).lower()
    if (
        activity_type == "therapy"
        and facilitator_type == "member"
        and any(term in title for term in ["mobility", "stretch", "activation"])
    ):
        return "fitness"
    return activity_type
