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
    dates = candidate_dates(task, availability)
    times = preferred_times(activity.get("frequency", {})) or DEFAULT_TIMES
    tzinfo = (
        availability.availability_blocks[0].start.tzinfo
        if availability.availability_blocks
        else timezone.utc
    )
    slots = []
    for candidate_date in dates:
        for candidate_time in times:
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


def candidate_dates(task: TaskInstance, availability: AvailabilityData) -> list[date]:
    horizon_start = availability.planning_start_date
    horizon_end = add_months(horizon_start, availability.planning_months)
    if task.target_date:
        dates = [task.target_date + timedelta(days=offset) for offset in range(7)]
    else:
        dates = [horizon_start + timedelta(days=offset) for offset in range(14)]
    return [candidate_date for candidate_date in dates if horizon_start <= candidate_date < horizon_end]


def preferred_times(frequency: dict[str, Any]) -> list[time]:
    times = []
    for window in frequency.get("preferred_time_windows", []):
        start_text = str(window).split("-", maxsplit=1)[0]
        hour, minute = [int(part) for part in start_text.split(":")]
        times.append(time(hour, minute))
    return times


def candidate_locations(activity: dict[str, Any], task: TaskInstance) -> list[str | None]:
    locations = activity.get("allowed_locations") or task.required_resources.get("location_ids") or []
    return list(dict.fromkeys(locations)) or [None]


def preferred_location(activity: dict[str, Any], task: TaskInstance) -> str | None:
    return candidate_locations(activity, task)[0]
