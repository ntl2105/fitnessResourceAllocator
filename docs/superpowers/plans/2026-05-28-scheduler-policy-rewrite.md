# Scheduler Policy Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current greedy scheduler behavior with a one-time phased policy scheduler that enforces daily food, daily medication, weekly no-spill fitness, and rolling labs/care check-ins without adding persistent data fields.

**Architecture:** Add a derived day-policy layer and a derived scheduler-class layer, then route task placement through explicit phases. Keep the current JSON data shape and output artifacts, but add richer trace reasons and use code-side maps for ambiguous demo families.

**Tech Stack:** Python, Pydantic models, JSON data artifacts, pytest.

---

## File Structure

- Create `src/scheduler/day_policy.py`: builds one `DayPolicy` per date with resolved member location, derived work blocks, travel/fatigue/explicit context, and work-compatible rules.
- Create `src/scheduler/classes.py`: derives scheduler classes from existing activity fields and small code-side maps.
- Modify `src/scheduler/policy.py`: evaluate member availability from `DayPolicy` when provided; keep old availability checks as compatibility fallback.
- Modify `src/scheduler/placement.py`: support candidate-date modes for daily no-spill, weekly no-spill, and rolling day-by-day tasks.
- Modify `src/scheduler/engine.py`: add phased placement order and class-aware failure statuses/reasons.
- Modify `src/scheduler/task_instances.py`: keep meal coverage generation compatible, but stop using it as the main policy source once phased meal placement owns coverage.
- Modify `scripts/build_demo_run.py` only if a new scheduler entrypoint argument or import is needed.
- Test `tests/test_day_policy.py`: day location/work-block derivation.
- Test `tests/test_scheduler_classes.py`: derived scheduler class coverage.
- Test `tests/test_scheduler.py`: phased scheduler behavior.
- Test `tests/test_demo_scenarios.py`: full demo invariants.

## Task 1: Add DayPolicy Builder

**Files:**
- Create: `src/scheduler/day_policy.py`
- Create: `tests/test_day_policy.py`

- [ ] **Step 1: Write failing day-policy tests**

Create `tests/test_day_policy.py`:

```python
from datetime import date, datetime, timezone

from src.models.availability import AvailabilityBlock, AvailabilityData
from src.scheduler.day_policy import build_day_policies


UTC = timezone.utc


def test_day_policy_derives_office_home_and_travel_work_blocks():
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[
            AvailabilityBlock(
                resource_id="travel_hk",
                resource_type="member_travel",
                start=datetime(2026, 6, 3, 10, tzinfo=UTC),
                end=datetime(2026, 6, 5, 20, tzinfo=UTC),
                timezone="UTC",
                location_id="travel_hotel",
            ),
            AvailabilityBlock(
                resource_id="wfh",
                resource_type="member_location",
                start=datetime(2026, 6, 12, 0, tzinfo=UTC),
                end=datetime(2026, 6, 13, 0, tzinfo=UTC),
                timezone="UTC",
                location_id="home",
            ),
        ],
    )

    policies = build_day_policies(availability)

    assert policies[date(2026, 6, 1)].member_location == "office"
    assert policies[date(2026, 6, 1)].core_work_blocks[0].location_id == "office"
    assert policies[date(2026, 6, 3)].member_location == "travel_hotel"
    assert policies[date(2026, 6, 3)].core_work_blocks[0].location_id == "travel_hotel"
    assert policies[date(2026, 6, 12)].member_location == "home"
    assert policies[date(2026, 6, 12)].core_work_blocks[0].location_id == "home"
    assert policies[date(2026, 6, 7)].member_location == "home"
    assert policies[date(2026, 6, 7)].core_work_blocks == []


def test_day_policy_keeps_explicit_fatigue_blocks():
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[
            AvailabilityBlock(
                resource_id="fatigue",
                resource_type="member_blocked",
                start=datetime(2026, 6, 3, 14, tzinfo=UTC),
                end=datetime(2026, 6, 4, 10, tzinfo=UTC),
                timezone="UTC",
                location_id="travel_hotel",
                notes="Arrival fatigue after flight.",
            ),
        ],
    )

    policies = build_day_policies(availability)

    assert policies[date(2026, 6, 3)].explicit_blocks[0].reason_code == "arrival_fatigue"
    assert policies[date(2026, 6, 4)].explicit_blocks[0].reason_code == "arrival_fatigue"
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
pytest tests/test_day_policy.py -q
```

Expected: fails with `ModuleNotFoundError: No module named 'src.scheduler.day_policy'`.

- [ ] **Step 3: Implement `src/scheduler/day_policy.py`**

Create:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

