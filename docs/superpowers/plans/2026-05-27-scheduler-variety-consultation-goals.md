# Scheduler Variety Consultation Goals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the overlapping travel-continuity goal, make meal substitutions appear as planned variety, and schedule enough consultations for the Elyx reviewer demo.

**Architecture:** Keep the 50-family activity board and generated batch structure, but repair active data contracts and scheduler policy. Add explicit goal actions for care-team follow-through and behavior coaching, then teach scheduling to select planned-variety substitutions before primaries when weekly variety/cap rules require it.

**Tech Stack:** Python, Pydantic models, FastAPI demo app, JSON data artifacts, pytest.

---

## File Structure

- Modify `data/member_profile.json`: remove `ga_travel_continuity_3month`; add `ga_care_team_followthrough_3month` and `ga_behavior_coaching_weekly`.
- Modify `data/goal_action_budget.json`: mirror the new goal-action taxonomy for generation/validation docs.
- Modify `data/activity_family_blueprint.json`: replace travel-continuity goal references with the new categories where appropriate.
- Modify `data/generated/stage05_activity_families/batches/*.json`: update existing generated families and activities in-place.
- Modify `data/activity_families.json` and `data/action_plan.json`: active source data consumed by scheduler and app.
- Modify `src/scheduler/engine.py`: add planned-variety substitution selection and keep goal reporting aligned with new categories.
- Modify `src/scheduler/task_instances.py`: expand planned-variety substitutions even when their original frequency has `count: 0`, when linked to a primary family occurrence.
- Modify `src/generation/validate.py`: reject active travel-continuity goal references and require the two replacement goal actions.
- Modify `scripts/repair_stage05_first_run.py`: keep the reproducible repair script aligned with new goal IDs and planned-variety metadata.
- Modify `docs/elyx_assignment_dataset_generation.md`: document the taxonomy replacement and scheduling policy.
- Test `tests/test_scheduler.py`: planned variety, consultation scheduling, and goal-report behavior.
- Test `tests/test_validation.py`: active data taxonomy checks.
- Test `tests/test_demo_scenarios.py`: final demo includes meal variety and consultation count.

## Task 1: Add Taxonomy Validation Tests

**Files:**
- Modify: `tests/test_validation.py`

- [ ] **Step 1: Add failing taxonomy test**

Add this test near the other validation/data contract tests:

```python
def test_active_goal_taxonomy_replaces_travel_continuity(load_seed):
    profile = load_seed("member_profile.json")
    action_ids = {action["goal_action_id"] for action in profile["goal_actions"]}

    assert "ga_travel_continuity_3month" not in action_ids
    assert "ga_care_team_followthrough_3month" in action_ids
    assert "ga_behavior_coaching_weekly" in action_ids
```

- [ ] **Step 2: Add failing active data reference test**

Add:

```python
def test_active_activities_do_not_reference_travel_continuity(load_seed):
    activity_families = load_seed("activity_families.json")["activity_families"]
    action_plan = load_seed("action_plan.json")["activities"]

    family_refs = {
        goal_action_id
        for family in activity_families
        for goal_action_id in family.get("goal_action_ids", [])
    }
    activity_refs = {
        contribution.get("goal_action_id")
        for activity in action_plan
        for contribution in activity.get("goal_contributions", [])
        if contribution.get("goal_action_id")
    }

    assert "ga_travel_continuity_3month" not in family_refs
    assert "ga_travel_continuity_3month" not in activity_refs
```

- [ ] **Step 3: Run test to verify failure**

Run:

```bash
pytest tests/test_validation.py::test_active_goal_taxonomy_replaces_travel_continuity tests/test_validation.py::test_active_activities_do_not_reference_travel_continuity -q
```

Expected: both tests fail because active data still includes `ga_travel_continuity_3month`.

## Task 2: Replace Goal Taxonomy In Active Data

**Files:**
- Modify: `data/member_profile.json`
- Modify: `data/goal_action_budget.json`
- Modify: `data/activity_family_blueprint.json`
- Modify: `data/generated/stage05_activity_families/batches/*.json`
- Modify: `data/activity_families.json`
- Modify: `data/action_plan.json`

