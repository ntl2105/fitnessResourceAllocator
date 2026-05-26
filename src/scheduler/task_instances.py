from __future__ import annotations

from calendar import monthrange
from datetime import date, timedelta
from typing import Any

from src.models.availability import AvailabilityData
from src.models.schedule import TaskInstance


WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

WEEK_ORDINALS = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "last": -1,
}


def expand_primary_activities(
    action_plan: dict[str, Any], availability: AvailabilityData
) -> list[TaskInstance]:
    horizon_start = availability.planning_start_date
    horizon_end = add_months(horizon_start, availability.planning_months)
    tasks: list[TaskInstance] = []

    for activity in action_plan.get("activities", []):
        dates = occurrence_dates(activity.get("frequency", {}), horizon_start, horizon_end)
        for occurrence_index, target_date in enumerate(dates, start=1):
            tasks.append(task_from_activity(activity, target_date, occurrence_index))

    return tasks


def task_from_activity(
    activity: dict[str, Any], target_date: date, occurrence_index: int
) -> TaskInstance:
    iso_week = target_date.isocalendar()
    target_week = f"{iso_week.year}-W{iso_week.week:02d}"
    required_resources = {
        "provider_ids": activity.get("required_provider_ids", []),
        "equipment_ids": activity.get("required_equipment_ids", []),
        "location_ids": activity.get("allowed_locations", []),
    }
    return TaskInstance(
        task_instance_id=(
            f"task_{activity['activity_id']}_{target_date.strftime('%Y%m%d')}_"
            f"{occurrence_index:03d}"
        ),
        activity_id=activity["activity_id"],
        activity_family_id=activity["activity_family_id"],
        is_substitution=not activity.get("is_primary", False),
        target_date=target_date,
        target_week=target_week,
        duration_minutes=activity["duration_minutes"],
        priority=activity["priority"],
        goal_tags=activity.get("goal_tags", []),
        required_resources=required_resources,
        dependencies=activity.get("dependencies", []),
        status="pending",
    )


def occurrence_dates(
    frequency: dict[str, Any], horizon_start: date, horizon_end: date
) -> list[date]:
    frequency_type = frequency.get("type", "once")
    if frequency_type == "once":
        target = parse_date(frequency.get("target_date")) or horizon_start
        return [target] if horizon_start <= target < horizon_end else []
    if frequency_type == "daily":
        return daily_dates(frequency, horizon_start, horizon_end)
    if frequency_type == "weekly":
        return weekly_dates(frequency, horizon_start, horizon_end)
    if frequency_type == "monthly":
        return monthly_dates(frequency, horizon_start, horizon_end)
    return []


def daily_dates(
    frequency: dict[str, Any], horizon_start: date, horizon_end: date
) -> list[date]:
    count = max(int(frequency.get("count", 1)), 1)
    dates: list[date] = []
    current = horizon_start
    while current < horizon_end:
        dates.extend([current] * count)
        current += timedelta(days=1)
    return dates


def weekly_dates(
    frequency: dict[str, Any], horizon_start: date, horizon_end: date
) -> list[date]:
    count = max(int(frequency.get("count", 1)), 1)
    weekdays = preferred_weekdays(frequency) or list(range(7))
    by_week: dict[str, list[date]] = {}
    current = horizon_start
    while current < horizon_end:
        if current.weekday() in weekdays:
            iso_week = current.isocalendar()
            week = f"{iso_week.year}-W{iso_week.week:02d}"
            by_week.setdefault(week, []).append(current)
        current += timedelta(days=1)
    return [
        occurrence
        for week in sorted(by_week)
        for occurrence in sorted(by_week[week])[:count]
    ]


def monthly_dates(
    frequency: dict[str, Any], horizon_start: date, horizon_end: date
) -> list[date]:
    count = max(int(frequency.get("count", 1)), 1)
    weekdays = preferred_weekdays(frequency) or [horizon_start.weekday()]
    preferred_week = frequency.get("preferred_week")
    dates: list[date] = []
    cursor = date(horizon_start.year, horizon_start.month, 1)

    while cursor < horizon_end:
        month_dates = dates_for_month(cursor.year, cursor.month, weekdays, preferred_week)
        dates.extend([day for day in month_dates if horizon_start <= day < horizon_end][:count])
        cursor = add_months(cursor, 1)

    return dates


def dates_for_month(
    year: int, month: int, weekdays: list[int], preferred_week: str | None
) -> list[date]:
    last_day = monthrange(year, month)[1]
    candidates = [
        date(year, month, day)
        for day in range(1, last_day + 1)
        if date(year, month, day).weekday() in weekdays
    ]
    ordinal = WEEK_ORDINALS.get(str(preferred_week).lower())
    if ordinal is None:
        return candidates
    if ordinal == -1:
        return candidates[-1:]
    start_index = ordinal - 1
    return candidates[start_index : start_index + 1]


def preferred_weekdays(frequency: dict[str, Any]) -> list[int]:
    return [
        WEEKDAYS[day.lower()]
        for day in frequency.get("preferred_days", [])
        if day.lower() in WEEKDAYS
    ]


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def add_months(value: date, months: int) -> date:
    month = value.month - 1 + months
    year = value.year + month // 12
    month = month % 12 + 1
    day = min(value.day, monthrange(year, month)[1])
    return date(year, month, day)


def expansion_report(tasks: list[TaskInstance]) -> str:
    by_activity: dict[str, int] = {}
    primary_count = 0
    substitution_count = 0
    for task in tasks:
        by_activity[task.activity_id] = by_activity.get(task.activity_id, 0) + 1
        if task.is_substitution:
            substitution_count += 1
        else:
            primary_count += 1

    lines = [
        "# Task Expansion Report",
        "",
        f"Expanded task instances: {len(tasks)}",
        f"Primary task instances: {primary_count}",
        f"Substitution task instances: {substitution_count}",
        "",
        "| Activity | Instances |",
        "| --- | ---: |",
    ]
    lines.extend(
        f"| {activity_id} | {count} |" for activity_id, count in sorted(by_activity.items())
    )
    return "\n".join(lines) + "\n"