from src.models.availability import AvailabilityBlock, AvailabilityData
from src.scheduler.task_instances import add_months


@dataclass(frozen=True)
class PolicyBlock:
    start: datetime
    end: datetime
    location_id: str | None
    reason_code: str
    notes: str | None = None


@dataclass(frozen=True)
class DayPolicy:
    date: date
    member_location: str
    is_travel: bool = False
    is_wfh: bool = False
    core_work_blocks: list[PolicyBlock] = field(default_factory=list)
    explicit_blocks: list[PolicyBlock] = field(default_factory=list)


def build_day_policies(availability: AvailabilityData) -> dict[date, DayPolicy]:
    start = availability.planning_start_date
    end = add_months(start, availability.planning_months)
    policies = {}
    current = start
    while current < end:
        travel = first_block_for_date(availability, current, "member_travel")
        wfh = first_block_for_date(availability, current, "member_location")
        member_location = resolved_member_location(current, travel, wfh)
        core_work_blocks = derived_core_work_blocks(current, member_location)
        explicit_blocks = explicit_member_blocks_for_date(availability, current)
        policies[current] = DayPolicy(
            date=current,
            member_location=member_location,
            is_travel=travel is not None,
            is_wfh=wfh is not None and travel is None,
            core_work_blocks=core_work_blocks,
            explicit_blocks=explicit_blocks,
        )
        current += timedelta(days=1)
    return policies


def resolved_member_location(
    target_date: date,
    travel: AvailabilityBlock | None,
    wfh: AvailabilityBlock | None,
) -> str:
    if travel is not None:
        return travel.location_id or "travel_hotel"
    if wfh is not None:
        return wfh.location_id or "home"
    if target_date.weekday() < 5:
        return "office"
    return "home"


def derived_core_work_blocks(target_date: date, location_id: str) -> list[PolicyBlock]:
    if target_date.weekday() >= 5:
        return []
    start = datetime.combine(target_date, time(8, 30))
    end = datetime.combine(target_date, time(18, 30))
    return [
        PolicyBlock(
            start=start,
            end=end,
            location_id=location_id if location_id in {"office", "home", "travel_hotel"} else "remote",
            reason_code="core_work",
            notes="Derived core work block for resolved member location.",
        )
    ]


def explicit_member_blocks_for_date(
    availability: AvailabilityData, target_date: date
) -> list[PolicyBlock]:
    blocks = []
    for block in availability.availability_blocks:
        if block.resource_type != "member_blocked":
            continue
        if not block_covers_date(block, target_date):
            continue
        notes = block.notes or ""
        reason_code = "arrival_fatigue" if "Arrival fatigue" in notes else "explicit_member_block"
        blocks.append(
            PolicyBlock(
                start=block.start,
                end=block.end,
                location_id=block.location_id,
                reason_code=reason_code,
                notes=notes,
            )
        )
    return blocks


def first_block_for_date(
    availability: AvailabilityData, target_date: date, resource_type: str
) -> AvailabilityBlock | None:
    return next(
        (
            block
            for block in availability.availability_blocks
            if block.resource_type == resource_type and block_covers_date(block, target_date)
        ),
        None,
    )


def block_covers_date(block: AvailabilityBlock, target_date: date) -> bool:
    start = block.start.date()
    end = block.end.date()
    if block.end.time() == block.start.time() and end > start:
        end -= timedelta(days=1)
    return start <= target_date <= end
```

- [ ] **Step 4: Run tests to verify pass**

Run:

```bash
pytest tests/test_day_policy.py -q
```

Expected: `2 passed`.

## Task 2: Add Derived Scheduler Classification

**Files:**
- Create: `src/scheduler/classes.py`
- Create: `tests/test_scheduler_classes.py`

- [ ] **Step 1: Write failing classifier tests**

Create `tests/test_scheduler_classes.py`:

```python
from src.scheduler.classes import (
    DAILY_REQUIRED_FOOD,
    DAILY_REQUIRED_MEDICATION,
    OPPORTUNISTIC,
    ROLLING_PRIORITY,
    WEEKLY_REQUIRED_FITNESS,
    WEEKLY_SUPPORT,
    classify_activity,
)


def test_classifies_daily_food_and_medication():
    assert classify_activity(
        {"activity_type": "food", "meal_slot": "breakfast", "frequency": {"type": "as_needed"}}
    ) == DAILY_REQUIRED_FOOD
    assert classify_activity(
        {"activity_type": "medication", "frequency": {"type": "daily"}}
    ) == DAILY_REQUIRED_MEDICATION


