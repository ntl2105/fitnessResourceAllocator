from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
import math
import re
from typing import Any

from src.scheduler.task_instances import add_months


WEEK_DAYS = 7
DISPLAY_START_HOUR = 6
DISPLAY_END_HOUR = 22
COMPACT_HABIT_TERMS = (
    "cgm",
    "hydration",
    "electrolyte",
    "supplement",
    "medication",
    "protocol",
    "check",
    "log",
)
SCENARIOS = [
    "remote",
    "travel_adaptation",
    "substitution",
    "high_load",
    "trace_rejections",
    "travel_time_rejection",
    "blocked_time_rejection",
    "dependency",
]


def decimal_hour(value: str) -> float:
    hour_text, minute_text = value.split(":", maxsplit=1)
    return int(hour_text) + int(minute_text) / 60


def duration_hours(start_time: str, end_time: str) -> float:
    return round(duration_decimal_hours(start_time, end_time), 2)


def duration_decimal_hours(start_time: str, end_time: str) -> float:
    duration = decimal_hour(end_time) - decimal_hour(start_time)
    if duration < 0:
        duration += 24
    return duration


def monday_start(value: date) -> date:
    return value - timedelta(days=value.weekday())


def build_calendar_interface(
    calendar_rows: list[dict[str, Any]],
    availability: dict[str, Any],
    traces: list[dict[str, Any]],
    rejection_summary: dict[str, Any],
    personalized_plan: dict[str, Any] | None = None,
    resource_universe: dict[str, Any] | None = None,
    action_plan: dict[str, Any] | None = None,
    member_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    traces_by_id = {trace["trace_id"]: trace for trace in traces}
    plan_tasks = tasks_by_id(personalized_plan)
    providers = providers_by_id(resource_universe)
    travel_time_rules = (resource_universe or {}).get("travel_time_rules", [])
    travel_windows = member_travel_windows(availability)
    activity_metadata = activities_by_id(action_plan)
    activity_titles = activity_titles_by_id(calendar_rows, personalized_plan, action_plan)
    rows_by_week: dict[date, list[dict[str, Any]]] = defaultdict(list)
    for row in calendar_rows:
        row_date = date.fromisoformat(row["date"])
        rows_by_week[monday_start(row_date)].append(row)

    unscheduled_by_week: dict[date, list[dict[str, Any]]] = defaultdict(list)
    for trace in traces:
        if trace.get("final_status") != "unscheduled":
            continue
        unscheduled_by_week[
            unscheduled_week_start(trace, plan_tasks, activity_metadata)
        ].append(trace)

    blocked_by_week: dict[date, list[dict[str, Any]]] = defaultdict(list)
    for block in availability.get("availability_blocks", []):
        if block.get("resource_type") != "member_blocked":
            continue
        block_start = datetime.fromisoformat(block["start"])
        blocked_by_week[monday_start(block_start.date())].append(block)

    context_by_week = context_blocks_by_week(availability)
    scenario_counts: Counter[str] = Counter()
    weeks = []
    for week_start in sorted(
        set(rows_by_week) | set(blocked_by_week) | set(context_by_week) | set(unscheduled_by_week)
    ):
        context_blocks = sorted(
            context_by_week.get(week_start, []),
            key=lambda item: item["start"],
        )
        activities = [
            activity_view(
                row,
                week_start,
                traces_by_id.get(row.get("trace_id")),
                travel_windows,
                plan_tasks,
                providers,
                activity_metadata,
            )
            for row in sorted(
                rows_by_week.get(week_start, []),
                key=lambda item: (item["date"], item["start_time"], item["title"]),
            )
        ]
        habit_blocks = compact_habit_blocks(activities)
        visible_activities = [
            activity for activity in activities if not is_compactable_habit(activity)
        ]
        for activity in activities:
            scenario_counts.update(activity["scenario_flags"])
        annotate_travel_transitions(activities, travel_time_rules)

        week_rows = rows_by_week.get(week_start, [])
        week_unscheduled_traces = unscheduled_by_week.get(week_start, [])
        weeks.append(
            {
                "week_id": iso_week_id(week_start),
                "start_date": week_start.isoformat(),
                "end_date": (week_start + timedelta(days=6)).isoformat(),
                "label": week_label(week_start),
                "days": week_days(week_start),
                "activities": visible_activities,
                "habit_blocks": habit_blocks,
                "goal_coverage": goal_summary(
                    week_rows,
                    week_unscheduled_traces,
                    plan_tasks,
                    activity_metadata,
                    member_profile,
                ),
                "category_time": category_time_summary(
                    week_rows, plan_tasks, activity_metadata
                ),
                "unscheduled_items": unscheduled_items_from_traces(
                    week_unscheduled_traces,
                    rejection_summary,
                    plan_tasks,
                    activity_titles,
                    activity_metadata,
                ),
                "location_bands": [
                    location_band(block, week_start) for block in context_blocks
                ],
                "travel_blocks": [
                    travel_block(block, week_start)
                    for block in context_blocks
                    if block.get("resource_type") == "member_travel"
                ],
                "unavailable_blocks": [
                    unavailable_view(block, week_start)
                    for block in sorted(
                        blocked_by_week.get(week_start, []),
                        key=lambda item: item["start"],
                    )
                ],
            }
        )

    return {
        "display_hours": {"start": DISPLAY_START_HOUR, "end": DISPLAY_END_HOUR},
        "scenarios": SCENARIOS,
        "scenario_counts": {
            scenario: scenario_counts.get(scenario, 0) for scenario in SCENARIOS
        },
        "goal_coverage": goal_coverage(
            calendar_rows, traces, personalized_plan, action_plan, member_profile
        ),
        "unscheduled_items": unscheduled_items(
            traces, rejection_summary, personalized_plan, activity_titles, action_plan
        ),
        "data_quality_warnings": data_quality_warnings(calendar_rows, availability),
        "member_profile": member_profile_view(member_profile, resource_universe),
        "activity_board": activity_board(action_plan, member_profile, traces),
        "three_month_recap": three_month_recap(
            calendar_rows,
            traces,
            plan_tasks,
            activity_metadata,
            member_profile,
            availability,
            weeks,
        ),
        "weeks": weeks,
        "rejection_summary": rejection_summary,
    }


def activity_board(
    action_plan: dict[str, Any] | None,
    member_profile: dict[str, Any] | None,
    traces: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    activities = (action_plan or {}).get("activities", [])
    scheduled_by_activity: Counter[str] = Counter()
    unscheduled_by_activity: Counter[str] = Counter()
    for trace in traces:
        activity_id = trace.get("activity_id")
        if not activity_id:
            continue
        if trace.get("final_status") == "scheduled":
            scheduled_by_activity[activity_id] += 1
        elif trace.get("final_status") == "unscheduled":
            unscheduled_by_activity[activity_id] += 1

    action_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    goal_actions = normalized_goal_actions(member_profile)
    action_ids = [action["goal_action_id"] for action in goal_actions]
    for activity in activities:
        contributions = activity.get("goal_contributions", [])
        if not contributions:
            continue
        for contribution in contributions:
            action_id = goal_contribution_action_id(contribution)
            if not action_id:
                continue
            action_rows[action_id].append(
                {
                    "activity_id": activity.get("activity_id"),
                    "family_id": activity.get("activity_family_id"),
                    "title": display_title(activity.get("title", "")),
                    "activity_type": activity.get("activity_type"),
                    "details": activity.get("details") or "",
                    "is_primary": bool(activity.get("is_primary")),
                    "priority": activity.get("priority"),
                    "frequency": frequency_label(activity.get("frequency", {})),
                    "load_level": activity.get("load_level"),
                    "facilitator_type": activity.get("facilitator_type") or "",
                    "provider_ids": activity.get("required_provider_ids", []),
                    "locations": activity.get("allowed_locations", []),
                    "remote_allowed": bool(activity.get("remote_allowed")),
                    "prep_required": bool(activity.get("prep_required")),
                    "prep_source": activity.get("prep_source") or activity.get("dining_source") or "",
                    "backup_activity_ids": activity.get("substitution_activity_ids", []),
                    "skip_adjustment": skip_adjustment_label(activity.get("skip_adjustment")),
                    "metrics": activity.get("metrics_to_collect", []),
                    "counts_toward_weekly_target": contribution.get("counts_toward_weekly_target") is not False,
                    "contribution_role": contribution.get("role"),
                    "scheduled_count": scheduled_by_activity[activity.get("activity_id", "")],
                    "unscheduled_count": unscheduled_by_activity[activity.get("activity_id", "")],
                    "dependencies": [dependency.get("type", "unknown") for dependency in activity.get("dependencies", []) if isinstance(dependency, dict)],
                    "warnings": activity_review_warnings(activity),
                }
            )

    board = []
    actions = {action["goal_action_id"]: action for action in goal_actions}
    for action_id in action_ids or sorted(action_rows):
        rows = sorted(
            action_rows.get(action_id, []),
            key=lambda row: (not row["counts_toward_weekly_target"], row["priority"] or 999, row["title"]),
        )
        if not rows:
            continue
        action = actions.get(action_id, {})
        board.append(
            {
                "weekly_goal_action_id": action_id,
                "goal_action_id": action_id,
                "label": action.get("label", action_id),
                "target_per_week": action.get("target_per_week"),
                "target_units": action.get("target_units"),
                "period": action.get("period"),
                "notes": action.get("notes", ""),
                "activities": rows,
            }
        )
    return board


def skip_adjustment_label(skip_adjustment: Any) -> str:
    if isinstance(skip_adjustment, dict):
        parts = []
        for key in ("if_skipped", "next_action", "notes", "fallback"):
            value = skip_adjustment.get(key)
            if value:
                parts.append(str(value))
        if parts:
            return " ".join(parts)
        return ", ".join(f"{key}: {value}" for key, value in skip_adjustment.items())
    if skip_adjustment is False:
        return "No skip adjustment"
    if skip_adjustment:
        return str(skip_adjustment)
    return "Not specified"


def three_month_recap(
    calendar_rows: list[dict[str, Any]],
    traces: list[dict[str, Any]],
    plan_tasks: dict[str, dict[str, Any]],
    activities: dict[str, dict[str, Any]],
    member_profile: dict[str, Any] | None,
    availability: dict[str, Any],
    weeks: list[dict[str, Any]],
) -> dict[str, Any]:
    weekly_actions = normalized_goal_actions(member_profile)
    horizon = recap_horizon(member_profile, availability, weeks)
    action_rows = recap_action_rows(
        calendar_rows, traces, plan_tasks, activities, weekly_actions, horizon["week_count"]
    )
    goals = recap_goal_rows(member_profile, action_rows)
    status_counts = Counter(action["status"] for action in action_rows)
    return {
        "horizon": horizon,
        "totals": {
            "goal_count": len(goals),
            "action_count": len(action_rows),
            "on_track": status_counts["on_track"],
            "at_risk": status_counts["at_risk"],
            "missed": status_counts["missed"],
            "over_target": status_counts["over_target"],
            "support_only": status_counts["support_only"],
        },
        "goals": goals,
    }


def recap_horizon(
    member_profile: dict[str, Any] | None,
    availability: dict[str, Any],
    weeks: list[dict[str, Any]],
) -> dict[str, Any]:
    rules = (member_profile or {}).get("scheduling_rules", {})
    start_text = (
        rules.get("planning_start_date")
        or availability.get("planning_start_date")
        or (weeks[0]["start_date"] if weeks else None)
    )
    months = int(rules.get("planning_months") or availability.get("planning_months") or 0)
    if start_text and months:
        start = date.fromisoformat(start_text)
        end = add_months(start, months)
        week_count = max(1, math.ceil((end - start).days / 7))
        return {
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "month_count": months,
            "week_count": week_count,
            "label": f"{months} months · {week_count} weeks",
        }
    if weeks:
        return {
            "start_date": weeks[0]["start_date"],
            "end_date": weeks[-1]["end_date"],
            "month_count": None,
            "week_count": len(weeks),
            "label": f"{len(weeks)} scheduled weeks",
        }
    return {
        "start_date": None,
        "end_date": None,
        "month_count": None,
        "week_count": 0,
        "label": "No planning horizon",
    }


def recap_action_rows(
    calendar_rows: list[dict[str, Any]],
    traces: list[dict[str, Any]],
    plan_tasks: dict[str, dict[str, Any]],
    activities: dict[str, dict[str, Any]],
    weekly_actions: list[dict[str, Any]],
    horizon_weeks: int,
) -> list[dict[str, Any]]:
    actions = ensure_normalized_goal_actions(weekly_actions)
    support_only_action_ids = {
        action["goal_action_id"]
        for action in actions
        if action.get("support_only")
    }
    scheduled_by_action: Counter[str] = Counter()
    substitutions_by_action: Counter[str] = Counter()
    support_scheduled_by_action: Counter[str] = Counter()
    blocked_by_action: Counter[str] = Counter()
    support_blocked_by_action: Counter[str] = Counter()
    weeks_by_action: dict[str, set[date]] = defaultdict(set)
    activity_titles_by_action: dict[str, Counter[str]] = defaultdict(Counter)

    for row in calendar_rows:
        activity = activity_for_calendar_row(row, plan_tasks, activities)
        row_week = monday_start(date.fromisoformat(row["date"]))
        title = display_title(row.get("title", activity.get("title", "Activity")))
        for contribution in activity.get("goal_contributions", []):
            action_id = goal_contribution_action_id(contribution)
            if not action_id:
                continue
            if (
                action_id in support_only_action_ids
                or contribution.get("counts_toward_weekly_target") is False
            ):
                support_scheduled_by_action[action_id] += 1
                if row.get("substitution_status") == "substitution":
                    substitutions_by_action[action_id] += 1
                continue
            value = contribution_value(contribution)
            scheduled_by_action[action_id] += value
            weeks_by_action[action_id].add(row_week)
            activity_titles_by_action[action_id][title] += 1
            if row.get("substitution_status") == "substitution":
                substitutions_by_action[action_id] += value

    for trace in traces:
        if trace.get("final_status") != "unscheduled":
            continue
        activity = activity_for_trace(trace, plan_tasks, activities)
        for contribution in activity.get("goal_contributions", []):
            action_id = goal_contribution_action_id(contribution)
            if not action_id:
                continue
            if (
                action_id in support_only_action_ids
                or contribution.get("counts_toward_weekly_target") is False
            ):
                support_blocked_by_action[action_id] += 1
                continue
            blocked_by_action[action_id] += contribution_value(contribution)

    rows = []
    for action in actions:
        action_id = action["goal_action_id"]
        support_only = bool(action.get("support_only"))
        period = action.get("period", "weekly")
        target_units = float(action.get("target_units") or 0)
        target_per_week = target_units if period == "weekly" else None
        horizon_target = (
            0
            if support_only
            else target_units * horizon_weeks
            if period == "weekly"
            else target_units
        )
        scheduled_total = scheduled_by_action[action_id]
        scheduled_capped = (
            scheduled_total
            if support_only or horizon_target <= 0
            else min(scheduled_total, horizon_target)
        )
        remaining = (
            0
            if support_only or horizon_target <= 0
            else max(horizon_target - scheduled_capped, 0)
        )
        extra = (
            0
            if support_only or horizon_target <= 0
            else max(scheduled_total - horizon_target, 0)
        )
        completion_percent = (
            None
            if support_only or horizon_target <= 0
            else round((scheduled_capped / horizon_target) * 100)
        )
        rows.append(
            {
                "weekly_goal_action_id": action_id,
                "goal_action_id": action_id,
                "goal_id": action.get("goal_id"),
                "label": action.get("label", action_id),
                "role": action.get("role"),
                "notes": action.get("notes", ""),
                "support_only": support_only,
                "period": period,
                "target_units": number_for_display(target_units),
                "target_per_week": number_for_display(target_per_week)
                if target_per_week is not None
                else None,
                "horizon_target": number_for_display(horizon_target),
                "scheduled": number_for_display(scheduled_capped),
                "scheduled_total": number_for_display(scheduled_total),
                "remaining": number_for_display(remaining),
                "blocked_instances": number_for_display(blocked_by_action[action_id]),
                "substitutions": number_for_display(substitutions_by_action[action_id]),
                "extra_scheduled": number_for_display(extra),
                "support_scheduled": support_scheduled_by_action[action_id],
                "support_blocked": support_blocked_by_action[action_id],
                "weeks_with_coverage": len(weeks_by_action[action_id]),
                "completion_percent": completion_percent,
                "status": recap_action_status(
                    scheduled_total,
                    remaining,
                    extra,
                    horizon_target,
                    support_only,
                    support_scheduled_by_action[action_id],
                    support_blocked_by_action[action_id],
                ),
                "top_activities": [
                    {"title": title, "count": count}
                    for title, count in activity_titles_by_action[action_id].most_common(3)
                ],
            }
        )
    return rows


def recap_action_status(
    scheduled_total: int | float,
    remaining: int | float,
    extra: int | float,
    horizon_target: int | float,
    support_only: bool,
    support_scheduled: int,
    support_blocked: int,
) -> str:
    if support_only:
        return "support_only" if support_scheduled or support_blocked else "no_activity"
    if horizon_target <= 0:
        return "no_activity"
    if not scheduled_total:
        return "missed"
    if remaining:
        return "at_risk"
    if extra:
        return "over_target"
    return "on_track"


def recap_goal_rows(
    member_profile: dict[str, Any] | None,
    action_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    goals_by_id = {
        goal.get("goal_id"): goal
        for goal in (member_profile or {}).get("goals", [])
        if goal.get("goal_id")
    }
    actions_by_goal: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for action in action_rows:
        actions_by_goal[action.get("goal_id") or "unmapped"].append(action)

    goals = []
    for goal_id, actions in sorted(
        actions_by_goal.items(),
        key=lambda item: (goals_by_id.get(item[0], {}).get("priority", 999), item[0]),
    ):
        goal = goals_by_id.get(goal_id, {})
        goals.append(
            {
                "goal_id": goal_id,
                "label": goal.get("name") or goal.get("label") or goal_id,
                "priority": goal.get("priority"),
                "description": goal.get("description", ""),
                "status": recap_goal_status(actions),
                "actions": actions,
            }
        )
    return goals


def recap_goal_status(actions: list[dict[str, Any]]) -> str:
    statuses = {action["status"] for action in actions if not action.get("support_only")}
    if "missed" in statuses:
        return "missed"
    if "at_risk" in statuses:
        return "at_risk"
    if "over_target" in statuses:
        return "over_target"
    if "on_track" in statuses:
        return "on_track"
    return "support_only"


def category_time_summary(
    calendar_rows: list[dict[str, Any]],
    plan_tasks: dict[str, dict[str, Any]] | None = None,
    activities: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    plan_tasks = plan_tasks or {}
    activities = activities or {}
    categories = ["consultation", "fitness", "food", "medication", "therapy"]
    minutes_by_category: Counter[str] = Counter()
    counts_by_category: Counter[str] = Counter()
    for row in calendar_rows:
        category = row.get("activity_type", "unknown")
        if category not in categories:
            continue
        activity = activity_for_calendar_row(row, plan_tasks, activities)
        if is_passive_constraint_activity(activity):
            continue
        minutes_by_category[category] += minutes_between(row["start_time"], row["end_time"])
        counts_by_category[category] += 1

    total_minutes = sum(minutes_by_category.values())
    return [
        {
            "category": category,
            "minutes": minutes_by_category[category],
            "hours": round(minutes_by_category[category] / 60, 2),
            "activity_count": counts_by_category[category],
            "percent": round((minutes_by_category[category] / total_minutes) * 100, 1)
            if total_minutes
            else 0,
        }
        for category in categories
    ]


def is_passive_constraint_activity(activity: dict[str, Any]) -> bool:
    goal_tags = {str(tag).lower() for tag in activity.get("goal_tags", [])}
    title = str(activity.get("title", "")).lower()
    return "fasting_prep" in goal_tags or "fasting prep block" in title


def minutes_between(start_time: str, end_time: str) -> int:
    return int(round(duration_decimal_hours(start_time, end_time) * 60))


def frequency_label(frequency: dict[str, Any]) -> str:
    frequency_type = frequency.get("type", "once")
    count = frequency.get("count")
    if frequency_type in {"daily", "weekly", "monthly"} and count:
        return f"{count}x {frequency_type}"
    if frequency.get("target_date"):
        return f"once on {frequency['target_date']}"
    return frequency_type


def activity_review_warnings(activity: dict[str, Any]) -> list[str]:
    warnings = []
    title = activity.get("title", "").lower()
    if "before/after" in title and not activity.get("dependencies"):
        warnings.append("Title implies a nearby core session, but no dependency is declared.")
    if (
        activity.get("activity_type") == "food"
        and activity.get("meal_slot")
        and "provider_chef_01" in activity.get("required_provider_ids", [])
    ):
        warnings.append("Meal requires chef during eating window; chef should usually be prep dependency only.")
    if activity.get("activity_type") == "consultation" and not activity.get("required_provider_ids"):
        warnings.append("Consultation has no provider requirement.")
    return warnings


def member_profile_view(
    member_profile: dict[str, Any] | None,
    resource_universe: dict[str, Any] | None = None,
) -> dict[str, Any]:
    profile = member_profile or {}
    return {
        "identity": {
            "name": profile.get("name", "Member"),
            "member_id": profile.get("member_id", "n/a"),
            "summary": profile.get("profile_summary")
            or (
                f"{profile.get('name', 'The member')} is a "
                f"{profile.get('occupation', 'member')} with a travel-aware plan."
            ),
            "occupation": profile.get("occupation", "n/a"),
            "timezone": profile.get("timezone", "n/a"),
        },
        "stats": [
            {"label": "Age", "value": profile.get("age_range", "n/a")},
            {"label": "Timezone", "value": profile.get("timezone", "n/a")},
            {
                "label": "Planning",
                "value": planning_horizon_label(profile.get("scheduling_rules", {})),
            },
        ],
        "goals": [goal_view(goal, index) for index, goal in enumerate(profile.get("goals", []), start=1)],
        "preferences": preference_views(profile.get("preferences", {})),
        "dietary_access": dietary_access_views(profile.get("dietary_access_plan", {})),
        "constraints": constraint_views(profile.get("constraints", {})),
        "baseline": baseline_views(profile.get("baseline_metrics", {})),
        "journey_phases": [
            {
                "id": phase.get("phase_id", "phase"),
                "label": phase.get("phase_type", "phase"),
                "date_range": f"{phase.get('start_date', 'n/a')} to {phase.get('end_date', 'n/a')}",
                "goals": phase.get("primary_goals", []),
                "biases": phase.get("scheduling_biases", []),
            }
            for phase in profile.get("journey_phases", [])
        ],
        "travel_windows": [
            {
                "id": window.get("travel_window_id", "travel"),
                "destination": window.get("destination", "n/a"),
                "date_range": f"{window.get('start', window.get('start_date', 'n/a'))} to {window.get('end', window.get('end_date', 'n/a'))}",
                "type": window.get("travel_type", "planned" if window.get("planned") else "last-minute"),
                "notes": window.get("notes") or window.get("resource_notes", ""),
            }
            for window in profile.get("travel_windows", [])
        ],
        "provider_universe": provider_universe_views(resource_universe),
        "scheduling_rules": scheduling_rule_views(profile.get("scheduling_rules", {})),
    }


def provider_universe_views(resource_universe: dict[str, Any] | None) -> list[dict[str, Any]]:
    providers = (resource_universe or {}).get("providers", [])
    return [
        {
            "provider_id": provider.get("provider_id", "provider"),
            "name": provider_display_name(provider.get("display_name", provider.get("provider_id", "Provider"))),
            "type": provider.get("provider_type", "provider"),
            "modes": provider.get("modalities_supported", []),
            "locations": provider.get("location_ids", []),
            "remote_supported": bool(provider.get("remote_supported")),
            "travel_compatible": bool(provider.get("travel_compatible")),
            "care_context": provider.get("care_context_supported", []),
            "notes": provider.get("notes", ""),
        }
        for provider in providers
    ]


def planning_horizon_label(rules: dict[str, Any]) -> str:
    start = rules.get("planning_start_date", "n/a")
    months = rules.get("planning_months", "n/a")
    return f"{start} for {months} months"


def goal_view(goal: dict[str, Any], fallback_priority: int) -> dict[str, Any]:
    target = goal.get("weekly_target", {})
    target_label = ""
    if target:
        target_label = (
            f"minimum {target.get('minimum', 'n/a')}, "
            f"preferred {target.get('preferred', 'n/a')} "
            f"{target.get('unit', 'actions')}"
        )
    return {
        "id": goal.get("goal_id", f"goal_{fallback_priority}"),
        "priority": goal.get("priority", fallback_priority),
        "label": goal.get("name") or goal.get("label") or goal.get("goal_id", "Goal"),
        "description": goal.get("description") or target.get("notes", ""),
        "target": target_label,
    }


def preference_views(preferences: dict[str, Any]) -> list[dict[str, str]]:
    exercise = preferences.get("exercise_timing", {})
    preferred = exercise.get("preferred")
    if preferred is None and preferences.get("exercise_time"):
        preferred = [preferences["exercise_time"]]
    views = [
        {"label": "Exercise timing", "value": join_display(preferred or [])},
        {
            "label": "Training",
            "value": join_display(preferences.get("training_preferences", [])),
        },
        {
            "label": "Nutrition",
            "value": join_display(
                preferences.get("nutrition_preferences")
                or preferences.get("food_preferences", [])
            ),
        },
    ]
    return [view for view in views if view["value"] != "none"]


def dietary_access_views(plan: dict[str, Any]) -> list[dict[str, str]]:
    if not plan:
        return []
    views = [
        {
            "label": "Home chef",
            "value": "available" if plan.get("home_chef_access") else "not available",
        },
        {
            "label": "Office meals",
            "value": str(plan.get("office_meal_access", "n/a")),
        },
        {
            "label": "Chef capacity",
            "value": f"{plan.get('chef_capacity_per_week', 'n/a')} support sessions/week",
        },
        {
            "label": "Member assembly",
            "value": f"{plan.get('member_assembly_limit_per_week', 'n/a')} meals/week max",
        },
        {
            "label": "Dining out",
            "value": f"{plan.get('dining_out_allowance_per_week', 'n/a')} structured meals/week",
        },
        {
            "label": "Explicit meals",
            "value": join_display(plan.get("explicit_meal_scheduling", [])),
        },
    ]
    if plan.get("normal_week_strategy"):
        views.append({"label": "Normal week", "value": mapping_display(plan["normal_week_strategy"])})
    if plan.get("travel_meal_strategy"):
        views.append({"label": "Travel", "value": mapping_display(plan["travel_meal_strategy"])})
    return [view for view in views if view["value"] != "n/a"]


def constraint_views(constraints: dict[str, Any]) -> list[dict[str, str]]:
    views = []
    for item in constraints.get("physical", []):
        views.append(
            {
                "label": item.get("name", "Physical constraint"),
                "value": join_display(item.get("implications", []))
                if item.get("implications")
                else item.get("description", ""),
            }
        )
    for key in ("schedule", "behavioral", "medical_safety"):
        if constraints.get(key):
            views.append(
                {
                    "label": key.replace("_", " ").title(),
                    "value": join_display(constraints[key]),
                }
            )
    for key, value in constraints.items():
        if key in {"physical", "schedule", "behavioral", "medical_safety"}:
            continue
        if isinstance(value, dict):
            views.append({"label": key.replace("_", " ").title(), "value": mapping_display(value)})
    return views


def baseline_views(metrics: dict[str, Any]) -> list[dict[str, str]]:
    views = []
    body = metrics.get("body_composition", {})
    if body:
        views.append(
            {
                "label": "Body composition",
                "value": ", ".join(
                    f"{key.replace('_', ' ')} {value}" for key, value in body.items()
                ),
            }
        )
    sleep = metrics.get("sleep", {})
    if sleep:
        views.append(
            {
                "label": "Sleep",
                "value": mapping_display(sleep),
            }
        )
    if metrics.get("recent_sleep_score"):
        views.append({"label": "Recent sleep", "value": str(metrics["recent_sleep_score"])})
    if metrics.get("metabolic_markers"):
        views.append({"label": "Metabolic", "value": str(metrics["metabolic_markers"])})
    return views


def scheduling_rule_views(rules: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"label": "Planning horizon", "value": planning_horizon_label(rules)},
        {
            "label": "Morning exercise",
            "value": "preferred" if rules.get("prefer_morning_exercise") else "not required",
        },
        {
            "label": "High-load guardrail",
            "value": str(
                rules.get("max_high_load_activities_per_day")
                or rules.get("max_core_sessions_per_day")
                or "n/a"
            ),
        },
    ]


def join_display(values: Any) -> str:
    if isinstance(values, list):
        return ", ".join(str(value) for value in values) if values else "none"
    if values is None:
        return "none"
    return str(values)


def mapping_display(values: dict[str, Any]) -> str:
    parts = []
    for key, value in values.items():
        label = key.replace("_", " ")
        if isinstance(value, list):
            parts.append(f"{label}: {join_display(value)}")
        elif isinstance(value, dict):
            parts.append(f"{label}: {mapping_display(value)}")
        else:
            parts.append(f"{label}: {value}")
    return "; ".join(parts)


def activity_view(
    row: dict[str, Any],
    week_start: date,
    trace: dict[str, Any] | None,
    travel_windows: list[tuple[date, date]],
    plan_tasks: dict[str, dict[str, Any]] | None = None,
    providers: dict[str, dict[str, Any]] | None = None,
    activities: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    row_date = date.fromisoformat(row["date"])
    flags = scenario_flags(row, trace, travel_windows)
    task = (plan_tasks or {}).get(task_id_from_row(row) or "")
    activity = activity_for_calendar_row(row, plan_tasks or {}, activities or {})
    title = display_title(row["title"])
    return {
        "id": row["calendar_row_id"],
        "title": title,
        "display_title": title,
        "raw_title": row["title"],
        "date": row["date"],
        "day_index": (row_date - week_start).days,
        "start_hour": decimal_hour(row["start_time"]),
        "duration_hours": duration_hours(row["start_time"], row["end_time"]),
        "start_time": row["start_time"],
        "end_time": row["end_time"],
        "activity_type": row["activity_type"],
        "goal_tags": row.get("goal_tags", []),
        "load_level": row["load_level"],
        "location_id": row.get("location_id"),
        "mode": row["mode"],
        "substitution_status": row["substitution_status"],
        "trace_id": row.get("trace_id"),
        "provider_summary": provider_summary(task, providers or {}),
        "prep_summary": compact_prep_summary(activity),
        "meal_summary": compact_meal_summary(activity),
        "travel_to": None,
        "badges": badges_for(row, flags),
        "scenario_flags": flags,
    }


def compact_habit_blocks(activities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    habits_by_day: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for activity in activities:
        if is_compactable_habit(activity):
            habits_by_day[activity["day_index"]].append(activity)

    blocks = []
    for day_index, habits in sorted(habits_by_day.items()):
        sorted_habits = sorted(habits, key=lambda item: (item["start_time"], item["title"]))
        blocks.append(
            {
                "day_index": day_index,
                "count": len(sorted_habits),
                "summary": compact_habit_summary(sorted_habits),
                "items": [
                    {
                        "time": habit["start_time"],
                        "title": compact_habit_title(habit["title"]),
                    }
                    for habit in sorted_habits
                ],
            }
        )
    return blocks


def compact_habit_summary(habits: list[dict[str, Any]]) -> str:
    items = [
        f"{habit['start_time']} {compact_habit_title(habit['title'])}"
        for habit in habits
    ]
    return "Habits: " + "; ".join(items)


def compact_habit_title(title: str) -> str:
    normalized = display_title(title)
    replacements = {
        "Morning CGM check and log": "CGM check",
        "Daily hydration and electrolyte protocol": "hydration",
        "Morning supplement protocol with breakfast": "supplements with breakfast",
        "Evening medication protocol with dinner": "medication with dinner",
    }
    return replacements.get(normalized, normalized)


def is_compactable_habit(activity: dict[str, Any]) -> bool:
    if activity.get("activity_type") != "medication":
        return False
    if activity.get("substitution_status") != "primary":
        return False
    if activity.get("load_level") not in {"low", None}:
        return False
    text = " ".join(
        [
            str(activity.get("title", "")),
            str(activity.get("raw_title", "")),
            " ".join(str(tag) for tag in activity.get("goal_tags", [])),
        ]
    ).lower()
    return any(term in text for term in COMPACT_HABIT_TERMS)


def annotate_travel_transitions(
    activities: list[dict[str, Any]], travel_time_rules: list[dict[str, Any]]
) -> None:
    by_day: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for activity in activities:
        by_day[activity["day_index"]].append(activity)

    for day_activities in by_day.values():
        sorted_day = sorted(day_activities, key=lambda item: (item["start_time"], item["end_time"]))
        previous = None
        for activity in sorted_day:
            if previous is not None:
                travel_label = travel_transition_label(previous, activity, travel_time_rules)
                if travel_label:
                    activity["travel_to"] = travel_label
            elif starts_away_from_home(activity):
                activity["travel_to"] = first_location_travel_label(activity, travel_time_rules)
            previous = activity


def starts_away_from_home(activity: dict[str, Any]) -> bool:
    location = activity.get("location_id")
    return bool(location and location not in {"home", "remote"})


def first_location_travel_label(
    activity: dict[str, Any], travel_time_rules: list[dict[str, Any]]
) -> str:
    to_location = activity["location_id"]
    minutes = travel_minutes_between(travel_time_rules, "home", to_location)
    destination = location_display(to_location)
    return f"🚇 Travel to {destination}{f' · {minutes}m' if minutes is not None else ''}"


def travel_transition_label(
    previous: dict[str, Any],
    activity: dict[str, Any],
    travel_time_rules: list[dict[str, Any]],
) -> str | None:
    from_location = previous.get("location_id")
    to_location = activity.get("location_id")
    if not from_location or not to_location or from_location == to_location:
        return None
    if "remote" in {from_location, to_location} or to_location == "home":
        return None
    minutes = travel_minutes_between(travel_time_rules, from_location, to_location)
    destination = location_display(to_location)
    return f"🚇 Travel to {destination}{f' · {minutes}m' if minutes is not None else ''}"


def travel_minutes_between(
    travel_time_rules: list[dict[str, Any]], from_location: str, to_location: str
) -> int | None:
    for rule in travel_time_rules:
        if (
            rule.get("from_location_id") == from_location
            and rule.get("to_location_id") == to_location
        ):
            return int(rule["minutes"])
    return None


def location_display(location_id: str) -> str:
    return location_id.replace("_", " ")


def task_id_from_row(row: dict[str, Any]) -> str | None:
    row_id = row.get("calendar_row_id", "")
    if row_id.startswith("row_"):
        return row_id.removeprefix("row_")
    return None


def tasks_by_id(personalized_plan: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    return {
        task["task_id"]: task
        for task in (personalized_plan or {}).get("tasks", [])
        if task.get("task_id")
    }


def providers_by_id(
    resource_universe: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    return {
        provider["provider_id"]: provider
        for provider in (resource_universe or {}).get("providers", [])
        if provider.get("provider_id")
    }


def activities_by_id(action_plan: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    return {
        activity["activity_id"]: activity
        for activity in (action_plan or {}).get("activities", [])
        if activity.get("activity_id")
    }


def normalized_goal_actions(member_profile: dict[str, Any] | None) -> list[dict[str, Any]]:
    profile = member_profile or {}
    return [
        *normalize_goal_action_items(profile.get("goal_actions", []), legacy=False),
        *normalize_goal_action_items(profile.get("weekly_goal_actions", []), legacy=True),
    ]


def normalize_goal_action_items(
    actions: list[dict[str, Any]], *, legacy: bool
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for action in actions:
        action_id = action.get("weekly_goal_action_id") if legacy else action.get("goal_action_id")
        if not action_id or action_id in seen:
            continue
        if legacy:
            normalized_action = {
                **action,
                "goal_action_id": action_id,
                "weekly_goal_action_id": action_id,
                "period": "weekly",
                "target_units": action.get("target_per_week", 0),
                "unit_label": action.get("unit_label") or "activities",
            }
        else:
            target = action.get("target", {}) or {}
            period = target.get("period", "weekly")
            normalized_action = {
                **action,
                "goal_action_id": action_id,
                "period": period,
                "target_units": target.get("units", 0),
                "unit_label": target.get("unit_label"),
                "weekly_goal_action_id": action.get("weekly_goal_action_id", action_id),
                "target_per_week": target.get("units") if period == "weekly" else None,
            }
        normalized.append(normalized_action)
        seen.add(action_id)

    return normalized


def ensure_normalized_goal_actions(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if all(
        "goal_action_id" in action and "period" in action and "target_units" in action
        for action in actions
    ):
        return actions
    if any("goal_action_id" in action for action in actions):
        return normalize_goal_action_items(actions, legacy=False)
    return normalize_goal_action_items(actions, legacy=True)


def goal_contribution_action_id(contribution: dict[str, Any]) -> str | None:
    return contribution.get("goal_action_id") or contribution.get("weekly_goal_action_id")


def provider_summary(
    task: dict[str, Any] | None, providers: dict[str, dict[str, Any]]
) -> str | None:
    if not task:
        return None
    labels = []
    for provider_id in task.get("provider_ids", []):
        provider = providers.get(provider_id)
        if provider:
            labels.append(
                f"{provider_display_name(provider.get('display_name', provider_id))}, "
                f"{provider.get('provider_type', 'provider')}"
            )
        else:
            labels.append(provider_id)
    return "; ".join(labels) if labels else None


def provider_display_name(display_name: str) -> str:
    if display_name == "Remote travel trainer pool":
        return "Remote trainer pool"
    return display_name


def prep_summary(activity: dict[str, Any]) -> str | None:
    if activity.get("activity_type") != "food":
        return None
    for dependency in activity.get("dependencies", []):
        if not isinstance(dependency, dict) or dependency.get("type") != "prep_task":
            continue
        duration = dependency.get("prep_duration_minutes")
        offset = dependency.get("offset_minutes_min")
        actor = prep_actor_label(dependency)
        timing = []
        if duration:
            timing.append(f"{duration}m prep")
        if offset:
            timing.append(f"{offset}m before")
        return f"Prep: {actor}{' · ' + ' · '.join(timing) if timing else ''}"
    if activity.get("prep_required"):
        return "Prep required"
    source = activity.get("prep_source") or activity.get("dining_source")
    if source:
        return f"Source: {display_token(source)}"
    return None


def compact_prep_summary(activity: dict[str, Any]) -> str | None:
    if activity.get("activity_type") == "food":
        return None
    return prep_summary(activity)


def meal_summary(activity: dict[str, Any]) -> str | None:
    if activity.get("activity_type") != "food":
        return None
    parts = []
    if activity.get("meal_slot"):
        parts.append(display_token(activity["meal_slot"]))
    metrics = activity.get("metrics_to_collect", [])
    useful_metrics = [
        display_token(metric)
        for metric in metrics
        if metric in {"protein_servings", "post_meal_energy", "meal_completion"}
    ]
    if useful_metrics:
        parts.append("tracks " + ", ".join(useful_metrics[:2]))
    for contribution in activity.get("goal_contributions", []):
        if contribution.get("counts_toward_weekly_target") is not False:
            parts.append("counts to meal target")
            break
    return " · ".join(parts) if parts else None


def compact_meal_summary(activity: dict[str, Any]) -> str | None:
    return None


def display_token(value: Any) -> str:
    return str(value).replace("_", " ")


def prep_actor_label(dependency: dict[str, Any]) -> str:
    provider_type = dependency.get("provider_type")
    member = bool(dependency.get("can_be_done_by_member"))
    provider = bool(dependency.get("can_be_done_by_provider"))
    if provider_type and member and provider:
        return f"{provider_type} or member"
    if provider_type and provider:
        return str(provider_type)
    if member:
        return "member"
    return "provider"


def display_title(raw_title: str) -> str:
    title_overrides = {
        "High-protein breakfast (chef-prepped or assembled at home)": "High-protein breakfast",
        "Structured metabolic lunch (chef-prepped or member-assembled)": "Structured lunch",
        "Chef-prepped recovery dinner (home or office)": "Recovery dinner",
        "Travel-compatible breakfast (restaurant or hotel buffet)": "Travel breakfast",
        "Travel-compatible lunch (restaurant or hotel meal)": "Travel lunch",
        "Travel-compatible dinner (restaurant or hotel meal)": "Travel dinner",
        "Fasting blood panel at clinic or lab": "Fasting blood panel",
        "Physician review of lab results": "Physician lab review",
        "Dietitian review of nutrition and lab results": "Dietitian nutrition review",
        "Physiotherapist reassessment after travel or pain escalation": "Physio reassessment",
        "Trainer care-plan handoff review": "Trainer handoff",
        "Remote trainer check-in before/after aerobic session": "Aerobic readiness check-in",
        "Remote coach check-in before/after aerobic session": "Aerobic readiness check-in",
    }
    if raw_title in title_overrides:
        return title_overrides[raw_title]

    prefixes = [
        "Remote or hotel-gym substitution:",
        "No-prep fallback for",
        "Remote fallback:",
        "Fallback:",
        "Substitution:",
    ]
    title = raw_title
    for prefix in prefixes:
        if title.startswith(prefix):
            title = title[len(prefix) :].strip()
    title = title.replace("chef-prepped or member-assembled", "structured")
    title = title.replace("chef-prepped or assembled at home", "structured")
    title = re.sub(r"\s*\([^)]*\)", "", title).strip()
    return title[:1].upper() + title[1:] if title else raw_title


def goal_status(scheduled: int, unscheduled: int, substitutions: int) -> str:
    if unscheduled and not scheduled:
        return "missed"
    if unscheduled or substitutions:
        return "at_risk"
    return "on_track" if scheduled else "no_activity"


def goal_coverage(
    calendar_rows: list[dict[str, Any]],
    traces: list[dict[str, Any]],
    personalized_plan: dict[str, Any] | None,
    action_plan: dict[str, Any] | None = None,
    member_profile: dict[str, Any] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    summary = goal_summary(
        calendar_rows,
        traces,
        tasks_by_id(personalized_plan),
        activities_by_id(action_plan),
        member_profile,
    )
    return {"week": summary, "full_plan": summary}


def goal_summary(
    calendar_rows: list[dict[str, Any]],
    traces: list[dict[str, Any]],
    plan_tasks: dict[str, dict[str, Any]],
    activities: dict[str, dict[str, Any]] | None = None,
    member_profile: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    activities = activities or {}
    weekly_goal_actions = normalized_goal_actions(member_profile)
    if weekly_goal_actions:
        return weekly_goal_action_summary(
            calendar_rows, traces, plan_tasks, activities, weekly_goal_actions
        )

    unscheduled_by_goal: Counter[str] = Counter()
    for trace in traces:
        if trace.get("final_status") != "unscheduled":
            continue
        task = plan_tasks.get(trace.get("task_instance_id", ""))
        activity = activities.get(trace.get("activity_id", ""))
        goals = task.get("goal_tags", []) if task else activity.get("goal_tags", [])
        for goal in goals:
            unscheduled_by_goal[goal] += 1

    scheduled_by_goal: Counter[str] = Counter()
    substitutions_by_goal: Counter[str] = Counter()
    for row in calendar_rows:
        for goal in row.get("goal_tags", []):
            scheduled_by_goal[goal] += 1
            if row.get("substitution_status") == "substitution":
                substitutions_by_goal[goal] += 1

    goals = sorted(set(scheduled_by_goal) | set(unscheduled_by_goal))
    summary = [
        {
            "goal_tag": goal,
            "scheduled": scheduled_by_goal[goal],
            "unscheduled": unscheduled_by_goal[goal],
            "substitutions": substitutions_by_goal[goal],
            "status": goal_status(
                scheduled_by_goal[goal],
                unscheduled_by_goal[goal],
                substitutions_by_goal[goal],
            ),
        }
        for goal in goals
    ]
    return summary


def weekly_goal_action_summary(
    calendar_rows: list[dict[str, Any]],
    traces: list[dict[str, Any]],
    plan_tasks: dict[str, dict[str, Any]],
    activities: dict[str, dict[str, Any]],
    weekly_goal_actions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    actions = ensure_normalized_goal_actions(weekly_goal_actions)
    support_only_action_ids = {
        action["goal_action_id"]
        for action in actions
        if action.get("support_only")
    }
    scheduled_by_action: Counter[str] = Counter()
    unscheduled_by_action: Counter[str] = Counter()
    substitutions_by_action: Counter[str] = Counter()
    support_scheduled_by_action: Counter[str] = Counter()
    support_unscheduled_by_action: Counter[str] = Counter()

    for row in calendar_rows:
        activity = activity_for_calendar_row(row, plan_tasks, activities)
        for contribution in activity.get("goal_contributions", []):
            action_id = goal_contribution_action_id(contribution)
            if not action_id:
                continue
            if (
                action_id in support_only_action_ids
                or contribution.get("counts_toward_weekly_target") is False
            ):
                support_scheduled_by_action[action_id] += 1
                continue
            scheduled_by_action[action_id] += contribution_value(contribution)
            if row.get("substitution_status") == "substitution":
                substitutions_by_action[action_id] += contribution_value(contribution)

    for trace in traces:
        if trace.get("final_status") != "unscheduled":
            continue
        activity = activity_for_trace(trace, plan_tasks, activities)
        for contribution in activity.get("goal_contributions", []):
            action_id = goal_contribution_action_id(contribution)
            if not action_id:
                continue
            if (
                action_id in support_only_action_ids
                or contribution.get("counts_toward_weekly_target") is False
            ):
                support_unscheduled_by_action[action_id] += 1
                continue
            unscheduled_by_action[action_id] += contribution_value(contribution)

    summary = []
    for action in actions:
        action_id = action["goal_action_id"]
        scheduled_total = scheduled_by_action[action_id]
        raw_unscheduled = number_for_display(unscheduled_by_action[action_id])
        substitutions = number_for_display(substitutions_by_action[action_id])
        support_scheduled = support_scheduled_by_action[action_id]
        support_unscheduled = support_unscheduled_by_action[action_id]
        support_only = bool(action.get("support_only"))

        if support_only and not (support_scheduled or support_unscheduled):
            continue

        target = action.get("target_per_week", action.get("target_units", 0))
        target_value = float(target or 0)
        scheduled_toward_target = (
            scheduled_total if support_only or target_value <= 0 else min(scheduled_total, target_value)
        )
        target_gap = (
            0
            if support_only or target_value <= 0
            else max(target_value - scheduled_toward_target, 0)
        )
        extra_scheduled = (
            0 if support_only or target_value <= 0 else max(scheduled_total - target_value, 0)
        )
        summary.append(
            {
                "goal_tag": action.get("goal_id", action_id),
                "goal_id": action.get("goal_id"),
                "weekly_goal_action_id": action_id,
                "goal_action_id": action_id,
                "label": action.get("label", action_id),
                "role": action.get("role"),
                "support_only": support_only,
                "target_per_week": target,
                "scheduled": number_for_display(scheduled_toward_target),
                "scheduled_total": number_for_display(scheduled_total),
                "extra_scheduled": number_for_display(extra_scheduled),
                "unscheduled": number_for_display(target_gap),
                "raw_unscheduled_instances": raw_unscheduled,
                "planned": number_for_display(target_value or scheduled_toward_target),
                "substitutions": substitutions,
                "support_scheduled": support_scheduled,
                "support_unscheduled": support_unscheduled,
                "status": weekly_goal_status(
                    scheduled_toward_target,
                    target_gap,
                    target_value,
                    support_only,
                    support_scheduled,
                    support_unscheduled,
                    extra_scheduled,
                ),
            }
        )
    return summary


def activity_for_calendar_row(
    row: dict[str, Any],
    plan_tasks: dict[str, dict[str, Any]],
    activities: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    task = plan_tasks.get(task_id_from_row(row) or "")
    if task:
        return activities.get(task.get("activity_id", ""), {})
    return activities.get(row.get("activity_id", ""), {})


def activity_for_trace(
    trace: dict[str, Any],
    plan_tasks: dict[str, dict[str, Any]],
    activities: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    task = plan_tasks.get(trace.get("task_instance_id", ""))
    if task:
        return activities.get(task.get("activity_id", ""), {})
    return activities.get(trace.get("activity_id", ""), {})


def contribution_value(contribution: dict[str, Any]) -> float:
    value = contribution.get("value", 1)
    if isinstance(value, (int, float)):
        return float(value)
    return 1.0


def number_for_display(value: float) -> int | float:
    return int(value) if float(value).is_integer() else round(value, 2)


def weekly_goal_status(
    scheduled: int | float,
    unscheduled: int | float,
    target: float,
    support_only: bool,
    support_scheduled: int,
    support_unscheduled: int,
    extra_scheduled: int | float = 0,
) -> str:
    if support_only:
        return "support_only" if support_scheduled or support_unscheduled else "no_activity"
    if scheduled >= target and unscheduled:
        return "target_met_with_risk"
    if scheduled >= target and extra_scheduled:
        return "covered_with_extras"
    if scheduled >= target:
        return "on_track"
    if scheduled == 0:
        return "missed"
    return "at_risk"


def unscheduled_items(
    traces: list[dict[str, Any]],
    rejection_summary: dict[str, Any],
    personalized_plan: dict[str, Any] | None,
    activity_titles: dict[str, str] | None = None,
    action_plan: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return unscheduled_items_from_traces(
        traces,
        rejection_summary,
        tasks_by_id(personalized_plan),
        activity_titles or {},
        activities_by_id(action_plan),
    )


def unscheduled_items_from_traces(
    traces: list[dict[str, Any]],
    rejection_summary: dict[str, Any],
    plan_tasks: dict[str, dict[str, Any]],
    activity_titles: dict[str, str],
    activities: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    activities = activities or {}
    items = []
    for trace in traces:
        if trace.get("final_status") != "unscheduled":
            continue
        task = plan_tasks.get(trace.get("task_instance_id", ""))
        activity_id = trace.get("activity_id")
        activity = activities.get(activity_id or "") or {}
        summary = rejection_summary.get(activity_id, {})
        items.append(
            {
                "activity_id": activity_id,
                "task_instance_id": trace.get("task_instance_id"),
                "title": item_title(activity_id, task, activity_titles),
                "goal_tags": task.get("goal_tags", [])
                if task
                else activity.get("goal_tags", []),
                "unscheduled_count": summary.get("unscheduled_count", 1),
                "rejected_candidate_count": summary.get(
                    "rejected_candidate_count",
                    len(trace.get("rejected_candidates", [])),
                ),
                "reason_summary": unscheduled_reason_summary(trace),
                "trace_id": trace.get("trace_id"),
            }
        )
    return items


def activity_titles_by_id(
    calendar_rows: list[dict[str, Any]],
    personalized_plan: dict[str, Any] | None,
    action_plan: dict[str, Any] | None = None,
) -> dict[str, str]:
    titles = {
        row.get("activity_id"): display_title(row["title"])
        for row in calendar_rows
        if row.get("activity_id")
    }
    for task in (personalized_plan or {}).get("tasks", []):
        if task.get("activity_id") and task.get("title"):
            titles.setdefault(task["activity_id"], display_title(task["title"]))
    for activity in (action_plan or {}).get("activities", []):
        if activity.get("activity_id") and activity.get("title"):
            titles.setdefault(activity["activity_id"], display_title(activity["title"]))
    return titles


def item_title(
    activity_id: str | None,
    task: dict[str, Any] | None,
    activity_titles: dict[str, str],
) -> str:
    if task and task.get("title"):
        return display_title(task["title"])
    if activity_id and activity_id in activity_titles:
        return activity_titles[activity_id]
    return activity_id or "Unscheduled activity"


def unscheduled_reason_summary(trace: dict[str, Any]) -> str:
    reason_text = " ".join(
        reason
        for candidate in trace.get("rejected_candidates", [])
        for reason in candidate.get("reasons", [])
    )
    if "physical location clinic" in reason_text:
        return "No clinic availability for this candidate slot."
    if "physical location lab" in reason_text:
        return "No lab availability for this candidate slot."
    if "No availability block covers candidate slot" in reason_text:
        return "Required provider or resource was unavailable for candidate slots."
    if "member travel" in reason_text.lower():
        return "Candidate slots conflicted with member travel constraints."
    if "overlaps" in reason_text.lower():
        return "Candidate slots overlapped existing scheduled activities."
    return (
        trace.get("policy_fit_summary")
        or "No candidate slot passed policy and resource checks."
    )


def unscheduled_week_start(
    trace: dict[str, Any],
    plan_tasks: dict[str, dict[str, Any]],
    activities: dict[str, dict[str, Any]] | None = None,
) -> date:
    task = plan_tasks.get(trace.get("task_instance_id", ""))
    for key in ("target_date", "date"):
        if task and task.get(key):
            return monday_start(date.fromisoformat(task[key]))
    activity = (activities or {}).get(trace.get("activity_id", "")) or {}
    frequency = activity.get("frequency", {})
    if frequency.get("target_date"):
        return monday_start(date.fromisoformat(frequency["target_date"]))
    for candidate in trace.get("rejected_candidates", []):
        if candidate.get("start"):
            return monday_start(datetime.fromisoformat(candidate["start"]).date())
    return date.today()


def data_quality_warnings(
    calendar_rows: list[dict[str, Any]], availability: dict[str, Any]
) -> list[str]:
    warnings = []
    food_titles = [
        row.get("title", "").lower()
        for row in calendar_rows
        if row.get("activity_type") == "food"
    ]
    clean_food_titles = [
        title
        for title in food_titles
        if "fallback" not in title and "protocol" not in title
    ]
    has_clean_meal = any(
        meal in title
        for title in clean_food_titles
        for meal in ["breakfast", "lunch", "dinner"]
    )
    has_protocol_food = any(
        "supplement" in title or "protocol" in title for title in food_titles
    )
    if has_protocol_food and not has_clean_meal:
        warnings.append(
            "Food plan has supplement/protocol rows but no explicit "
            "breakfast/lunch/dinner coverage."
        )

    raw_title_text = " ".join(row.get("title", "") for row in calendar_rows).lower()
    if "fallback" in raw_title_text or "substitution:" in raw_title_text:
        warnings.append("Raw activity titles still contain fallback/substitution wording.")

    for block in availability.get("availability_blocks", []):
        if block.get("resource_type") != "member_travel":
            continue
        start = datetime.fromisoformat(block["start"])
        end = datetime.fromisoformat(block["end"])
        if start.hour == 0 and start.minute == 0 and end.hour in {23, 0}:
            warnings.append("Travel windows should include exact travel leg times.")
            break
    return warnings


def unavailable_view(block: dict[str, Any], week_start: date) -> dict[str, Any]:
    start = datetime.fromisoformat(block["start"])
    end = datetime.fromisoformat(block["end"])
    return {
        "date": start.date().isoformat(),
        "day_index": (start.date() - week_start).days,
        "start_hour": round(start.hour + start.minute / 60, 2),
        "duration_hours": round((end - start).total_seconds() / 3600, 2),
        "label": block.get("notes") or block.get("resource_id") or "Unavailable",
        "location_id": block.get("location_id"),
    }


def context_blocks_by_week(availability: dict[str, Any]) -> dict[date, list[dict[str, Any]]]:
    by_week: dict[date, list[dict[str, Any]]] = defaultdict(list)
    for block in availability.get("availability_blocks", []):
        if block.get("resource_type") not in {"member_travel", "member_location"}:
            continue
        start = datetime.fromisoformat(block["start"])
        end = datetime.fromisoformat(block["end"])
        for week_start in overlapping_week_starts(start.date(), end.date()):
            by_week[week_start].append(block)
    return by_week


def overlapping_week_starts(start: date, end: date) -> list[date]:
    week_start = monday_start(start)
    final_week_start = monday_start(end)
    weeks = []
    while week_start <= final_week_start:
        weeks.append(week_start)
        week_start += timedelta(days=7)
    return weeks


def location_band(block: dict[str, Any], week_start: date) -> dict[str, Any]:
    start = datetime.fromisoformat(block["start"])
    end = datetime.fromisoformat(block["end"])
    return {
        "label": block.get("notes") or block.get("location_id") or "Location context",
        "location_id": block.get("location_id"),
        "resource_type": block.get("resource_type"),
        "start_day_index": max(0, (start.date() - week_start).days),
        "end_day_index": min(6, (end.date() - week_start).days),
    }


def travel_block(block: dict[str, Any], week_start: date) -> dict[str, Any]:
    start = datetime.fromisoformat(block["start"])
    end = datetime.fromisoformat(block["end"])
    week_start_dt = datetime.combine(week_start, datetime.min.time(), tzinfo=start.tzinfo)
    week_end_dt = week_start_dt + timedelta(days=7)
    clipped_start = max(start, week_start_dt)
    clipped_end = min(end, week_end_dt)
    return {
        "date": clipped_start.date().isoformat(),
        "day_index": (clipped_start.date() - week_start).days,
        "start_hour": round(clipped_start.hour + clipped_start.minute / 60, 2),
        "duration_hours": round((clipped_end - clipped_start).total_seconds() / 3600, 2),
        "label": block.get("notes") or "Travel",
        "location_id": block.get("location_id"),
    }


def scenario_flags(
    row: dict[str, Any],
    trace: dict[str, Any] | None,
    travel_windows: list[tuple[date, date]],
) -> list[str]:
    flags: set[str] = set()
    row_date = date.fromisoformat(row["date"])
    if row.get("mode") == "remote":
        flags.add("remote")
    if row.get("location_id") == "travel_hotel" or (
        row.get("mode") == "remote"
        and any(start <= row_date <= end for start, end in travel_windows)
    ):
        flags.add("travel_adaptation")
    if row.get("substitution_status") == "substitution":
        flags.add("substitution")
    if row.get("load_level") == "high":
        flags.add("high_load")
    if trace:
        if trace.get("rejected_candidates"):
            flags.add("trace_rejections")
        checks = trace.get("constraint_checks", [])
        if any(
            check.get("name") == "travel_time_buffer" and check.get("passed") is False
            for check in checks
        ):
            flags.add("travel_time_rejection")
        reason_text = " ".join(
            reason
            for candidate in trace.get("rejected_candidates", [])
            for reason in candidate.get("reasons", [])
        ).lower()
        if "requires" in reason_text and "minutes" in reason_text:
            flags.add("travel_time_rejection")
        if "member blocked" in reason_text:
            flags.add("blocked_time_rejection")
        dependency_checks = trace.get("dependency_checks", [])
        if any(
            check.get("name") != "dependencies_acknowledged"
            for check in dependency_checks
            if isinstance(check, dict)
        ):
            flags.add("dependency")
    return sorted(flags)


def badges_for(row: dict[str, Any], flags: list[str]) -> list[str]:
    badges = []
    if "remote" in flags:
        badges.append("remote")
    if row.get("location_id") == "travel_hotel":
        badges.append("travel hotel")
    if "substitution" in flags:
        badges.append("substitution")
    if "high_load" in flags:
        badges.append("high load")
    if "dependency" in flags:
        badges.append("dependency")
    if "trace_rejections" in flags:
        badges.append("rejections")
    return badges


def member_travel_windows(availability: dict[str, Any]) -> list[tuple[date, date]]:
    windows = []
    for block in availability.get("availability_blocks", []):
        if block.get("resource_type") != "member_travel":
            continue
        windows.append(
            (
                datetime.fromisoformat(block["start"]).date(),
                datetime.fromisoformat(block["end"]).date(),
            )
        )
    return windows


def week_days(week_start: date) -> list[dict[str, str]]:
    days = []
    for offset in range(WEEK_DAYS):
        current = week_start + timedelta(days=offset)
        days.append({"date": current.isoformat(), "label": day_label(current)})
    return days


def week_label(week_start: date) -> str:
    end = week_start + timedelta(days=6)
    return f"{month_day(week_start)} - {month_day(end)}, {end.year}"


def day_label(value: date) -> str:
    return f"{value.strftime('%a %b')} {value.day}"


def month_day(value: date) -> str:
    return f"{value.strftime('%b')} {value.day}"


def iso_week_id(week_start: date) -> str:
    iso = week_start.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"