- [ ] **Step 1: Replace `ga_travel_continuity_3month` in `member_profile.json`**

Remove the `Maintain travel continuity adaptations` goal action. Add:

```json
{
  "goal_action_id": "ga_care_team_followthrough_3month",
  "goal_id": "goal_adherence_and_careteam",
  "label": "Complete care-team review and decision follow-through",
  "role": "care_team",
  "target": {
    "period": "3_month",
    "units": 6,
    "unit_label": "touchpoints"
  },
  "activity_types": ["consultation"],
  "substitutions_allowed": true,
  "counts_substitutions": true,
  "support_only": false,
  "notes": "Counts physician, dietitian, physio, remote care-team handoff, plan-adjustment review, and lab-result follow-up touchpoints. Passive logs and reminders do not count."
}
```

and:

```json
{
  "goal_action_id": "ga_behavior_coaching_weekly",
  "goal_id": "goal_adherence_and_careteam",
  "label": "Complete behavior coaching and friction-resolution touchpoints",
  "role": "coaching",
  "target": {
    "period": "weekly",
    "units": 1,
    "unit_label": "touchpoints"
  },
  "activity_types": ["consultation"],
  "substitutions_allowed": true,
  "counts_substitutions": true,
  "support_only": false,
  "notes": "Counts member-facing coaching, adherence barrier review, travel friction planning, post-missed-session coaching, and meal-prep failure resolution. Daily supplement-taking does not count."
}
```

- [ ] **Step 2: Update generated and flattened activity references**

Use structured JSON editing, not text replacement, to map references:

- Travel meal/fitness/recovery activities that currently reference `ga_travel_continuity_3month` should drop that contribution if they already contribute to the underlying meal, fitness, strength, or recovery goal.
- Remote coach check-ins, adherence check-ins, and friction-resolution activities should reference `ga_behavior_coaching_weekly`.
- Remote care-team handoffs, dietitian lab follow-ups, physio reassessments, and plan-adjustment consults should reference `ga_care_team_followthrough_3month`.

Preserve each activity's original care domain and family.

- [ ] **Step 3: Update family targets**

For affected families:

- set `family_target.goal_action_id` to `ga_behavior_coaching_weekly` for coaching/friction families
- set `family_target.goal_action_id` to `ga_care_team_followthrough_3month` for care-team handoff/review families
- keep travel meals under `ga_structured_meals_weekly`
- keep travel exercise under aerobic, strength, or recovery goals

- [ ] **Step 4: Run validation tests**

Run:

```bash
pytest tests/test_validation.py::test_active_goal_taxonomy_replaces_travel_continuity tests/test_validation.py::test_active_activities_do_not_reference_travel_continuity -q
```

Expected: pass.

## Task 3: Make Meal Substitutions Expand For Planned Variety

**Files:**
- Modify: `data/generated/stage05_activity_families/batches/batch_001_metabolic_nutrition.json`
- Modify: `data/activity_families.json`
- Modify: `data/action_plan.json`
- Modify: `src/scheduler/task_instances.py`
- Test: `tests/test_task_instances.py`

- [ ] **Step 1: Add failing task expansion test**

Add to `tests/test_task_instances.py`:

```python
def test_expands_planned_variety_substitution_from_primary_frequency():
    availability = AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1)
    action_plan = {
        "activities": [
            {
                "activity_id": "meal_primary",
                "activity_family_id": "fam_meal",
                "is_primary": True,
                "duration_minutes": 30,
                "priority": 10,
                "goal_tags": ["nutrition"],
                "required_provider_ids": [],
                "required_equipment_ids": [],
                "allowed_locations": ["home"],
                "dependencies": [],
                "frequency": {
                    "type": "weekly",
                    "count": 2,
                    "preferred_days": ["monday", "tuesday"],
                },
            },
            {
                "activity_id": "meal_restaurant",
                "activity_family_id": "fam_meal",
                "is_primary": False,
                "substitution_for_activity_id": "meal_primary",
                "variety_role": "planned_variety",
                "duration_minutes": 30,
                "priority": 11,
                "goal_tags": ["nutrition"],
                "required_provider_ids": [],
                "required_equipment_ids": [],
                "allowed_locations": ["restaurant"],
                "dependencies": [],
                "frequency": {"type": "as_needed", "count": 0},
            },
        ]
    }

    tasks = expand_primary_activities(action_plan, availability)

    assert sum(1 for task in tasks if task.activity_id == "meal_primary") == 5
    assert sum(1 for task in tasks if task.activity_id == "meal_restaurant") == 5
```

