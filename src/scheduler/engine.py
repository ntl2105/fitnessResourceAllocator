from __future__ import annotations

from dataclasses import dataclass
from datetime import date
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
    source_artifact_paths: list[str] | None = None,
) -> SchedulingResult:
    plan = PersonalizedPlan(run_id=run_id, tasks=[], metadata={"scheduler": "simple_explainable"})
    rows: list[CalendarRow] = []
    traces: list[DecisionTrace] = []
    rejection_summary: dict[str, dict[str, int]] = {}
    trace_source_paths = source_artifact_paths or [
        "data/action_plan.json",
        "data/availability.json",
    ]

    for task in sort_tasks(tasks):
        activity = activities.get(task.activity_id, {})
        trace = place_task(
            task,
            activity,
            availability,
            plan.tasks,
            travel_time_rules or [],
            trace_source_paths,
        )
        traces.append(trace)

        if trace.final_status != "scheduled" or not trace.selected_slot:
            summary = rejection_summary.setdefault(
                task.activity_id,
                {"unscheduled_count": 0, "rejected_candidate_count": 0},
            )
            summary["unscheduled_count"] += 1
            summary["rejected_candidate_count"] += len(trace.rejected_candidates)
            continue

        selected = trace.selected_slot
        scheduled = ScheduledTask(
            task_id=task.task_instance_id,
            activity_id=task.activity_id,
            activity_family_id=task.activity_family_id,
            title=activity.get("title", task.activity_id),
            goal_tags=task.goal_tags,
            start=selected["start"],
            end=selected["end"],
            location_id=selected.get("location_id"),
            provider_ids=task.required_resources.get("provider_ids", []),
            equipment_ids=task.required_resources.get("equipment_ids", []),
            status="scheduled",
            trace_id=trace.trace_id,
        )
        plan.tasks.append(scheduled)
        rows.append(calendar_row(task, activity, scheduled, trace.trace_id))

    plan.metadata["scheduled_count"] = len(plan.tasks)
    plan.metadata["unscheduled_count"] = len(tasks) - len(plan.tasks)
    return SchedulingResult(plan=plan, calendar_rows=rows, traces=traces, rejection_summary=rejection_summary)


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
    return CalendarRow(
        calendar_row_id=f"row_{task.task_instance_id}",
        date=scheduled.start.date(),
        start_time=scheduled.start.strftime("%H:%M"),
        end_time=scheduled.end.strftime("%H:%M"),
        title=activity.get("title", task.activity_id),
        activity_type=activity.get("activity_type", "consultation"),
        goal_tags=task.goal_tags,
        load_level=activity.get("load_level", "unknown"),
        location_id=scheduled.location_id,
        mode="remote" if scheduled.location_id == "remote" else "in_person",
        substitution_status="substitution" if task.is_substitution else "primary",
        trace_id=trace_id,
        compact_group_key=f"{scheduled.start.date().isoformat()}:{activity.get('activity_type', 'activity')}",
    )
