from __future__ import annotations

from datetime import datetime

from src.models.availability import AvailabilityData
from src.models.schedule import TaskInstance
from src.models.trace import ConstraintCheck


MEMBER_CONTEXT_LOCATIONS = {"remote", "home", "office", "restaurant"}


def check_required_resources(
    task: TaskInstance,
    start: datetime,
    end: datetime,
    availability: AvailabilityData,
    candidate_location_id: str | None = None,
) -> tuple[bool, list[ConstraintCheck]]:
    resource_ids = required_resource_ids(task)
    location_ids = required_location_ids(task, candidate_location_id)
    if not resource_ids and not location_ids:
        return (
            True,
            [
                ConstraintCheck(
                    name="resource_available:none",
                    passed=True,
                    reason="Task has no required resources.",
                )
            ],
        )

    checks = []
    for resource_id in resource_ids:
        matching_block = next(
            (
                block
                for block in availability.availability_blocks
                if block.resource_id == resource_id and block.start <= start and block.end >= end
            ),
            None,
        )
        checks.append(
            ConstraintCheck(
                name=f"resource_available:{resource_id}",
                passed=matching_block is not None,
                reason=(
                    "Availability block covers candidate slot."
                    if matching_block
                    else "No availability block covers candidate slot."
                ),
            )
        )
    for location_id in location_ids:
        checks.append(location_available_check(location_id, start, end, availability))
    return all(check.passed for check in checks), checks


def required_resource_ids(task: TaskInstance) -> list[str]:
    resources = task.required_resources or {}
    ids: list[str] = []
    for key in ("provider_ids", "equipment_ids"):
        ids.extend(resources.get(key, []))
    return ids


def required_location_ids(
    task: TaskInstance, candidate_location_id: str | None = None
) -> list[str]:
    if candidate_location_id:
        return [candidate_location_id]
    return (task.required_resources or {}).get("location_ids", [])


def location_available_check(
    location_id: str,
    start: datetime,
    end: datetime,
    availability: AvailabilityData,
) -> ConstraintCheck:
    if location_id in MEMBER_CONTEXT_LOCATIONS:
        if location_id == "remote":
            reason = (
                "Remote location does not require a physical location availability block; "
                "remote is a member-context location."
            )
        else:
            reason = (
                f"{location_id} is a member-context location and does not require "
                "a physical facility availability block."
            )
        return ConstraintCheck(
            name=f"location_available:{location_id}",
            passed=True,
            reason=reason,
        )
    if location_id == "travel_hotel" and member_travel_covers_date(start, availability):
        return ConstraintCheck(
            name=f"location_available:{location_id}",
            passed=True,
            reason="Travel hotel is the member-context location for this travel date.",
        )

    matching_block = next(
        (
            block
            for block in availability.availability_blocks
            if block.resource_id == location_id
            and block.resource_type == "location"
            and block.start <= start
            and block.end >= end
        ),
        None,
    )
    return ConstraintCheck(
        name=f"location_available:{location_id}",
        passed=matching_block is not None,
        reason=(
            f"Availability block covers physical location {location_id}."
            if matching_block
            else f"No availability block covers physical location {location_id} for candidate slot."
        ),
    )


def member_travel_covers_date(start: datetime, availability: AvailabilityData) -> bool:
    return any(
        block.resource_type in {"member_travel", "travel_window"}
        and block.start.date() <= start.date() <= block.end.date()
        for block in availability.availability_blocks
    )
