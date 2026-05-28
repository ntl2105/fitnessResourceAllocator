from __future__ import annotations

from datetime import datetime
from typing import Any

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
                if block.resource_id == resource_id
                and block.start <= start
                and block.end >= end
                and resource_location_matches(block, candidate_location_id)
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
    if location_id == "travel_hotel" and member_travel_covers_slot(start, end, availability):
        return ConstraintCheck(
            name=f"location_available:{location_id}",
            passed=True,
            reason="Travel hotel is the member-context location for this active travel slot.",
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


def resource_location_matches(block: Any, candidate_location_id: str | None) -> bool:
    block_location = getattr(block, "location_id", None)
    resource_type = getattr(block, "resource_type", None)
    if not candidate_location_id or not block_location:
        return True
    if resource_type == "provider":
        return block_location == candidate_location_id or (
            candidate_location_id == "remote" and bool(getattr(block, "remote_supported", False))
        )
    if resource_type == "equipment":
        return block_location == candidate_location_id or block_location == "portable"
    return True


def member_travel_covers_slot(start: datetime, end: datetime, availability: AvailabilityData) -> bool:
    return any(
        block.resource_type in {"member_travel", "travel_window"}
        and start < block.end
        and end > block.start
        for block in availability.availability_blocks
    )