def test_classifies_weekly_fitness_by_counted_goal_action():
    activity = {
        "activity_type": "fitness",
        "frequency": {"type": "weekly"},
        "goal_contributions": [
            {
                "goal_action_id": "ga_aerobic_conditioning_weekly",
                "counts_toward_weekly_target": True,
                "value": 1,
            }
        ],
    }

    assert classify_activity(activity) == WEEKLY_REQUIRED_FITNESS


def test_classifies_rolling_priority_and_office_break_maps():
    assert classify_activity(
        {"activity_family_id": "b05_clinical_lab_draw_due_week", "activity_type": "consultation"}
    ) == ROLLING_PRIORITY
    assert classify_activity(
        {
            "activity_family_id": "b02_cardio_walking_office",
            "activity_type": "fitness",
            "frequency": {"type": "as_needed"},
        }
    ) == WEEKLY_SUPPORT


def test_classifies_as_needed_fallback_as_opportunistic():
    assert classify_activity(
        {"activity_type": "fitness", "frequency": {"type": "as_needed"}}
    ) == OPPORTUNISTIC
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
pytest tests/test_scheduler_classes.py -q
```

Expected: fails with missing module.

- [ ] **Step 3: Implement `src/scheduler/classes.py`**

Create:

```python
from __future__ import annotations

from typing import Any


DAILY_REQUIRED_FOOD = "daily_required_food"
DAILY_REQUIRED_MEDICATION = "daily_required_medication"
ROLLING_PRIORITY = "rolling_priority"
WEEKLY_REQUIRED_FITNESS = "weekly_required_fitness"
WEEKLY_SUPPORT = "weekly_support"
OPPORTUNISTIC = "opportunistic"


ROLLING_PRIORITY_FAMILIES = {
    "b05_clinical_lab_draw_due_week",
    "b05_clinical_physician_review_due_week",
    "b05_clinical_dietitian_lab_followup",
    "b05_clinical_remote_care_team_handoff",
    "b05_clinical_dietitian_review_monthly",
    "b05_clinical_biometric_review_support",
}


OFFICE_BREAK_FAMILIES = {
    "b02_cardio_walking_office",
}


FITNESS_DOSE_ACTIONS = {
    "ga_aerobic_conditioning_weekly",
    "ga_strength_sessions_weekly",
}


def classify_activity(activity: dict[str, Any]) -> str:
    family_id = activity.get("activity_family_id")
    activity_type = activity.get("activity_type")
    frequency = activity.get("frequency", {})

    if family_id in ROLLING_PRIORITY_FAMILIES:
        return ROLLING_PRIORITY
    if family_id in OFFICE_BREAK_FAMILIES:
        return WEEKLY_SUPPORT
    if activity_type == "food" and activity.get("meal_slot") in {"breakfast", "lunch", "dinner"}:
        return DAILY_REQUIRED_FOOD
    if activity_type == "medication" and frequency.get("type") == "daily":
        return DAILY_REQUIRED_MEDICATION
    if activity_type == "fitness" and counts_toward_fitness_dose(activity):
        return WEEKLY_REQUIRED_FITNESS
    if is_support_only(activity):
        return WEEKLY_SUPPORT
    return OPPORTUNISTIC


def counts_toward_fitness_dose(activity: dict[str, Any]) -> bool:
    for contribution in activity.get("goal_contributions", []):
        if not contribution.get("counts_toward_weekly_target"):
            continue
        if contribution.get("goal_action_id") in FITNESS_DOSE_ACTIONS:
            return True
    return False


def is_support_only(activity: dict[str, Any]) -> bool:
    contributions = activity.get("goal_contributions", [])
    if contributions and all(not item.get("counts_toward_weekly_target") for item in contributions):
        return True
    return activity.get("frequency", {}).get("type") == "as_needed" and activity.get("load_level") == "low"
```

- [ ] **Step 4: Run tests to verify pass**

Run:

```bash
pytest tests/test_scheduler_classes.py -q
```

Expected: `4 passed`.

## Task 3: Make Member Availability Policy Use DayPolicy

**Files:**
- Modify: `src/scheduler/policy.py`
- Test: `tests/test_scheduler.py`

- [ ] **Step 1: Add failing work-block policy tests**

Add to `tests/test_scheduler.py`:

```python
def test_low_load_office_break_allowed_inside_derived_office_work_block():
    start = datetime(2026, 6, 1, 10, 30, tzinfo=UTC)
    task = _task("office_walk", resources={"location_ids": ["office"]})
    task.duration_minutes = 10
    activity = {
        "activity_id": "office_walk",
        "activity_family_id": "b02_cardio_walking_office",
        "activity_type": "fitness",
        "title": "Short walking or movement break at office",
        "load_level": "low",
        "allowed_locations": ["office"],
        "duration_minutes": 10,
        "frequency": {"type": "as_needed"},
    }

    passed, checks = evaluate_policy(
        task,
        start,
        start + timedelta(minutes=10),
        [],
        activity=activity,
        dependency_state={
            "day_policy": {
                start.date(): {
                    "member_location": "office",
                    "core_work_blocks": [
                        {
                            "start": datetime(2026, 6, 1, 8, 30, tzinfo=UTC),
                            "end": datetime(2026, 6, 1, 18, 30, tzinfo=UTC),
                            "location_id": "office",
                            "reason_code": "core_work",
                        }
                    ],
                    "explicit_blocks": [],
                }
            }
        },
        candidate_location_id="office",
    )

    assert passed is True
    member_check = next(check for check in checks if check.name == "member_availability")
    assert "work-compatible low-load task" in member_check.reason


