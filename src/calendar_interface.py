from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from typing import Any


WEEK_DAYS = 7
DISPLAY_START_HOUR = 6
DISPLAY_END_HOUR = 22
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
    return round(decimal_hour(end_time) - decimal_hour(start_time), 2)


def monday_start(value: date) -> date:
    return value - timedelta(days=value.weekday())


def build_calendar_interface(
    calendar_rows: list[dict[str, Any]],
    availability: dict[str, Any],
    traces: list[dict[str, Any]],
    rejection_summary: dict[str, Any],
    personalized_plan: dict[str, Any] | None = None,
    resource_universe: dict[str, Any] | None = None,
) -> dict[str, Any]:
    traces_by_id = {trace["trace_id"]: trace for trace in traces}
    plan_tasks = tasks_by_id(personalized_plan)
    providers = providers_by_id(resource_universe)
    travel_windows = member_travel_windows(availability)
    rows_by_week: dict[date, list[dict[str, Any]]] = defaultdict(list)
    for row in calendar_rows:
        row_date = date.fromisoformat(row["date"])
        rows_by_week[monday_start(row_date)].append(row)

    blocked_by_week: dict[date, list[dict[str, Any]]] = defaultdict(list)
    for block in availability.get("availability_blocks", []):
        if block.get("resource_type") != "member_blocked":
            continue
        block_start = datetime.fromisoformat(block["start"])
        blocked_by_week[monday_start(block_start.date())].append(block)

    context_by_week = context_blocks_by_week(availability)
    scenario_counts: Counter[str] = Counter()
    weeks = []
    for week_start in sorted(set(rows_by_week) | set(blocked_by_week) | set(context_by_week)):
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
            )
            for row in sorted(
                rows_by_week.get(week_start, []),
                key=lambda item: (item["date"], item["start_time"], item["title"]),
            )
        ]
        for activity in activities:
            scenario_counts.update(activity["scenario_flags"])

        weeks.append(
            {
                "week_id": iso_week_id(week_start),
                "start_date": week_start.isoformat(),
                "end_date": (week_start + timedelta(days=6)).isoformat(),
                "label": week_label(week_start),
                "days": week_days(week_start),
                "activities": activities,
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
        "goal_coverage": goal_coverage(calendar_rows, traces, personalized_plan),
        "unscheduled_items": unscheduled_items(
            traces, rejection_summary, personalized_plan
        ),
        "data_quality_warnings": data_quality_warnings(calendar_rows, availability),
        "weeks": weeks,
        "rejection_summary": rejection_summary,
    }


def activity_view(
    row: dict[str, Any],
    week_start: date,
    trace: dict[str, Any] | None,
    travel_windows: list[tuple[date, date]],
    plan_tasks: dict[str, dict[str, Any]] | None = None,
    providers: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    row_date = date.fromisoformat(row["date"])
    flags = scenario_flags(row, trace, travel_windows)
    task = (plan_tasks or {}).get(task_id_from_row(row) or "")
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
        "badges": badges_for(row, flags),
        "scenario_flags": flags,
    }


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
                f"{provider.get('display_name', provider_id)}, "
                f"{provider.get('provider_type', 'provider')}"
            )
        else:
            labels.append(provider_id)
    return "; ".join(labels) if labels else None


def display_title(raw_title: str) -> str:
    prefixes = [
        "Remote or hotel-gym substitution:",
        "No-prep fallback for",
        "Fallback:",
        "Substitution:",
    ]
    title = raw_title
    for prefix in prefixes:
        if title.startswith(prefix):
            title = title[len(prefix) :].strip()
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
) -> dict[str, list[dict[str, Any]]]:
    plan_tasks = tasks_by_id(personalized_plan)
    unscheduled_by_goal: Counter[str] = Counter()
    for trace in traces:
        if trace.get("final_status") != "unscheduled":
            continue
        task = plan_tasks.get(trace.get("task_instance_id", ""))
        for goal in task.get("goal_tags", []) if task else []:
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
    return {"week": summary, "full_plan": summary}


def unscheduled_items(
    traces: list[dict[str, Any]],
    rejection_summary: dict[str, Any],
    personalized_plan: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    plan_tasks = tasks_by_id(personalized_plan)
    items = []
    for trace in traces:
        if trace.get("final_status") != "unscheduled":
            continue
        task = plan_tasks.get(trace.get("task_instance_id", ""))
        activity_id = trace.get("activity_id")
        summary = rejection_summary.get(activity_id, {})
        items.append(
            {
                "activity_id": activity_id,
                "task_instance_id": trace.get("task_instance_id"),
                "title": activity_id,
                "goal_tags": task.get("goal_tags", []) if task else [],
                "unscheduled_count": summary.get("unscheduled_count", 1),
                "rejected_candidate_count": summary.get(
                    "rejected_candidate_count",
                    len(trace.get("rejected_candidates", [])),
                ),
                "reason_summary": trace.get("policy_fit_summary")
                or "No candidate slot passed policy and resource checks.",
                "trace_id": trace.get("trace_id"),
            }
        )
    return items


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
        if block.get("resource_type") not in {"member_blocked", "member_travel"}:
            continue
        start = datetime.fromisoformat(block["start"])
        by_week[monday_start(start.date())].append(block)
    return by_week


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
    return {
        "date": start.date().isoformat(),
        "day_index": (start.date() - week_start).days,
        "start_hour": round(start.hour + start.minute / 60, 2),
        "duration_hours": round((end - start).total_seconds() / 3600, 2),
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
