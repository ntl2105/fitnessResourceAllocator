from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from src.models.availability import AvailabilityData
from src.models.schedule import ScheduledTask, TaskInstance
from src.models.trace import ConstraintCheck


def evaluate_policy(
    task: TaskInstance,
    start: datetime,
    end: datetime,
    scheduled_tasks: list[ScheduledTask],
    activity: dict[str, Any] | None = None,
    dependency_state: dict[str, Any] | None = None,
    candidate_location_id: str | None = None,
) -> tuple[bool, list[ConstraintCheck]]:
    availability = (dependency_state or {}).get("availability")
    travel_time_rules = (dependency_state or {}).get("travel_time_rules", [])
    checks = [
        no_overlap_check(start, end, scheduled_tasks),
        movement_spacing_check(start, end, scheduled_tasks, activity),
        late_substantial_fitness_check(start, end, activity),
        same_day_substantial_fitness_check(start, scheduled_tasks, activity),
        same_day_repeat_check(task, start, scheduled_tasks, activity),
        same_provider_consultation_spacing_check(task, start, end, scheduled_tasks, activity),
        meal_slot_exclusivity_check(start, scheduled_tasks, activity),
        location_compatibility_check(start, end, scheduled_tasks, activity),
        member_availability_check(start, end, availability, activity, candidate_location_id, task),
        member_travel_location_check(start, end, candidate_location_id, availability),
        active_travel_required_check(start, end, activity, availability),
        travel_time_buffer_check(
            start,
            end,
            candidate_location_id,
            scheduled_tasks,
            availability,
            travel_time_rules,
        ),
    ]
    checks.extend(dependency_checks(task, start, scheduled_tasks, dependency_state))
    return all(check.passed for check in checks), checks


MOVEMENT_ACTIVITY_TYPES = {"fitness", "therapy"}
MOVEMENT_SPACING_MINUTES = 90
LATEST_SUBSTANTIAL_FITNESS_END_HOUR = 20
LATEST_SUBSTANTIAL_FITNESS_END_MINUTE = 30


def movement_spacing_check(
    start: datetime,
    end: datetime,
    scheduled_tasks: list[ScheduledTask],
    activity: dict[str, Any] | None,
) -> ConstraintCheck:
    if not is_movement_activity(activity):
        return ConstraintCheck(
            name="movement_spacing",
            passed=True,
            reason="Activity is not a standalone movement or therapy block.",
        )

    nearest = None
    nearest_gap = None
    for scheduled in scheduled_tasks:
        if scheduled.start.date() != start.date():
            continue
        if not scheduled_task_is_movement(scheduled):
            continue
        gap = gap_between_minutes(start, end, scheduled.start, scheduled.end)
        if gap is None:
            continue
        if nearest_gap is None or gap < nearest_gap:
            nearest = scheduled
            nearest_gap = gap

    passed = nearest_gap is None or nearest_gap >= MOVEMENT_SPACING_MINUTES
    return ConstraintCheck(
        name="movement_spacing",
        passed=passed,
        reason=(
            "No nearby movement or therapy block creates an unrealistic sequence."
            if passed
            else (
                f"This standalone fitness/therapy block requires {MOVEMENT_SPACING_MINUTES} "
                f"minutes between sessions; only {nearest_gap} minutes around "
                f"{nearest.title if nearest else 'another movement task'}."
            )
        ),
    )


def late_substantial_fitness_check(
    start: datetime,
    end: datetime,
    activity: dict[str, Any] | None,
) -> ConstraintCheck:
    activity = activity or {}
    if (
        activity.get("activity_type") != "fitness"
        or activity.get("load_level") == "low"
        or activity.get("allow_late_finish")
    ):
        return ConstraintCheck(
            name="late_substantial_fitness",
            passed=True,
            reason="Activity is not a medium/high-load fitness session.",
        )
    cutoff = start.replace(
        hour=LATEST_SUBSTANTIAL_FITNESS_END_HOUR,
        minute=LATEST_SUBSTANTIAL_FITNESS_END_MINUTE,
        second=0,
        microsecond=0,
    )
    passed = end <= cutoff
    return ConstraintCheck(
        name="late_substantial_fitness",
        passed=passed,
        reason=(
            "Medium/high-load fitness ends by Marcus's 20:30 cutoff."
            if passed
            else "Rejected because Marcus avoids medium/high-load fitness ending after 20:30."
        ),
    )