def test_high_load_fitness_rejected_inside_derived_work_block():
    start = datetime(2026, 6, 1, 10, 30, tzinfo=UTC)
    task = _task("strength", resources={"location_ids": ["office"]})
    task.duration_minutes = 45
    activity = {
        "activity_id": "strength",
        "activity_type": "fitness",
        "title": "Strength session",
        "load_level": "high",
        "allowed_locations": ["office"],
    }

    passed, checks = evaluate_policy(
        task,
        start,
        start + timedelta(minutes=45),
        [],
        activity=activity,
        dependency_state={
            "day_policy": {
                start.date(): {
                    "member_location": "office",
                    "core_work_blocks": [
                        {
                            "start": datetime(2026, 6, 1, 8, 30, tzinfo=UTC),
                            "end": datetime(2026, 6, 1, 18, 30, tzinfo=UTC),
                            "location_id": "office",
                            "reason_code": "core_work",
                        }
                    ],
                    "explicit_blocks": [],
                }
            }
        },
        candidate_location_id="office",
    )

    assert passed is False
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
pytest tests/test_scheduler.py::test_low_load_office_break_allowed_inside_derived_office_work_block tests/test_scheduler.py::test_high_load_fitness_rejected_inside_derived_work_block -q
```

Expected: first test fails because `evaluate_policy` ignores `day_policy`.

- [ ] **Step 3: Update `src/scheduler/policy.py`**

Add helpers near `member_availability_check`:

```python
def day_policy_member_availability_check(
    start: datetime,
    end: datetime,
    day_policy: dict[str, Any] | None,
    activity: dict[str, Any] | None,
    candidate_location_id: str | None,
    task: TaskInstance | None,
) -> ConstraintCheck | None:
    if not day_policy:
        return None
    policy = day_policy.get(start.date())
    if policy is None:
        return None
    blocks = [*policy.get("core_work_blocks", []), *policy.get("explicit_blocks", [])]
    overlapping = next(
        (
            block
            for block in blocks
            if intervals_overlap(start, end, block["start"], block["end"])
        ),
        None,
    )
    if overlapping is None:
        return ConstraintCheck(
            name="member_availability",
            passed=True,
            reason="Candidate does not overlap derived member policy blocks.",
        )
    if is_required_meal_slot(activity, task) or is_daily_medication(activity):
        return ConstraintCheck(
            name="member_availability",
            passed=True,
            reason="Required daily food/medication is allowed during compatible work blocks.",
        )
    if is_work_compatible_low_load(activity, candidate_location_id, overlapping):
        return ConstraintCheck(
            name="member_availability",
            passed=True,
            reason="Candidate overlaps work block but is a work-compatible low-load task.",
        )
    return ConstraintCheck(
        name="member_availability",
        passed=False,
        reason=f"Candidate blocked by derived {overlapping.get('reason_code', 'member_block')}.",
    )


def is_daily_medication(activity: dict[str, Any] | None) -> bool:
    activity = activity or {}
    return activity.get("activity_type") == "medication" and activity.get("frequency", {}).get("type") == "daily"


def is_work_compatible_low_load(
    activity: dict[str, Any] | None,
    candidate_location_id: str | None,
    block: dict[str, Any],
) -> bool:
    activity = activity or {}
    if activity.get("load_level") != "low":
        return False
    if candidate_location_id not in {block.get("location_id"), "remote"}:
        return False
    if activity.get("activity_type") in {"food", "medication", "consultation"}:
        return True
    return (
        activity.get("activity_type") == "fitness"
        and int(activity.get("duration_minutes") or 999) <= 15
        and activity.get("facilitator_type") in {None, "self", "member"}
    )
