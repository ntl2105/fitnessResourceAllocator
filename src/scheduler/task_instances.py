from __future__ import annotations

from calendar import monthrange
from collections import Counter
from datetime import date, datetime, time, timedelta
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

MEAL_SOURCE_WEEKLY_CAPS = {
    "member_assembled": 2,
}


def expand_primary_activities(
    action_plan: dict[str, Any], availability: AvailabilityData
) -> list[TaskInstance]:
    horizon_start = availability.planning_start_date
    horizon_end = add_months(horizon_start, availability.planning_months)
    tasks: list[TaskInstance] = []
    primary_frequencies = {
        activity["activity_id"]: activity.get("frequency", {})
        for activity in action_plan.get("activities", [])
        if activity.get("is_primary", False)
    }

    for activity in action_plan.get("activities", []):
        if activity.get("activity_type") == "food" and activity.get("meal_slot"):
            continue
        frequency = activity.get("frequency", {})
        if frequency.get("type") == "travel_window":
            dates = travel_window_dates(frequency, availability, horizon_start, horizon_end)
        else:
            dates = occurrence_dates(frequency, horizon_start, horizon_end)
        if (
            not dates
            and activity.get("variety_role") == "planned_variety"
            and activity.get("substitution_for_activity_id") in primary_frequencies
        ):
            primary_frequency = primary_frequencies[activity["substitution_for_activity_id"]]
            dates = occurrence_dates(primary_frequency, horizon_start, horizon_end)
        for occurrence_index, target_date in enumerate(dates, start=1):
            tasks.append(task_from_activity(activity, target_date, occurrence_index))

    tasks.extend(meal_coverage_tasks(action_plan, availability, horizon_start, horizon_end))
    return tasks


MEAL_SLOTS = ("breakfast", "lunch", "dinner")


def meal_coverage_tasks(
    action_plan: dict[str, Any],
    availability: AvailabilityData,
    horizon_start: date,
    horizon_end: date,
) -> list[TaskInstance]:
    meals_by_slot = meal_activities_by_slot(action_plan)
    tasks: list[TaskInstance] = []
    weekly_source_counts: Counter[tuple[str, str]] = Counter()
    current = horizon_start
    while current < horizon_end:
        week_id = iso_week_id(current)
        for meal_slot in MEAL_SLOTS:
            activities = meal_coverage_activities(
                meals_by_slot.get(meal_slot, []),
                current,
                meal_slot,
                availability,
                weekly_source_counts,
                week_id,
            )
            for rank, activity in enumerate(activities):
                tasks.append(meal_coverage_task_from_activity(activity, current, meal_slot, rank))
            if activities:
                source = meal_source(activities[0])
                if source in MEAL_SOURCE_WEEKLY_CAPS:
                    weekly_source_counts[(week_id, source)] += 1
        current += timedelta(days=1)
    return tasks


