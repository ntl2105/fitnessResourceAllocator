from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Iterable

from src.models.availability import AvailabilityData
from src.models.schedule import TaskInstance
from src.scheduler.task_instances import add_months


DEFAULT_TIMES = [
    time(7, 0),
    time(7, 30),
    time(8, 0),
    time(8, 30),
    time(9, 0),
    time(9, 30),
    time(10, 0),
    time(13, 0),
    time(16, 0),
    time(18, 45),
]

FITNESS_FALLBACK_TIMES = [
    time(19, 15),
    time(19, 30),
    time(19, 50),
]


def sort_tasks(tasks: Iterable[TaskInstance]) -> list[TaskInstance]:
    return sorted(
        tasks,
        key=lambda task: (
            task.priority + (0.5 if task.is_substitution else 0),
            task.target_date or date.max,
            task.activity_id,
            task.task_instance_id,
        ),
    )


def candidate_slots(
    task: TaskInstance,
    activity: dict[str, Any],
    availability: AvailabilityData,
) -> list[dict[str, Any]]:
    dates = candidate_dates(task, availability, activity)
    times = candidate_times(activity, task, availability, dates)
    tzinfo = (
        availability.availability_blocks[0].start.tzinfo
        if availability.availability_blocks
        else timezone.utc
    )
    slots = []
    for candidate_date in dates:
        day_times = candidate_times_for_date(task, activity, candidate_date, times)
        for candidate_time in day_times:
            for location_id in candidate_locations(activity, task):
                start = datetime.combine(candidate_date, candidate_time, tzinfo=tzinfo)
                end = start + timedelta(minutes=task.duration_minutes)
                slots.append(
                    {
                        "start": start,
                        "end": end,
                        "location_id": location_id,
                    }
                )
    return slots


def candidate_times_for_date(
    task: TaskInstance,
    activity: dict[str, Any],
    candidate_date: date,
    times: list[time],
) -> list[time]:
    if (
        activity.get("activity_type") == "fitness"
        and task.target_date is not None
        and candidate_date > task.target_date
    ):
        return times
    return times


def candidate_times(
    activity: dict[str, Any],
    task: TaskInstance,
    availability: AvailabilityData,
    dates: list[date],
) -> list[time]:
    frequency = activity.get("frequency", {})
    preferred_windows = parsed_preferred_windows(frequency)
    times = preferred_times(frequency) or list(DEFAULT_TIMES)
    if activity.get("activity_type") == "fitness":
        times.extend(DEFAULT_TIMES)
        times.extend(FITNESS_FALLBACK_TIMES)
    for start, end in preferred_windows:
        times.extend(window_times(start, end, task.duration_minutes))
    candidate_dates_set = set(dates)
    duration = timedelta(minutes=task.duration_minutes)

    for block in availability.availability_blocks:
        if block.resource_id not in task.required_resources.get("provider_ids", []):
            continue
        if block.start.date() not in candidate_dates_set:
            continue
        if block.end - block.start < duration:
            continue
        times.append(block.start.time().replace(second=0, microsecond=0))

    return list(dict.fromkeys(times))


def window_times(start: time, end: time, duration_minutes: int) -> list[time]:
    values = []
    cursor = datetime.combine(date.today(), start)
    window_end = datetime.combine(date.today(), end)
    duration = timedelta(minutes=duration_minutes)
    while cursor + duration <= window_end:
        values.append(cursor.time().replace(second=0, microsecond=0))
        cursor += timedelta(minutes=30)
    return values


def candidate_dates(
    task: TaskInstance,
    availability: AvailabilityData,
    activity: dict[str, Any] | None = None,
) -> list[date]:
    horizon_start = availability.planning_start_date
    horizon_end = add_months(horizon_start, availability.planning_months)
    if task.target_date:
        dates = [
            task.target_date + timedelta(days=offset)
            for offset in range(target_drift_days(activity) + 1)
        ]
    else:
        dates = [horizon_start + timedelta(days=offset) for offset in range(14)]
    return [candidate_date for candidate_date in dates if horizon_start <= candidate_date < horizon_end]


def target_drift_days(activity: dict[str, Any] | None) -> int:
    activity = activity or {}
    if activity.get("meal_slot"):
        return 0
    if activity.get("activity_type") == "food":
        return 0
    if activity.get("activity_type") == "medication":
        return 0
    if activity.get("activity_type") == "fitness":
        return 1
    return 6


def preferred_times(frequency: dict[str, Any]) -> list[time]:
    times = []
    for window in frequency.get("preferred_time_windows", []):
        start_text = str(window).split("-", maxsplit=1)[0]
        hour, minute = [int(part) for part in start_text.split(":")]
        times.append(time(hour, minute))
    return times


def parsed_preferred_windows(frequency: dict[str, Any]) -> list[tuple[time, time]]:
    windows = []
    for window in frequency.get("preferred_time_windows", []):
        start_text, _, end_text = str(window).partition("-")
        if not end_text:
            continue
        start_hour, start_minute = [int(part) for part in start_text.split(":")]
        end_hour, end_minute = [int(part) for part in end_text.split(":")]
        start = time(start_hour, start_minute)
        end = time(end_hour, end_minute)
        if start <= end:
            windows.append((start, end))
    return windows


def candidate_locations(activity: dict[str, Any], task: TaskInstance) -> list[str | None]:
    locations = activity.get("allowed_locations") or task.required_resources.get("location_ids") or []
    if activity_requires_remote_location(activity):
        locations = [location for location in locations if location == "remote"]
    return list(dict.fromkeys(locations)) or [None]


def preferred_location(activity: dict[str, Any], task: TaskInstance) -> str | None:
    return candidate_locations(activity, task)[0]


def activity_requires_remote_location(activity: dict[str, Any]) -> bool:
    title = str(activity.get("title") or "").lower()
    if title.startswith("remote ") or "remote trainer-led" in title:
        return True
    return False