```

Then in `evaluate_policy`, before calling `member_availability_check`, read:

```python
day_policy_check = day_policy_member_availability_check(
    start,
    end,
    (dependency_state or {}).get("day_policy"),
    activity,
    candidate_location_id,
    task,
)
```

Use `day_policy_check` in the checks list when not `None`; otherwise keep the existing `member_availability_check`.

- [ ] **Step 4: Run tests to verify pass**

Run:

```bash
pytest tests/test_scheduler.py::test_low_load_office_break_allowed_inside_derived_office_work_block tests/test_scheduler.py::test_high_load_fitness_rejected_inside_derived_work_block -q
```

Expected: `2 passed`.

## Task 4: Add Phased Placement Inputs

**Files:**
- Modify: `src/scheduler/engine.py`
- Test: `tests/test_scheduler.py`

- [ ] **Step 1: Add failing phase-order test**

Add to `tests/test_scheduler.py`:

```python
def test_scheduler_places_daily_medication_after_same_day_breakfast():
    target_date = date(2026, 6, 1)
    breakfast = _task(
        "breakfast",
        priority=10,
        target_date=target_date,
        resources={"location_ids": ["home"]},
    )
    breakfast.duration_minutes = 20
    medication = _task(
        "supplement",
        priority=90,
        target_date=target_date,
        resources={"location_ids": ["home"]},
    )
    medication.duration_minutes = 5
    activities = {
        "breakfast": {
            "activity_id": "breakfast",
            "activity_family_id": "fam_breakfast",
            "activity_type": "food",
            "meal_slot": "breakfast",
            "title": "Breakfast",
            "load_level": "low",
            "allowed_locations": ["home"],
            "frequency": {"preferred_time_windows": ["07:00-07:30"]},
        },
        "supplement": {
            "activity_id": "supplement",
            "activity_family_id": "fam_supplement",
            "activity_type": "medication",
            "title": "Daily supplement protocol with breakfast or dinner",
            "load_level": "low",
            "allowed_locations": ["home"],
            "frequency": {"type": "daily", "preferred_time_windows": ["07:00-08:30"]},
        },
    }

    result = schedule_tasks(
        [medication, breakfast],
        activities,
        AvailabilityData(planning_start_date=target_date, planning_months=1),
    )

    rows = {row.title: row for row in result.calendar_rows}
    assert rows["Breakfast"].start_time == "07:00"
    assert rows["Daily supplement protocol with breakfast or dinner"].start_time == "07:20"
```

- [ ] **Step 2: Run test to verify failure**

Run:

```bash
pytest tests/test_scheduler.py::test_scheduler_places_daily_medication_after_same_day_breakfast -q
```

Expected: fails because medication is not anchored after same-day meal.

- [ ] **Step 3: Add phase grouping helpers in `engine.py`**

Import:

```python
from src.scheduler.classes import (
    DAILY_REQUIRED_FOOD,
    DAILY_REQUIRED_MEDICATION,
    OPPORTUNISTIC,
    ROLLING_PRIORITY,
    WEEKLY_REQUIRED_FITNESS,
    WEEKLY_SUPPORT,
    classify_activity,
)
from src.scheduler.day_policy import build_day_policies
```

Add:

```python
PHASE_ORDER = [
    ROLLING_PRIORITY,
    DAILY_REQUIRED_FOOD,
    DAILY_REQUIRED_MEDICATION,
    WEEKLY_REQUIRED_FITNESS,
    WEEKLY_SUPPORT,
    OPPORTUNISTIC,
]


def phased_task_groups(
    tasks: list[TaskInstance], activities: dict[str, dict[str, Any]]
) -> list[list[TaskInstance]]:
    groups = grouped_task_instances(tasks, activities)
    return sorted(
        groups,
        key=lambda group: (
            phase_index(classify_activity(activities.get(representative_task(group, activities).activity_id, {}))),
            task_order_key(representative_task(group, activities)),
        ),
    )


def phase_index(scheduler_class: str) -> int:
    try:
        return PHASE_ORDER.index(scheduler_class)
    except ValueError:
        return len(PHASE_ORDER)
```

In `schedule_tasks`, compute:

```python
day_policy = build_day_policies(availability)
```

Pass `day_policy` into `try_schedule_task` and then into `place_task` via dependency state.

Replace `for task_group in grouped_task_instances(...)` with:

```python
for task_group in phased_task_groups(tasks, activities):
```

- [ ] **Step 4: Add same-day meal anchor placement**

In `try_schedule_task`, before `place_task`, if activity is daily medication and title contains `breakfast or dinner`, try a meal-anchored placement:

```python
anchored = try_schedule_medication_after_meal(task, activity, plan, rows, availability, travel_time_rules, trace_source_paths)
if anchored is not None:
    return anchored