def meal_activities_by_slot(action_plan: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    meals: dict[str, list[dict[str, Any]]] = {slot: [] for slot in MEAL_SLOTS}
    for activity in action_plan.get("activities", []):
        if activity.get("activity_type") != "food":
            continue
        meal_slot = str(activity.get("meal_slot") or "").lower()
        if meal_slot in meals:
            meals[meal_slot].append(activity)
    return meals


def meal_coverage_activity(
    activities: list[dict[str, Any]],
    target_date: date,
    meal_slot: str,
    availability: AvailabilityData,
) -> dict[str, Any] | None:
    activities = meal_coverage_activities(activities, target_date, meal_slot, availability)
    return activities[0] if activities else None


def meal_coverage_activities(
    activities: list[dict[str, Any]],
    target_date: date,
    meal_slot: str,
    availability: AvailabilityData,
    weekly_source_counts: Counter[tuple[str, str]] | None = None,
    week_id: str | None = None,
) -> list[dict[str, Any]]:
    location_preferences = meal_location_preferences(target_date, meal_slot, availability)
    ranked_candidates = meal_coverage_candidates(activities, location_preferences, meal_slot)
    if not ranked_candidates:
        return []
    rotation_index = (target_date.toordinal() + MEAL_SLOTS.index(meal_slot)) % len(ranked_candidates)
    rotated = [*ranked_candidates[rotation_index:], *ranked_candidates[:rotation_index]]
    if weekly_source_counts is None or week_id is None:
        return rotated
    return sorted(
        rotated,
        key=lambda activity: (
            meal_source_cap_penalty(activity, weekly_source_counts, week_id),
            rotated.index(activity),
        ),
    )


def meal_source(activity: dict[str, Any]) -> str:
    return str(activity.get("prep_source") or activity.get("dining_source") or "unknown")


def meal_source_cap_penalty(
    activity: dict[str, Any],
    weekly_source_counts: Counter[tuple[str, str]],
    week_id: str,
) -> int:
    source = meal_source(activity)
    cap = MEAL_SOURCE_WEEKLY_CAPS.get(source)
    if cap is None:
        return 0
    return 1 if weekly_source_counts[(week_id, source)] >= cap else 0


def meal_coverage_candidates(
    activities: list[dict[str, Any]], location_preferences: list[str], meal_slot: str
) -> list[dict[str, Any]]:
    ranked: list[tuple[int, dict[str, Any]]] = []
    for activity in activities:
        skip_adjustment = activity.get("skip_adjustment")
        if isinstance(skip_adjustment, dict) and skip_adjustment.get("is_skip"):
            continue
        location_ranks = [
            location_preferences.index(location)
            for location in activity.get("allowed_locations", [])
            if location in location_preferences
        ]
        if location_ranks:
            ranked.append((min(location_ranks), activity))
    if not ranked:
        return []

    best_rank = min(rank for rank, _activity in ranked)
    if meal_slot == "breakfast":
        ranked = [(rank, activity) for rank, activity in ranked if rank == best_rank]

    return [
        activity
        for _rank, activity in sorted(
            ranked,
            key=lambda item: (
                item[0],
                1 if item[1].get("frequency", {}).get("type") == "as_needed" else 0,
                1 if not item[1].get("is_primary", False) else 0,
                item[1].get("priority", 999),
                item[1].get("activity_id", ""),
            ),
        )
    ]


def meal_location_preferences(
    target_date: date, meal_slot: str, availability: AvailabilityData
) -> list[str]:
    override = member_location_override(
        target_date,
        availability,
        meal_reference_time(meal_slot),
    )
    if override == "travel_hotel":
        return ["travel_hotel"]
    if override == "home" or target_date.weekday() >= 5:
        return ["home", "restaurant"]
    if meal_slot == "lunch":
        return ["office"]
    if meal_slot == "dinner":
        return ["home", "restaurant"]
    return ["home", "office"]


def meal_reference_time(meal_slot: str) -> time:
    return {
        "breakfast": time(7, 0),
        "lunch": time(12, 0),
        "dinner": time(19, 0),
    }.get(meal_slot, time(12, 0))


def member_location_override(
    target_date: date,
    availability: AvailabilityData,
    reference_time: time | None = None,
) -> str | None:
    for block in availability.availability_blocks:
        reference_start = (
            datetime.combine(target_date, reference_time, tzinfo=block.start.tzinfo)
            if reference_time is not None
            else None
        )
        if block.resource_type == "member_travel" and (
            (reference_start is not None and block.start <= reference_start < block.end)
            or (reference_start is None and block_covers_date(block, target_date))
        ):
            return block.location_id or "travel_hotel"
    for block in availability.availability_blocks:
        if block.resource_type == "member_location" and block_covers_date(block, target_date):
            return block.location_id
    return None


def block_covers_date(block: Any, target_date: date) -> bool:
    start = block.start.date()
    end = block.end.date()
    if block.end.time() == block.start.time() and end > start:
        end -= timedelta(days=1)
    return start <= target_date <= end


def iso_week_id(value: date) -> str:
    iso = value.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def meal_coverage_task_from_activity(
    activity: dict[str, Any], target_date: date, meal_slot: str, rank: int = 0
) -> TaskInstance:
    task = task_from_activity(activity, target_date, 900)
    task.task_instance_id = (
        f"task_meal_coverage_{activity['activity_id']}_{target_date.strftime('%Y%m%d')}"
    )
    task.activity_family_id = f"meal_coverage_{meal_slot}_{target_date.strftime('%Y%m%d')}"
    task.is_substitution = False
    task.priority = rank
    return task


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


def travel_window_dates(
    frequency: dict[str, Any],
    availability: AvailabilityData,
    horizon_start: date,
    horizon_end: date,
) -> list[date]:
    count = int(frequency.get("count", 1))
    if count <= 0:
        return []
    dates: list[date] = []
    for block in sorted(availability.availability_blocks, key=lambda item: item.start):
        if block.resource_type != "member_travel":
            continue
        current = max(block.start.date(), horizon_start)
        if block.start.time() != time.min:
            current += timedelta(days=1)
        final = min(block.end.date(), horizon_end - timedelta(days=1))
        window_dates = []
        while current <= final:
            window_dates.append(current)
            current += timedelta(days=1)
        dates.extend(window_dates[:count])
    return dates


def daily_dates(
    frequency: dict[str, Any], horizon_start: date, horizon_end: date
) -> list[date]:
    count = int(frequency.get("count", 1))
    if count <= 0:
        return []
    dates: list[date] = []
    current = horizon_start
    while current < horizon_end:
        dates.extend([current] * count)
        current += timedelta(days=1)
    return dates


def weekly_dates(
    frequency: dict[str, Any], horizon_start: date, horizon_end: date
) -> list[date]:
    count = int(frequency.get("count", 1))
    if count <= 0:
        return []
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
    count = int(frequency.get("count", 1))
    if count <= 0:
        return []
    weekdays = preferred_weekdays(frequency) or [horizon_start.weekday()]
    preferred_week = frequency.get("preferred_week")
    preferred_weeks = frequency.get("preferred_weeks") or []
    dates: list[date] = []
    cursor = date(horizon_start.year, horizon_start.month, 1)
    month_index = 0

    while cursor < horizon_end:
        month_preferred_week = (
            preferred_weeks[month_index % len(preferred_weeks)]
            if preferred_weeks
            else preferred_week
        )
        month_dates = dates_for_month(cursor.year, cursor.month, weekdays, month_preferred_week)
        dates.extend([day for day in month_dates if horizon_start <= day < horizon_end][:count])
        cursor = add_months(cursor, 1)
        month_index += 1

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
