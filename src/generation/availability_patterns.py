from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from src.models.availability import AvailabilityData


WEEKDAY_INDEX = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def expand_availability_patterns(payload: dict[str, Any]) -> dict[str, Any]:
    """Expand compact availability patterns into scheduler-facing blocks."""

    planning_start = date.fromisoformat(payload["planning_start_date"])
    planning_months = int(payload["planning_months"])
    planning_end = add_months(planning_start, planning_months)
    blocks: list[dict[str, Any]] = []

    for pattern in payload.get("patterns", []):
        pattern_type = pattern["type"]
        if pattern_type == "weekly":
            blocks.extend(expand_weekly_pattern(pattern, planning_start, planning_end))
        elif pattern_type in {"once", "date_range"}:
            blocks.append(expand_direct_block(pattern))
        else:
            raise ValueError(f"Unsupported availability pattern type: {pattern_type}")

    expanded = {
        "planning_start_date": planning_start.isoformat(),
        "planning_months": planning_months,
        "availability_blocks": sorted(blocks, key=lambda block: (block["start"], block["resource_id"])),
    }
    AvailabilityData.model_validate(expanded)
    return expanded


def expand_weekly_pattern(
    pattern: dict[str, Any], planning_start: date, planning_end: date
) -> list[dict[str, Any]]:
    timezone_name = pattern["timezone"]
    timezone = ZoneInfo(timezone_name)
    start_date = max(date.fromisoformat(pattern.get("start_date", planning_start.isoformat())), planning_start)
    end_date = min(date.fromisoformat(pattern.get("end_date", planning_end.isoformat())), planning_end)
    weekdays = {WEEKDAY_INDEX[day.lower()] for day in pattern["days"]}
    start_time = parse_time(pattern["start_time"])
    end_time = parse_time(pattern["end_time"])
    skip_ranges = [
        (parse_date_or_datetime(item["start"]).date(), parse_date_or_datetime(item["end"]).date())
        for item in pattern.get("skip_date_ranges", [])
    ]

    blocks = []
    current = start_date
    while current < end_date:
        if current.weekday() in weekdays and not in_skip_range(current, skip_ranges):
            start = datetime.combine(current, start_time, tzinfo=timezone)
            end = datetime.combine(current, end_time, tzinfo=timezone)
            if end <= start:
                end += timedelta(days=1)
            blocks.append(build_block(pattern, start, end))
        current += timedelta(days=1)
    return blocks


def expand_direct_block(pattern: dict[str, Any]) -> dict[str, Any]:
    timezone = ZoneInfo(pattern["timezone"])
    start = parse_date_or_datetime(pattern["start"], timezone)
    end = parse_date_or_datetime(pattern["end"], timezone)
    return build_block(pattern, start, end)


def build_block(pattern: dict[str, Any], start: datetime, end: datetime) -> dict[str, Any]:
    return {
        "resource_id": pattern["resource_id"],
        "resource_type": pattern["resource_type"],
        "start": start.isoformat(),
        "end": end.isoformat(),
        "timezone": pattern["timezone"],
        "location_id": pattern.get("location_id"),
        "remote_supported": bool(pattern.get("remote_supported", False)),
        "travel_compatible": bool(pattern.get("travel_compatible", False)),
        "notes": pattern.get("notes"),
    }


def parse_time(value: str) -> time:
    hour, minute = [int(part) for part in value.split(":", maxsplit=1)]
    return time(hour, minute)


def parse_date_or_datetime(value: str, timezone: ZoneInfo | None = None) -> datetime:
    if "T" in value:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None and timezone is not None:
            return parsed.replace(tzinfo=timezone)
        return parsed
    parsed_date = date.fromisoformat(value)
    return datetime.combine(parsed_date, time.min, tzinfo=timezone)


def in_skip_range(candidate: date, skip_ranges: list[tuple[date, date]]) -> bool:
    return any(start <= candidate <= end for start, end in skip_ranges)


def add_months(start_date: date, month_count: int) -> date:
    month_index = start_date.month - 1 + month_count
    year = start_date.year + month_index // 12
    month = month_index % 12 + 1
    return start_date.replace(day=1, year=year, month=month)