```

Add helper:

```python
def try_schedule_medication_after_meal(
    task: TaskInstance,
    activity: dict[str, Any],
    plan: PersonalizedPlan,
    rows: list[CalendarRow],
    availability: AvailabilityData,
    travel_time_rules: list[Any],
    trace_source_paths: list[str],
) -> ScheduledTask | None:
    if activity.get("activity_type") != "medication":
        return None
    if "breakfast or dinner" not in activity.get("title", "").lower():
        return None
    target_date = task.target_date
    if target_date is None:
        return None
    meal = next(
        (
            scheduled
            for scheduled in plan.tasks
            if scheduled.start.date() == target_date
            and scheduled.activity_type == "food"
            and "breakfast" in (scheduled.goal_tags or [])
        ),
        None,
    )
    if meal is None:
        meal = next(
            (
                scheduled
                for scheduled in plan.tasks
                if scheduled.start.date() == target_date
                and scheduled.activity_type == "food"
                and "dinner" in (scheduled.goal_tags or [])
            ),
            None,
        )
    if meal is None:
        return None
    start = meal.end
    end = start + timedelta(minutes=task.duration_minutes)
    scheduled = ScheduledTask(
        task_id=task.task_instance_id,
        activity_id=task.activity_id,
        activity_family_id=task.activity_family_id,
        title=activity.get("title", task.activity_id),
        start=start,
        end=end,
        activity_type=activity.get("activity_type"),
        load_level=activity.get("load_level"),
        location_id=meal.location_id,
        provider_ids=[],
        equipment_ids=[],
        trace_id=f"trace_{task.task_instance_id}",
    )
    plan.tasks.append(scheduled)
    rows.append(calendar_row_from_task(task, activity, scheduled))
    return scheduled
```

- [ ] **Step 5: Run test to verify pass**

Run:

```bash
pytest tests/test_scheduler.py::test_scheduler_places_daily_medication_after_same_day_breakfast -q
```

Expected: pass.

## Task 5: Enforce Weekly Fitness No Spillover

**Files:**
- Modify: `src/scheduler/placement.py`
- Modify: `src/scheduler/engine.py`
- Test: `tests/test_scheduler.py`

- [ ] **Step 1: Add failing no-spillover test**

Add:

```python
def test_weekly_required_fitness_does_not_spill_into_next_week():
    task = _task("cardio", target_date=date(2026, 6, 6), resources={"location_ids": ["home"]})
    task.duration_minutes = 45
    activity = {
        "activity_id": "cardio",
        "activity_type": "fitness",
        "title": "Cardio",
        "load_level": "medium",
        "allowed_locations": ["home"],
        "frequency": {"type": "weekly", "preferred_time_windows": ["07:00-08:00"]},
        "goal_contributions": [
            {
                "goal_action_id": "ga_aerobic_conditioning_weekly",
                "counts_toward_weekly_target": True,
                "value": 1,
            }
        ],
    }
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[
            AvailabilityBlock(
                resource_id="member",
                resource_type="member_blocked",
                start=datetime(2026, 6, 6, 0, tzinfo=UTC),
                end=datetime(2026, 6, 7, 23, 59, tzinfo=UTC),
                timezone="UTC",
                location_id="home",
                notes="Weekend unavailable.",
            )
        ],
    )

    result = schedule_tasks([task], {"cardio": activity}, availability)

    assert result.calendar_rows == []
    assert result.traces[0].final_status == "unscheduled"
    assert "fitness_missed_week" in result.traces[0].policy_fit_summary
    assert all(candidate["start"][:10] <= "2026-06-07" for candidate in result.traces[0].rejected_candidates)
```

- [ ] **Step 2: Run test to verify failure**

Run:

```bash
pytest tests/test_scheduler.py::test_weekly_required_fitness_does_not_spill_into_next_week -q
```

Expected: fails because current candidate drift can try later dates or lacks the required reason.

- [ ] **Step 3: Modify `candidate_dates` in `placement.py`**

Import `classify_activity` and `WEEKLY_REQUIRED_FITNESS`. In `candidate_dates`, when classifier returns `WEEKLY_REQUIRED_FITNESS`, return dates from the task's ISO week only:

```python
if activity and classify_activity(activity) == WEEKLY_REQUIRED_FITNESS and task.target_date:
    week_start = task.target_date - timedelta(days=task.target_date.weekday())
    week_end = week_start + timedelta(days=7)
    return [
        week_start + timedelta(days=offset)
        for offset in range(7)
        if horizon_start <= week_start + timedelta(days=offset) < horizon_end
    ]