def same_day_substantial_fitness_check(
    start: datetime,
    scheduled_tasks: list[ScheduledTask],
    activity: dict[str, Any] | None,
) -> ConstraintCheck:
    activity = activity or {}
    if activity.get("activity_type") != "fitness" or activity.get("load_level") == "low":
        return ConstraintCheck(
            name="same_day_substantial_fitness",
            passed=True,
            reason="Activity is not a substantial fitness session.",
        )
    existing = next(
        (
            scheduled
            for scheduled in scheduled_tasks
            if scheduled.activity_type == "fitness"
            and scheduled.load_level != "low"
            and scheduled.start.date() == start.date()
        ),
        None,
    )
    return ConstraintCheck(
        name="same_day_substantial_fitness",
        passed=existing is None,
        reason=(
            "No substantial fitness session is already scheduled on this day."
            if existing is None
            else f"Rejected because {existing.title} is already the substantial fitness session for this day."
        ),
    )


def is_movement_activity(activity: dict[str, Any] | None) -> bool:
    if not activity:
        return False
    return str(activity.get("activity_type", "")).lower() in MOVEMENT_ACTIVITY_TYPES


def scheduled_task_is_movement(scheduled: ScheduledTask) -> bool:
    activity_type = str(getattr(scheduled, "activity_type", "") or "").lower()
    return activity_type in MOVEMENT_ACTIVITY_TYPES