- [ ] **Step 2: Run test to verify failure**

Run:

```bash
pytest tests/test_task_instances.py::test_expands_planned_variety_substitution_from_primary_frequency -q
```

Expected: fail because `as_needed` substitutions do not expand.

- [ ] **Step 3: Implement expansion rule**

In `src/scheduler/task_instances.py`, build a primary frequency map before expansion. For substitution activities with `variety_role == "planned_variety"` and `substitution_for_activity_id`, use the referenced primary activity frequency when the substitution's own frequency would expand to no dates.

- [ ] **Step 4: Mark meal substitutions as planned variety**

Add `variety_role: "planned_variety"` to:

- `act_b01_breakfast_home_lowprep`
- `act_b01_lunch_office_member_assembled`
- `act_b01_dinner_home_restaurant`
- relevant travel meal substitutions that preserve structured-meal intent

Add `weekly_variety_min: 1` where appropriate.

- [ ] **Step 5: Run expansion test**

Run:

```bash
pytest tests/test_task_instances.py::test_expands_planned_variety_substitution_from_primary_frequency -q
```

Expected: pass.

## Task 4: Add Planned Variety Scheduler Policy

**Files:**
- Modify: `src/scheduler/engine.py`
- Test: `tests/test_scheduler.py`

- [ ] **Step 1: Add failing scheduler test for primary cap**

Add to `tests/test_scheduler.py`:

```python
def test_scheduler_uses_planned_variety_after_primary_weekly_cap():
    availability = AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1)
    primary = {
        "activity_id": "chef_meal",
        "activity_type": "food",
        "meal_slot": "dinner",
        "title": "Chef meal",
        "load_level": "low",
        "allowed_locations": ["home"],
        "weekly_primary_cap": 1,
        "goal_contributions": [{"goal_action_id": "ga_meals", "counts_toward_weekly_target": True, "value": 1}],
    }
    restaurant = {
        "activity_id": "restaurant_meal",
        "activity_type": "food",
        "meal_slot": "dinner",
        "title": "Restaurant meal",
        "load_level": "low",
        "allowed_locations": ["restaurant"],
        "substitution_for_activity_id": "chef_meal",
        "variety_role": "planned_variety",
        "goal_contributions": [{"goal_action_id": "ga_meals", "counts_toward_weekly_target": True, "value": 1}],
    }
    tasks = [
        _task("chef_meal", target_date=date(2026, 6, 1)),
        _task("restaurant_meal", target_date=date(2026, 6, 1)),
        _task("chef_meal", target_date=date(2026, 6, 2)),
        _task("restaurant_meal", target_date=date(2026, 6, 2)),
    ]
    for task in tasks:
        task.activity_family_id = "fam_meal"
        task.duration_minutes = 30
        task.required_resources = {"location_ids": ["home" if task.activity_id == "chef_meal" else "restaurant"]}
        task.is_substitution = task.activity_id == "restaurant_meal"

    result = schedule_tasks(
        tasks,
        {"chef_meal": primary, "restaurant_meal": restaurant},
        availability,
        goal_actions=[{"goal_action_id": "ga_meals", "target": {"period": "weekly", "units": 14}}],
    )

    scheduled_ids = [task.activity_id for task in result.plan.tasks]
    assert scheduled_ids == ["chef_meal", "restaurant_meal"]
```

- [ ] **Step 2: Run test to verify failure**

Run:

```bash
pytest tests/test_scheduler.py::test_scheduler_uses_planned_variety_after_primary_weekly_cap -q
```

Expected: fail because scheduler always schedules the primary when possible.

- [ ] **Step 3: Implement weekly primary cap and planned-variety preference**

