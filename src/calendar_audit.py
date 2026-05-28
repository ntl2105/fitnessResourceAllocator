from __future__ import annotations

from datetime import datetime
from typing import Any


def build_constraint_audit(
    calendar_rows: list[dict[str, Any]],
    availability: dict[str, Any],
    resource_universe: dict[str, Any],
) -> dict[str, Any]:
    violations = []
    travel_rules = resource_universe.get("travel_time_rules", [])
    rows = sorted(calendar_rows, key=lambda row: (row["date"], row["start_time"], row["end_time"]))

    for row in rows:
        start = row_datetime(row, "start_time")
        end = row_datetime(row, "end_time")
        violations.extend(member_blocked_violations(row, start, end, availability))
        violations.extend(exact_travel_location_violations(row, start, end, availability))
        violations.extend(wfh_violations(row, start, end, availability))
        violations.extend(arrival_fatigue_violations(row, start, end, availability))
        violations.extend(provider_location_violations(row, start, end, availability))

    for first, second in zip(rows, rows[1:]):
        if first["date"] != second["date"]:
            continue
        violation = transition_violation(first, second, travel_rules)
        if violation:
            violations.append(violation)

    return {
        "status": "pass" if not violations else "fail",
        "violation_count": len(violations),
        "checks": [
            "member_blocked_windows",
            "exact_travel_window_location",
            "wfh_office_ban",
            "arrival_fatigue_load",
            "provider_location_availability",
            "same_day_location_transition_buffer",
        ],
        "violations": violations,
    }


def row_datetime(row: dict[str, Any], key: str) -> datetime:
    return datetime.fromisoformat(f"{row['date']}T{row[key]}:00+08:00")


def member_blocked_violations(
    row: dict[str, Any],
    start: datetime,
    end: datetime,
    availability: dict[str, Any],
) -> list[dict[str, Any]]:
    if row.get("activity_type") == "food":
        return []
    violations = []
    for block in availability.get("availability_blocks", []):
        if block.get("resource_type") != "member_blocked":
            continue
        if "arrival fatigue" in str(block.get("notes", "")).lower() and row.get("activity_type") not in {
            "fitness",
            "therapy",
        }:
            continue
        if allows_low_complexity_workday_exception(block, row):
            continue
        block_start = datetime.fromisoformat(block["start"])
        block_end = datetime.fromisoformat(block["end"])
        if overlaps(start, end, block_start, block_end):
            violations.append(violation(row, "member_blocked_windows", block.get("notes")))
    return violations


def allows_low_complexity_workday_exception(block: dict[str, Any], row: dict[str, Any]) -> bool:
    notes = str(block.get("notes", ""))
    if (
        "except low-complexity remote/office/home tasks" not in notes
        and "except low-complexity home or remote tasks" not in notes
        and "except low-complexity remote tasks" not in notes
    ):
        return False
    if row.get("location_id") not in {"remote", "office", "home"}:
        return False
    if row.get("load_level") != "low":
        return False
    if row.get("activity_type") in {"consultation", "medication", "food"}:
        return True
    if row.get("activity_type") != "fitness":
        return False
    start = row_datetime(row, "start_time")
    end = row_datetime(row, "end_time")
    return (end - start).total_seconds() <= 15 * 60


def exact_travel_location_violations(
    row: dict[str, Any],
    start: datetime,
    end: datetime,
    availability: dict[str, Any],
) -> list[dict[str, Any]]:
    active_travel = any(
        block.get("resource_type") == "member_travel"
        and overlaps(start, end, datetime.fromisoformat(block["start"]), datetime.fromisoformat(block["end"]))
        for block in availability.get("availability_blocks", [])
    )
    location = row.get("location_id")
    if active_travel and location in {"home", "office", "gym", "restaurant", "clinic", "lab"}:
        return [violation(row, "exact_travel_window_location", "In-person local row during active travel.")]
    if location == "travel_hotel" and not active_travel:
        return [violation(row, "exact_travel_window_location", "Travel hotel row outside active travel.")]
    return []


def wfh_violations(
    row: dict[str, Any],
    start: datetime,
    end: datetime,
    availability: dict[str, Any],
) -> list[dict[str, Any]]:
    if row.get("location_id") != "office":
        return []
    wfh = any(
        block.get("resource_type") == "member_location"
        and block.get("location_id") == "home"
        and start.date() == datetime.fromisoformat(block["start"]).date()
        for block in availability.get("availability_blocks", [])
    )
    return [violation(row, "wfh_office_ban", "Office row on WFH date.")] if wfh else []


def arrival_fatigue_violations(
    row: dict[str, Any],
    start: datetime,
    end: datetime,
    availability: dict[str, Any],
) -> list[dict[str, Any]]:
    if row.get("activity_type") not in {"fitness", "therapy"} or row.get("load_level") == "low":
        return []
    fatigue = any(
        block.get("resource_type") in {"member_blocked", "scheduling_rule", "member_load_restriction"}
        and "arrival fatigue" in str(block.get("notes", "")).lower()
        and overlaps(start, end, datetime.fromisoformat(block["start"]), datetime.fromisoformat(block["end"]))
        for block in availability.get("availability_blocks", [])
    )
    return [violation(row, "arrival_fatigue_load", "Medium/high load row during arrival fatigue.")] if fatigue else []


def provider_location_violations(
    row: dict[str, Any],
    start: datetime,
    end: datetime,
    availability: dict[str, Any],
) -> list[dict[str, Any]]:
    provider_ids = row.get("provider_ids") or []
    if not provider_ids:
        return []
    violations = []
    for provider_id in provider_ids:
        covered = any(
            block.get("resource_id") == provider_id
            and block.get("resource_type") == "provider"
            and datetime.fromisoformat(block["start"]) <= start
            and datetime.fromisoformat(block["end"]) >= end
            and (
                block.get("location_id") == row.get("location_id")
                or (row.get("location_id") == "remote" and block.get("remote_supported"))
            )
            for block in availability.get("availability_blocks", [])
        )
        if not covered:
            violations.append(
                violation(row, "provider_location_availability", f"{provider_id} unavailable at row location.")
            )
    return violations


def transition_violation(
    first: dict[str, Any], second: dict[str, Any], travel_rules: list[dict[str, Any]]
) -> dict[str, Any] | None:
    first_location = first.get("location_id")
    second_location = second.get("location_id")
    if not first_location or not second_location or first_location == second_location:
        return None
    required = travel_minutes(first_location, second_location, travel_rules)
    if required is None:
        return None
    first_end = row_datetime(first, "end_time")
    second_start = row_datetime(second, "start_time")
    gap = int((second_start - first_end).total_seconds() // 60)
    if gap >= required:
        return None
    return {
        "check_id": "same_day_location_transition_buffer",
        "date": second["date"],
        "calendar_row_id": second.get("calendar_row_id"),
        "title": second.get("title"),
        "message": f"{first_location}->{second_location} requires {required}m; only {gap}m available.",
    }


def travel_minutes(from_location: str, to_location: str, travel_rules: list[dict[str, Any]]) -> int | None:
    for rule in travel_rules:
        if rule.get("from_location_id") == from_location and rule.get("to_location_id") == to_location:
            return int(rule["minutes"])
    return None


def overlaps(start: datetime, end: datetime, other_start: datetime, other_end: datetime) -> bool:
    return start < other_end and end > other_start


def violation(row: dict[str, Any], check_id: str, message: str | None) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "date": row.get("date"),
        "calendar_row_id": row.get("calendar_row_id"),
        "title": row.get("title"),
        "message": message or check_id,
    }