```

- [ ] **Step 4: Add missed-week reason in `engine.py`**

When `place_task` returns an unscheduled trace for `WEEKLY_REQUIRED_FITNESS`, set:

```python
trace.policy_fit_summary = f"fitness_missed_week: {trace.policy_fit_summary}"
```

before appending it.

- [ ] **Step 5: Run test to verify pass**

Run:

```bash
pytest tests/test_scheduler.py::test_weekly_required_fitness_does_not_spill_into_next_week -q
```

Expected: pass.

## Task 6: Add Rolling Priority Day-by-Day Placement

**Files:**
- Modify: `src/scheduler/placement.py`
- Modify: `src/scheduler/engine.py`
- Test: `tests/test_scheduler.py`

- [ ] **Step 1: Add failing rolling-priority test**

Add:

```python
def test_rolling_priority_checkin_rolls_forward_until_provider_available():
    task = _task("care_checkin", target_date=date(2026, 6, 2), resources={"provider_ids": ["provider_1"], "location_ids": ["remote"]})
    task.activity_family_id = "b05_clinical_remote_care_team_handoff"
    task.duration_minutes = 30
    activity = {
        "activity_id": "care_checkin",
        "activity_family_id": "b05_clinical_remote_care_team_handoff",
        "activity_type": "consultation",
        "title": "Remote care-team handoff",
        "load_level": "low",
        "allowed_locations": ["remote"],
        "required_provider_ids": ["provider_1"],
        "frequency": {"type": "monthly", "preferred_time_windows": ["10:00-11:00"]},
    }
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[
            AvailabilityBlock(
                resource_id="provider_1",
                resource_type="provider",
                start=datetime(2026, 6, 4, 10, tzinfo=UTC),
                end=datetime(2026, 6, 4, 11, tzinfo=UTC),
                timezone="UTC",
                location_id="remote",
                remote_supported=True,
            )
        ],
    )

    result = schedule_tasks([task], {"care_checkin": activity}, availability)

    assert len(result.calendar_rows) == 1
    assert result.calendar_rows[0].date == date(2026, 6, 4)
```

- [ ] **Step 2: Run test to verify failure**

Run:

```bash
pytest tests/test_scheduler.py::test_rolling_priority_checkin_rolls_forward_until_provider_available -q
```

Expected: fails if current drift behavior does not classify and explain rolling placement deterministically.

- [ ] **Step 3: Modify `candidate_dates` for rolling priority**

In `placement.py`, when `classify_activity(activity) == ROLLING_PRIORITY`, return every date from `task.target_date` through horizon end:

```python
if activity and classify_activity(activity) == ROLLING_PRIORITY and task.target_date:
    current = max(task.target_date, horizon_start)
    values = []
    while current < horizon_end:
        values.append(current)
        current += timedelta(days=1)
    return values
```

- [ ] **Step 4: Add delayed trace reason**

When a rolling-priority task schedules after `task.target_date`, add to the scheduled trace summary:

```python
if classify_activity(activity) == ROLLING_PRIORITY and task.target_date and scheduled.start.date() > task.target_date:
    trace.policy_fit_summary = f"rolling_priority_delayed: scheduled on {scheduled.start.date().isoformat()} after target {task.target_date.isoformat()}."