In `src/scheduler/engine.py`, track scheduled primary counts by `(activity_family_id, week_id)`. Before ordering a family occurrence, if the primary activity has `weekly_primary_cap` and the cap is already met, order planned-variety substitutions before the primary.

- [ ] **Step 4: Add trace reason**

When a planned-variety substitution is selected due to cap or variety policy, set `trace.substitution_reason` to:

```text
Substitution used for planned variety after primary weekly cap was met.
```

- [ ] **Step 5: Run scheduler test**

Run:

```bash
pytest tests/test_scheduler.py::test_scheduler_uses_planned_variety_after_primary_weekly_cap -q
```

Expected: pass.

## Task 5: Raise Consultation Scheduling

**Files:**
- Modify: `data/generated/stage05_activity_families/batches/batch_005_clinical_review_measurement.json`
- Modify: `data/activity_families.json`
- Modify: `data/action_plan.json`
- Modify: `src/scheduler/placement.py`
- Modify: `src/scheduler/engine.py`
- Test: `tests/test_demo_scenarios.py`

- [ ] **Step 1: Add demo assertion for consultation count**

Add to `tests/test_demo_scenarios.py`:

```python
def test_latest_calendar_has_high_touch_consultations(data_dir):
    rows = json.loads((data_dir / "runs/demo-run/04_calendar/calendar_rows.json").read_text())
    consultations = [row for row in rows if row["activity_type"] == "consultation"]

    assert len(consultations) >= 10
```

- [ ] **Step 2: Make clinical/coaching consultations schedulable**

Update B05 consultation activities so:

- behavior coaching activities use `ga_behavior_coaching_weekly`
- care-team follow-through activities use `ga_care_team_followthrough_3month`
- member-facing consultation supports are not marked support-only if they should count
- monthly and weekly consultation frequencies have feasible preferred windows, including remote evening windows
- core clinical due-week activities have priority higher than recurring meals/supplements

- [ ] **Step 3: Improve consultation candidate times**

In `src/scheduler/placement.py`, ensure remote consultations can use evening preferred windows and provider availability starts. Keep the existing `candidate_times` pattern, but verify it does not discard provider availability because it falls outside an overly narrow preferred window.

- [ ] **Step 4: Rebuild demo run**

Run:

```bash
python scripts/build_demo_run.py
```

Expected: validation pass and calendar rows regenerated.

- [ ] **Step 5: Run demo test**

Run:

```bash
pytest tests/test_demo_scenarios.py::test_latest_calendar_has_high_touch_consultations -q
```

Expected: pass with at least 10 consultation rows.

## Task 6: Verify End-To-End Reviewer Output

**Files:**
- Modify: `docs/elyx_assignment_dataset_generation.md`

- [ ] **Step 1: Run canonical validation**

Run:

```bash
python scripts/validate_data.py
```

Expected:

```text
Validation pass: 100 activities, 50 primary
```

- [ ] **Step 2: Run full test suite**

Run:

```bash
pytest -q
```

Expected: all tests pass.

- [ ] **Step 3: Inspect final calendar summary**

Run:

```bash
sed -n '1,120p' data/runs/demo-run/04_calendar/summary_report.md
```

Expected:

- consultation rows are at least 10
- food rows include chef-prepped, restaurant, and member-prepped/low-prep activities
- scheduled rows are plausible for the 3-month horizon

- [ ] **Step 4: Inspect goal report**

Run:

```bash
jq '.goal_report.summary' data/runs/demo-run/03_scheduling/personalized_plan.json
```

Expected: output includes weekly and three-month status with the new categories.

- [ ] **Step 5: Update reviewer documentation**

Update `docs/elyx_assignment_dataset_generation.md` to mention:

- travel-continuity goal was removed
- care-team follow-through and behavior coaching were added
- planner now supports planned variety substitutions
- consultation scheduling policy was raised for Elyx high-touch realism

## Self-Review

- Spec coverage: taxonomy replacement, meal variety, consultation scheduling, availability semantics, validation, and reviewer documentation are covered.
- Placeholder scan: no placeholders or deferred "TBD" items remain.
- Type consistency: all referenced keys already fit the flexible activity JSON model or are new metadata keys consumed by scheduler policy.