def gap_between_minutes(
    start: datetime,
    end: datetime,
    other_start: datetime,
    other_end: datetime,
) -> int | None:
    if start >= other_end:
        return int((start - other_end).total_seconds() // 60)
    if other_start >= end:
        return int((other_start - end).total_seconds() // 60)
    return None


def no_overlap_check(
    start: datetime, end: datetime, scheduled_tasks: list[ScheduledTask]
) -> ConstraintCheck:
    overlaps = [
        scheduled
        for scheduled in scheduled_tasks
        if start < scheduled.end and end > scheduled.start
    ]
    return ConstraintCheck(
        name="no_overlap",
        passed=not overlaps,
        reason="No scheduled task overlaps candidate slot."
        if not overlaps
        else f"Overlaps {overlaps[0].task_id}.",
    )


def same_day_repeat_check(
    task: TaskInstance,
    start: datetime,
    scheduled_tasks: list[ScheduledTask],
    activity: dict[str, Any] | None,
) -> ConstraintCheck:
    allowed = bool((activity or {}).get("same_day_repeat_allowed", False))
    repeated = [
        scheduled
        for scheduled in scheduled_tasks
        if scheduled.activity_id == task.activity_id and scheduled.start.date() == start.date()
    ]
    passed = allowed or not repeated
    return ConstraintCheck(
        name="same_day_repeat",
        passed=passed,
        reason="No same-day repeat for this activity."
        if passed
        else "Same-day repeat is not allowed for this activity.",
    )


SAME_PROVIDER_CONSULTATION_BUFFER_MINUTES = 30


def same_provider_consultation_spacing_check(
    task: TaskInstance,
    start: datetime,
    end: datetime,
    scheduled_tasks: list[ScheduledTask],
    activity: dict[str, Any] | None,
) -> ConstraintCheck:
    if (activity or {}).get("activity_type") != "consultation":
        return ConstraintCheck(
            name="same_provider_consultation_spacing",
            passed=True,
            reason="Activity is not a consultation.",
        )
    provider_ids = set(task.required_resources.get("provider_ids", []))
    if not provider_ids:
        return ConstraintCheck(
            name="same_provider_consultation_spacing",
            passed=True,
            reason="Consultation has no provider requirement.",
        )

    for scheduled in scheduled_tasks:
        if scheduled.activity_type != "consultation" or scheduled.start.date() != start.date():
            continue
        shared_provider_ids = provider_ids & set(scheduled.provider_ids)
        if not shared_provider_ids:
            continue
        gap = gap_between_minutes(start, end, scheduled.start, scheduled.end)
        if gap is None or gap < SAME_PROVIDER_CONSULTATION_BUFFER_MINUTES:
            provider_label = ", ".join(sorted(shared_provider_ids))
            return ConstraintCheck(
                name="same_provider_consultation_spacing",
                passed=False,
                reason=(
                    f"Consultation with {provider_label} needs at least "
                    f"{SAME_PROVIDER_CONSULTATION_BUFFER_MINUTES} minutes from "
                    f"{scheduled.title}; current gap is {gap if gap is not None else 0} minutes."
                ),
            )

    return ConstraintCheck(
        name="same_provider_consultation_spacing",
        passed=True,
        reason="No same-provider consultation is too close.",
    )


def meal_slot_exclusivity_check(
    start: datetime,
    scheduled_tasks: list[ScheduledTask],
    activity: dict[str, Any] | None,
) -> ConstraintCheck:
    meal_slot = str((activity or {}).get("meal_slot") or "").lower()
    if not meal_slot:
        return ConstraintCheck(
            name="meal_slot_exclusivity",
            passed=True,
            reason="Activity is not a meal-slot activity.",
        )

    existing = [
        scheduled
        for scheduled in scheduled_tasks
        if scheduled.start.date() == start.date()
        and scheduled_matches_meal_slot(scheduled, meal_slot)
    ]
    return ConstraintCheck(
        name="meal_slot_exclusivity",
        passed=not existing,
        reason=(
            f"No {meal_slot} has been scheduled on this day."
            if not existing
            else f"Rejected because {existing[0].title} already covers {meal_slot} on this day."
        ),
    )


def dependency_checks(
    task: TaskInstance,
    start: datetime,
    scheduled_tasks: list[ScheduledTask],
    dependency_state: dict[str, Any] | None,
) -> list[ConstraintCheck]:
    if not task.dependencies:
        return [ConstraintCheck(
            name="dependencies_acknowledged",
            passed=True,
            reason="Task has no dependencies.",
        )]

    checks = []
    for dependency in task.dependencies:
        if not isinstance(dependency, dict):
            checks.append(
                ConstraintCheck(
                    name="dependency:unknown",
                    passed=False,
                    reason="Dependency metadata is not structured.",
                )
            )
            continue

        dependency_type = dependency.get("type")
        if dependency_type == "fasting":
            checks.append(fasting_dependency_check(dependency))
        elif dependency_type == "hydration":
            checks.append(hydration_dependency_check(dependency))
        elif dependency_type == "food_timing":
            checks.append(food_timing_dependency_check(dependency))
        elif dependency_type == "food_task":
            checks.append(food_task_dependency_check(dependency, start, scheduled_tasks))
        elif dependency_type == "prep_task":
            checks.append(prep_task_dependency_check(dependency, start, dependency_state))
        elif dependency_type == "prerequisite_activity":
            checks.append(prerequisite_activity_check(dependency, start, scheduled_tasks))
        else:
            checks.append(
                ConstraintCheck(
                    name=f"dependency:{dependency_type or 'unknown'}",
                    passed=True,
                    reason=f"Dependency type {dependency_type or 'unknown'} is represented in task metadata.",
                )
            )

    return checks


def fasting_dependency_check(dependency: dict[str, Any]) -> ConstraintCheck:
    hours = dependency.get("hours")
    hours_text = f" for {hours} hours" if hours is not None else ""
    return ConstraintCheck(
        name="dependency:fasting",
        passed=True,
        reason=(
            f"The fasting requirement is represented{hours_text} and must occur before "
            "the candidate slot; no scheduler slot is required."
        ),
    )


def hydration_dependency_check(dependency: dict[str, Any]) -> ConstraintCheck:
    target = dependency.get("target") or dependency.get("amount")
    target_text = f" ({target})" if target else ""
    return ConstraintCheck(
        name="dependency:hydration",
        passed=True,
        reason=f"The hydration requirement is represented{target_text} before/around the candidate slot.",
    )


def food_timing_dependency_check(dependency: dict[str, Any]) -> ConstraintCheck:
    metadata_keys = sorted(key for key in dependency if key != "type")
    passed = bool(metadata_keys)
    return ConstraintCheck(
        name="dependency:food_timing",
        passed=passed,
        reason=(
            f"food timing metadata is present: {', '.join(metadata_keys)}."
            if passed
            else "Food timing dependency is missing timing metadata."
        ),
    )


def food_task_dependency_check(
    dependency: dict[str, Any],
    start: datetime,
    scheduled_tasks: list[ScheduledTask],
) -> ConstraintCheck:
    meal_slot = str(dependency.get("meal_slot") or "").lower()
    if not meal_slot:
        return ConstraintCheck(
            name="dependency:food_task",
            passed=False,
            reason="Food task dependency is missing meal_slot.",
        )

    max_offset = int(dependency.get("offset_minutes_max", 30))
    valid_meals = [
        meal
        for meal in scheduled_tasks
        if meal.start.date() == start.date()
        and scheduled_matches_meal_slot(meal, meal_slot)
        and 0 <= int((start - meal.end).total_seconds() // 60) <= max_offset
    ]

    return ConstraintCheck(
        name="dependency:food_task",
        passed=bool(valid_meals),
        reason=(
            f"Accepted because {meal_slot} ended at {valid_meals[0].end.isoformat()}, "
            f"within {max_offset} minutes of candidate."
            if valid_meals
            else f"Requires a same-day {meal_slot} ending within {max_offset} minutes before candidate."
        ),
    )


def scheduled_matches_meal_slot(scheduled: ScheduledTask, meal_slot: str) -> bool:
    title = scheduled.title.lower()
    goal_tags = {tag.lower() for tag in scheduled.goal_tags}
    return meal_slot in title or meal_slot in goal_tags


def prep_task_dependency_check(
    dependency: dict[str, Any],
    start: datetime,
    dependency_state: dict[str, Any] | None,
) -> ConstraintCheck:
    can_be_done_by_member = bool(dependency.get("can_be_done_by_member"))
    can_be_done_by_provider = bool(dependency.get("can_be_done_by_provider"))
    provider_type = dependency.get("provider_type")

    if not can_be_done_by_member and not can_be_done_by_provider:
        return ConstraintCheck(
            name="dependency:prep_task",
            passed=False,
            reason="Prep task requires can_be_done_by_member or can_be_done_by_provider metadata.",
        )

    if provider_type == "chef":
        availability = (dependency_state or {}).get("availability")
        duration_minutes = int(dependency.get("prep_duration_minutes", 30))
        offset_minutes = int(dependency.get("offset_minutes_min", 0))
        prep_end = start - timedelta(minutes=offset_minutes)
        prep_start = prep_end - timedelta(minutes=duration_minutes)
        chef_available = chef_provider_available_for_prep_window(
            availability, prep_start, prep_end
        )
        if not chef_available and can_be_done_by_member:
            member_available = member_available_for_prep_window(
                availability, prep_start, prep_end
            )
            if not member_available:
                return ConstraintCheck(
                    name="dependency:prep_task",
                    passed=False,
                    reason=(
                        f"Rejected {duration_minutes} minute member prep window ending "
                        f"{offset_minutes} minutes before candidate due to member blocked/travel overlap."
                    ),
                )
            return ConstraintCheck(
                name="dependency:prep_task",
                passed=True,
                reason=(
                    f"Chef provider is not available; accepted {duration_minutes} minute "
                    f"member prep window ending {offset_minutes} minutes before candidate; "
                    "prep task can be done by member."
                ),
            )
        return ConstraintCheck(
            name="dependency:prep_task",
            passed=chef_available,
            reason=(
                f"Accepted {duration_minutes} minute provider prep window ending "
                f"{offset_minutes} minutes before candidate."
                if chef_available
                else f"Rejected {duration_minutes} minute provider prep window ending "
                f"{offset_minutes} minutes before candidate; chef provider availability does not cover it."
            ),
        )

    if can_be_done_by_member:
        availability = (dependency_state or {}).get("availability")
        duration_minutes = int(dependency.get("prep_duration_minutes", 30))
        offset_minutes = int(dependency.get("offset_minutes_min", 0))
        prep_end = start - timedelta(minutes=offset_minutes)
        prep_start = prep_end - timedelta(minutes=duration_minutes)
        member_available = member_available_for_prep_window(
            availability, prep_start, prep_end
        )
        return ConstraintCheck(
            name="dependency:prep_task",
            passed=member_available,
            reason=(
                f"Accepted {duration_minutes} minute member prep window ending "
                f"{offset_minutes} minutes before candidate."
                if member_available
                else f"Rejected {duration_minutes} minute member prep window ending "
                f"{offset_minutes} minutes before candidate due to member blocked/travel overlap."
            ),
        )

    return ConstraintCheck(
        name="dependency:prep_task",
        passed=True,
        reason=f"Prep task can be done by provider type {provider_type or 'provider'} before candidate.",
    )


def chef_provider_available_for_prep_window(
    availability: AvailabilityData | None, prep_start: datetime, prep_end: datetime
) -> bool:
    if availability is None:
        return False
    return any(
        block.resource_type == "provider"
        and "chef" in block.resource_id
        and block.start <= prep_start
        and block.end >= prep_end
        for block in availability.availability_blocks
    )


def member_available_for_prep_window(
    availability: AvailabilityData | None, prep_start: datetime, prep_end: datetime
) -> bool:
    if availability is None:
        return True
    return not any(
        block.resource_type in {"member_blocked", "member_travel"}
        and intervals_overlap(prep_start, prep_end, block.start, block.end)
        for block in availability.availability_blocks
    )


def prerequisite_activity_check(
    dependency: dict[str, Any],
    start: datetime,
    scheduled_tasks: list[ScheduledTask],
) -> ConstraintCheck:
    offset_days_min = int(dependency.get("offset_days_min", 0))
    cutoff = start.date().toordinal() - offset_days_min
    match_description = prerequisite_match_description(dependency)
    eligible = [
        scheduled
        for scheduled in scheduled_tasks
        if scheduled.end.date().toordinal() <= cutoff
        and scheduled_matches_prerequisite(scheduled, dependency)
    ]
    has_prior = bool(eligible)
    return ConstraintCheck(
        name="dependency:prerequisite_activity",
        passed=has_prior,
        reason=(
            f"Prerequisite activity matching {match_description} has been scheduled early enough."
            if has_prior
            else f"Prerequisite activity matching {match_description} has not been scheduled early enough."
        ),
    )


def scheduled_matches_prerequisite(
    scheduled: ScheduledTask, dependency: dict[str, Any]
) -> bool:
    if dependency.get("activity_id"):
        return scheduled.activity_id == dependency["activity_id"]
    if dependency.get("activity_family_id"):
        return getattr(scheduled, "activity_family_id", None) == dependency["activity_family_id"]
    if dependency.get("goal_tags"):
        scheduled_goal_tags = set(getattr(scheduled, "goal_tags", []) or [])
        return bool(scheduled_goal_tags.intersection(set(dependency["goal_tags"])))
    if dependency.get("goal_tag"):
        scheduled_goal_tags = set(getattr(scheduled, "goal_tags", []) or [])
        return dependency["goal_tag"] in scheduled_goal_tags
    if dependency.get("activity_title_contains"):
        title = getattr(scheduled, "title", "") or ""
        return dependency["activity_title_contains"].lower() in title.lower()
    return False


def prerequisite_match_description(dependency: dict[str, Any]) -> str:
    if dependency.get("activity_id"):
        return f"activity_id {dependency['activity_id']!r}"
    if dependency.get("activity_family_id"):
        return f"activity_family_id {dependency['activity_family_id']!r}"
    if dependency.get("goal_tags"):
        return f"any goal tag in {dependency['goal_tags']!r}"
    if dependency.get("goal_tag"):
        return f"goal tag {dependency['goal_tag']!r}"
    if dependency.get("activity_title_contains"):
        return f"title containing {dependency['activity_title_contains']!r}"
    return "an explicit prerequisite reference"


def member_availability_check(
    start: datetime,
    end: datetime,
    availability: AvailabilityData | None,
    activity: dict[str, Any] | None = None,
    candidate_location_id: str | None = None,
    task: TaskInstance | None = None,
) -> ConstraintCheck:
    if availability is None:
        return ConstraintCheck(
            name="member_availability",
            passed=True,
            reason="No member availability blocks were provided.",
        )
    overlapping = next(
        (
            block
            for block in availability.availability_blocks
            if block.resource_type == "member_blocked"
            and intervals_overlap(start, end, block.start, block.end)
        ),
        None,
    )
    if overlapping and is_required_meal_slot(activity, task):
        return ConstraintCheck(
            name="member_availability",
            passed=True,
            reason=(
                "Candidate overlaps a member block, but daily meal slots remain "
                "schedulable unless a fasting/meal-skip reason is explicit."
            ),
        )
    if overlapping and allows_low_complexity_workday_exception(
        overlapping.notes or "", activity, candidate_location_id
    ):
        return ConstraintCheck(
            name="member_availability",
            passed=True,
            reason=(
                "Candidate overlaps a work block, but the block allows "
                "low-complexity remote/office/home tasks and this activity qualifies."
            ),
        )
    return ConstraintCheck(
        name="member_availability",
        passed=overlapping is None,
        reason=(
            "Candidate does not overlap member blocked time."
            if overlapping is None
            else f"Member blocked by {overlapping.notes or overlapping.resource_id} "
            f"from {overlapping.start.isoformat()} to {overlapping.end.isoformat()}."
        ),
    )


def allows_low_complexity_workday_exception(
    notes: str,
    activity: dict[str, Any] | None,
    candidate_location_id: str | None,
) -> bool:
    if "except low-complexity remote tasks" not in notes and (
        "except low-complexity remote/office/home tasks" not in notes
    ):
        return False
    if candidate_location_id not in {"remote", "office", "home"}:
        return False
    activity = activity or {}
    if activity.get("load_level") != "low":
        return False
    if activity.get("activity_type") in {"consultation", "medication", "food"}:
        return True
    return (
        activity.get("activity_type") == "fitness"
        and int(activity.get("duration_minutes") or 999) <= 15
        and activity.get("facilitator_type") in {"self", "member"}
    )


def is_required_meal_slot(activity: dict[str, Any] | None, task: TaskInstance | None = None) -> bool:
    activity = activity or {}
    if task is None or not task.task_instance_id.startswith("task_meal_coverage_"):
        return False
    return activity.get("activity_type") == "food" and activity.get("meal_slot") in {
        "breakfast",
        "lunch",
        "dinner",
    }


def member_travel_location_check(
    start: datetime,
    end: datetime,
    candidate_location_id: str | None,
    availability: AvailabilityData | None,
) -> ConstraintCheck:
    if availability is None or candidate_location_id is None:
        return ConstraintCheck(
            name="member_travel_location",
            passed=True,
            reason="No member travel location constraint applies.",
        )
    overlapping = next(
        (
            block
            for block in availability.availability_blocks
            if block.resource_type in {"member_travel", "travel_window"}
            and intervals_overlap(start, end, block.start, block.end)
        ),
        None,
    )
    if overlapping is None:
        same_day = travel_window_on_date(start, availability)
        if same_day is not None:
            allowed_locations = {"remote", "travel_hotel"}
            if same_day.location_id:
                allowed_locations.add(same_day.location_id)
            passed = candidate_location_id in allowed_locations
            return ConstraintCheck(
                name="member_travel_location",
                passed=passed,
                reason=(
                    f"Candidate location {candidate_location_id} is allowed on member travel day."
                    if passed
                    else f"Candidate location {candidate_location_id} rejected on member travel day; "
                    f"allowed locations are {sorted(allowed_locations)}."
                ),
            )
        return ConstraintCheck(
            name="member_travel_location",
            passed=True,
            reason="Candidate does not overlap member travel.",
        )

    allowed_locations = {"remote", "travel_hotel"}
    if overlapping.location_id:
        allowed_locations.add(overlapping.location_id)
    passed = candidate_location_id in allowed_locations
    return ConstraintCheck(
        name="member_travel_location",
        passed=passed,
        reason=(
            f"Candidate location {candidate_location_id} is allowed during member travel."
            if passed
            else f"Candidate location {candidate_location_id} rejected during member travel; "
            f"allowed locations are {sorted(allowed_locations)}."
        ),
    )


def active_travel_required_check(
    start: datetime,
    end: datetime,
    activity: dict[str, Any] | None,
    availability: AvailabilityData | None,
) -> ConstraintCheck:
    if not activity_requires_active_travel(activity):
        return ConstraintCheck(
            name="active_travel_required",
            passed=True,
            reason="Activity does not require an active travel window.",
        )

    active_travel = active_travel_window(start, end, availability) or travel_window_on_date(
        start, availability
    )
    return ConstraintCheck(
        name="active_travel_required",
        passed=active_travel is not None,
        reason=(
            "Travel-specific activity overlaps an active travel window."
            if active_travel is not None
            else "Travel-specific activity can only be scheduled during an active travel window."
        ),
    )


def activity_requires_active_travel(activity: dict[str, Any] | None) -> bool:
    if not activity:
        return False

    title = str(activity.get("title") or "").lower()
    activity_id = str(activity.get("activity_id") or "").lower()
    family_id = str(activity.get("activity_family_id") or "").lower()
    allowed_locations = set(activity.get("allowed_locations") or [])
    goal_tags = {str(tag).lower() for tag in activity.get("goal_tags") or []}
    phase_ids = {str(phase).lower() for phase in activity.get("journey_phase_applicability") or []}

    title_is_travel_specific = (
        "travel-compatible" in title
        or "during travel" in title
        or "hotel room" in title
        or "hotel gym" in title
    )
    id_is_travel_specific = "travel" in activity_id or "travel" in family_id
    location_is_travel_only = bool(allowed_locations) and allowed_locations.issubset(
        {"remote", "travel_hotel"}
    )
    phase_is_travel_specific = bool(phase_ids) and all(
        "travel" in phase or phase.endswith("_002") or phase.endswith("_004") or phase.endswith("_006")
        for phase in phase_ids
    )

    return (
        title_is_travel_specific
        or (location_is_travel_only and ("travel" in goal_tags or id_is_travel_specific))
        or (location_is_travel_only and phase_is_travel_specific)
    )


def active_travel_window(
    start: datetime,
    end: datetime,
    availability: AvailabilityData | None,
):
    if availability is None:
        return None
    return next(
        (
            block
            for block in availability.availability_blocks
            if block.resource_type in {"member_travel", "travel_window"}
            and intervals_overlap(start, end, block.start, block.end)
        ),
        None,
    )


def travel_window_on_date(start: datetime, availability: AvailabilityData | None):
    if availability is None:
        return None
    return next(
        (
            block
            for block in availability.availability_blocks
            if block.resource_type in {"member_travel", "travel_window"}
            and block.start.date() <= start.date() <= block.end.date()
        ),
        None,
    )


def travel_time_buffer_check(
    start: datetime,
    end: datetime,
    candidate_location_id: str | None,
    scheduled_tasks: list[ScheduledTask],
    availability: AvailabilityData | None,
    travel_time_rules: list[Any],
) -> ConstraintCheck:
    if not candidate_location_id:
        return ConstraintCheck(
            name="travel_time_buffer",
            passed=True,
            reason="Candidate has no location for travel-time evaluation.",
        )

    contexts = travel_contexts_for_day(start, scheduled_tasks, availability)
    for context in contexts:
        context_location = context.get("location_id")
        if not context_location or context_location == candidate_location_id:
            continue
        if context["end"] <= start:
            required_minutes = travel_minutes(
                travel_time_rules, context_location, candidate_location_id
            )
            if required_minutes is not None:
                gap_minutes = int((start - context["end"]).total_seconds() // 60)
                if gap_minutes < required_minutes:
                    return ConstraintCheck(
                        name="travel_time_buffer",
                        passed=False,
                        reason=(
                            f"{context_location}->{candidate_location_id} requires "
                            f"{required_minutes} minutes; only {gap_minutes} minutes available "
                            f"after {context['label']}."
                        ),
                    )
        if end <= context["start"]:
            required_minutes = travel_minutes(
                travel_time_rules, candidate_location_id, context_location
            )
            if required_minutes is not None:
                gap_minutes = int((context["start"] - end).total_seconds() // 60)
                if gap_minutes < required_minutes:
                    return ConstraintCheck(
                        name="travel_time_buffer",
                        passed=False,
                        reason=(
                            f"{candidate_location_id}->{context_location} requires "
                            f"{required_minutes} minutes; only {gap_minutes} minutes available "
                            f"before {context['label']}."
                        ),
                    )
    return ConstraintCheck(
        name="travel_time_buffer",
        passed=True,
        reason="Travel-time buffers fit candidate location.",
    )


def travel_contexts_for_day(
    start: datetime,
    scheduled_tasks: list[ScheduledTask],
    availability: AvailabilityData | None,
) -> list[dict[str, Any]]:
    contexts = [
        {
            "start": scheduled.start,
            "end": scheduled.end,
            "location_id": scheduled.location_id,
            "label": scheduled.task_id,
        }
        for scheduled in scheduled_tasks
        if scheduled.start.date() == start.date() and scheduled.location_id
    ]
    if availability is not None:
        contexts.extend(
            {
                "start": block.start,
                "end": block.end,
                "location_id": block.location_id,
                "label": block.notes or block.resource_id,
            }
            for block in availability.availability_blocks
            if block.resource_type == "member_blocked"
            and block.start.date() == start.date()
            and block.location_id
        )
    return contexts


def travel_minutes(
    travel_time_rules: list[Any], from_location_id: str, to_location_id: str
) -> int | None:
    for rule in travel_time_rules:
        rule_from = getattr(rule, "from_location_id", None)
        rule_to = getattr(rule, "to_location_id", None)
        rule_minutes = getattr(rule, "minutes", None)
        if isinstance(rule, dict):
            rule_from = rule.get("from_location_id")
            rule_to = rule.get("to_location_id")
            rule_minutes = rule.get("minutes")
        if rule_from == from_location_id and rule_to == to_location_id:
            return int(rule_minutes)
    return None


def intervals_overlap(
    start: datetime, end: datetime, other_start: datetime, other_end: datetime
) -> bool:
    return start < other_end and end > other_start


def location_compatibility_check(
    start: datetime,
    end: datetime,
    scheduled_tasks: list[ScheduledTask],
    activity: dict[str, Any] | None,
) -> ConstraintCheck:
    allowed_locations = set((activity or {}).get("allowed_locations", []))
    if not allowed_locations:
        return ConstraintCheck(
            name="location_compatibility",
            passed=True,
            reason="No location restriction declared.",
        )

    same_day_nearby = [
        scheduled
        for scheduled in scheduled_tasks
        if scheduled.location_id
        and scheduled.start.date() == start.date()
        and start < scheduled.end
        and end > scheduled.start
    ]
    incompatible = [
        scheduled
        for scheduled in same_day_nearby
        if scheduled.location_id not in allowed_locations
        and "remote" not in {scheduled.location_id, *allowed_locations}
    ]
    return ConstraintCheck(
        name="location_compatibility",
        passed=not incompatible,
        reason="Candidate location is compatible with nearby scheduled tasks."
        if not incompatible
        else f"Nearby task at incompatible location {incompatible[0].location_id}.",
    )