```

- [ ] **Step 5: Run test to verify pass**

Run:

```bash
pytest tests/test_scheduler.py::test_rolling_priority_checkin_rolls_forward_until_provider_available -q
```

Expected: pass.

## Task 7: Add Demo-Level Invariants

**Files:**
- Modify: `tests/test_demo_scenarios.py`

- [ ] **Step 1: Add failing demo invariant tests**

Add:

```python
def test_latest_schedule_has_daily_medications_and_weekday_fitness_distribution():
    plan = _demo_json("03_scheduling/personalized_plan.json")
    action_plan = _demo_json("00_inputs/action_plan.json")
    availability = _demo_json("00_inputs/availability.json")
    activities = {activity["activity_id"]: activity for activity in action_plan["activities"]}

    start = date.fromisoformat(availability["planning_start_date"])
    month_index = start.month - 1 + int(availability["planning_months"])
    end = date(start.year + month_index // 12, month_index % 12 + 1, 1)

    medication_dates = {
        datetime.fromisoformat(task["start"]).date()
        for task in plan["tasks"]
        if activities[task["activity_id"]].get("activity_type") == "medication"
        and activities[task["activity_id"]].get("frequency", {}).get("type") == "daily"
    }
    expected_dates = set()
    current = start
    while current < end:
        expected_dates.add(current)
        current += timedelta(days=1)

    assert expected_dates - medication_dates == set()

    fitness_weekdays = [
        datetime.fromisoformat(task["start"]).date().weekday()
        for task in plan["tasks"]
        if activities[task["activity_id"]].get("activity_type") == "fitness"
    ]
    assert sum(1 for weekday in fitness_weekdays if weekday < 5) >= 10
```

Add:

```python
def test_latest_schedule_has_no_fitness_spillover_traces():
    traces = _demo_json("03_scheduling/decision_traces.json")

    assert not any(
        "spill" in trace.get("policy_fit_summary", "").lower()
        for trace in traces
        if trace.get("final_status") == "scheduled"
    )
```

- [ ] **Step 2: Run tests to verify current failure**

Run:

```bash
pytest tests/test_demo_scenarios.py::test_latest_schedule_has_daily_medications_and_weekday_fitness_distribution tests/test_demo_scenarios.py::test_latest_schedule_has_no_fitness_spillover_traces -q
```

Expected: medication or weekday fitness distribution test fails on current generated artifacts.

## Task 8: Rebuild Demo And Verify Suite

**Files:**
- Generated: `data/action_plan.json`
- Generated: `data/availability.json`
- Generated: `data/runs/demo-run/**`

- [ ] **Step 1: Rebuild availability if availability patterns changed**

Run:

```bash
python scripts/expand_availability.py
```

Expected: command exits 0 and prints expanded availability count.

- [ ] **Step 2: Rebuild demo run**

Run:

```bash
python scripts/build_demo_run.py
```

Expected: command exits 0 and prints scheduler/calendar row counts.

- [ ] **Step 3: Run targeted scheduler tests**

Run:

```bash
pytest tests/test_day_policy.py tests/test_scheduler_classes.py tests/test_scheduler.py::test_scheduler_places_daily_medication_after_same_day_breakfast tests/test_scheduler.py::test_weekly_required_fitness_does_not_spill_into_next_week tests/test_scheduler.py::test_rolling_priority_checkin_rolls_forward_until_provider_available -q
```

Expected: all selected tests pass.

- [ ] **Step 4: Run demo scenario tests**

Run:

```bash
pytest tests/test_demo_scenarios.py -q
```

Expected: all demo scenario tests pass.

- [ ] **Step 5: Run full suite**

Run:

```bash
pytest -q
```

Expected: all tests pass. Existing `pytest_asyncio` deprecation warning is acceptable if no test fails.

- [ ] **Step 6: Produce final artifact sanity summary**

Run:

```bash
python - <<'PY'
import json
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

root = Path("data/runs/demo-run")
plan = json.loads((root / "03_scheduling/personalized_plan.json").read_text())
calendar = json.loads((root / "04_calendar/calendar_rows.json").read_text())
availability = json.loads((root / "00_inputs/availability.json").read_text())
action_plan = json.loads((root / "00_inputs/action_plan.json").read_text())
activities = {activity["activity_id"]: activity for activity in action_plan["activities"]}

counts = Counter(row["activity_type"] for row in calendar)
fitness_weekdays = Counter(
    datetime.fromisoformat(task["start"]).strftime("%A")
    for task in plan["tasks"]
    if activities[task["activity_id"]].get("activity_type") == "fitness"
)
medication_dates = {
    datetime.fromisoformat(task["start"]).date()
    for task in plan["tasks"]
    if activities[task["activity_id"]].get("activity_type") == "medication"
    and activities[task["activity_id"]].get("frequency", {}).get("type") == "daily"
}
start = date.fromisoformat(availability["planning_start_date"])
month_index = start.month - 1 + int(availability["planning_months"])
end = date(start.year + month_index // 12, month_index % 12 + 1, 1)
expected = set()
current = start
while current < end:
    expected.add(current)
    current += timedelta(days=1)

print("calendar_rows", len(calendar))
print("activity_type_counts", dict(counts))
print("fitness_weekdays", dict(fitness_weekdays))
print("missing_daily_medications", len(expected - medication_dates))
PY
```

Expected: `missing_daily_medications 0`, plus a weekday/weekend fitness distribution suitable for the demo.

## Self-Review Checklist

- Spec coverage:
  - Daily food: Task 4 + existing meal tests + Task 7 demo invariants.
  - Daily medication: Task 4 + Task 7.
  - Weekly no-spill fitness: Task 5 + Task 7.
  - Rolling labs/care check-ins: Task 6.
  - Travel/WFH day policy: Task 1 + Task 3.
  - No new persistent fields: Task 2 uses code-side maps only.
- Placeholder scan: no TBD/TODO placeholders are used.
- Type consistency:
  - `DayPolicy` and `PolicyBlock` are defined in Task 1.
  - scheduler class constants are defined in Task 2 and imported by later tasks.
  - `day_policy` is passed through `dependency_state` as described in Task 3 and Task 4.
