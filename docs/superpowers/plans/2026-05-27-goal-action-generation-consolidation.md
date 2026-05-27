# Goal Action Generation Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate generated activity data around family-level weekly and 3-month goal targets, five care domains, and UI-required metadata before rerunning Stage 05 generation.

**Architecture:** Keep stages 01-04 as the current baseline. Add period-aware `goal_actions` while preserving legacy `weekly_goal_actions` reads, then migrate Stage 05 prompt assembly, validators, and UI recap helpers to the shared goal-action interface. Stage 05 should generate activity families in five care-domain batches and flatten them into `action_plan.json`.

**Tech Stack:** Python 3, Pydantic models, FastAPI/Jinja UI helpers, pytest, JSON prompt/data artifacts.

---

### Task 1: Goal Action Compatibility Model

**Files:**
- Modify: `src/models/member.py`
- Modify: `src/calendar_interface.py`
- Test: `tests/test_models.py`
- Test: `tests/test_calendar_interface.py`

- [ ] **Step 1: Write failing model tests**

Add tests that validate both legacy and new goal action shapes:

```python
def test_member_profile_accepts_period_aware_goal_actions(load_seed):
    payload = load_seed("member_profile.json")
    payload["goal_actions"] = [
        {
            "goal_action_id": "ga_structured_meals_001",
            "goal_id": "goal_metabolic_health",
            "label": "Complete structured metabolic meals",
            "role": "core",
            "target": {"period": "weekly", "units": 14, "unit_label": "meals"},
            "activity_types": ["food"],
            "substitutions_allowed": True,
            "counts_substitutions": True,
            "support_only": False,
        },
        {
            "goal_action_id": "ga_three_month_review_001",
            "goal_id": "goal_adherence_and_careteam",
            "label": "Complete 3-month clinical review package",
            "role": "measurement",
            "target": {"period": "3_month", "units": 1, "unit_label": "review package"},
            "activity_types": ["consultation"],
            "substitutions_allowed": True,
            "counts_substitutions": True,
            "support_only": False,
        },
    ]

    profile = MemberProfile.model_validate(payload)

    assert profile.goal_actions[0].goal_action_id == "ga_structured_meals_001"
    assert profile.goal_actions[0].target.period == "weekly"
    assert profile.goal_actions[1].target.period == "3_month"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_models.py::test_member_profile_accepts_period_aware_goal_actions -q`

Expected: fail because `goal_actions` and target model do not exist yet.

- [ ] **Step 3: Implement minimal model support**

In `src/models/member.py`, add `GoalActionTarget`, `GoalAction`, and `goal_actions` to `MemberProfile`. Keep `WeeklyGoalAction` unchanged for compatibility.

- [ ] **Step 4: Add helper tests for normalized goal actions**

Add a test in `tests/test_calendar_interface.py` for a helper that accepts legacy `weekly_goal_actions` and returns normalized records with `goal_action_id`, `period`, and `target_units`.

- [ ] **Step 5: Implement normalized goal action helper**

In `src/calendar_interface.py`, add a small helper that converts either:

```python
{"weekly_goal_action_id": "wga_x", "target_per_week": 2}
```

or:

```python
{"goal_action_id": "ga_x", "target": {"period": "weekly", "units": 2}}
```

into a common internal dictionary.

- [ ] **Step 6: Verify**

Run: `pytest tests/test_models.py tests/test_calendar_interface.py -q`

Expected: all selected tests pass.

### Task 2: Period-Aware Goal Recap

**Files:**
- Modify: `src/calendar_interface.py`
- Test: `tests/test_calendar_interface.py`

- [ ] **Step 1: Write failing recap test**

Add a test that builds calendar rows and activities for one weekly action and one 3-month action, then asserts the recap targets are not both multiplied by week count.

```python
def test_three_month_recap_handles_weekly_and_three_month_goal_actions():
    member_profile = {
        "goals": [{"goal_id": "goal_metabolic_health", "name": "Improve metabolic health", "priority": 1}],
        "goal_actions": [
            {
                "goal_action_id": "ga_cardio_weekly",
                "goal_id": "goal_metabolic_health",
                "label": "Complete cardio",
                "target": {"period": "weekly", "units": 2, "unit_label": "sessions"},
                "support_only": False,
            },
            {
                "goal_action_id": "ga_clinical_review",
                "goal_id": "goal_metabolic_health",
                "label": "Complete clinical review package",
                "target": {"period": "3_month", "units": 1, "unit_label": "package"},
                "support_only": False,
            },
        ],
        "scheduling_rules": {"planning_start_date": "2026-06-01", "planning_months": 3},
    }
    activities = {
        "act_cardio": {
            "activity_id": "act_cardio",
            "goal_contributions": [{"goal_action_id": "ga_cardio_weekly", "value": 1}],
        },
        "act_review": {
            "activity_id": "act_review",
            "goal_contributions": [{"goal_action_id": "ga_clinical_review", "value": 1}],
        },
    }

    rows = recap_action_rows(
        calendar_rows=[
            {"calendar_row_id": "row_task_cardio", "date": "2026-06-01", "title": "Cardio"},
            {"calendar_row_id": "row_task_review", "date": "2026-06-08", "title": "Review"},
        ],
        traces=[],
        plan_tasks={
            "task_cardio": {"activity_id": "act_cardio"},
            "task_review": {"activity_id": "act_review"},
        },
        activities=activities,
        weekly_actions=member_profile["goal_actions"],
        horizon_weeks=13,
    )

    targets = {row["goal_action_id"]: row["horizon_target"] for row in rows}
    assert targets["ga_cardio_weekly"] == 26
    assert targets["ga_clinical_review"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_calendar_interface.py::test_three_month_recap_handles_weekly_and_three_month_goal_actions -q`

Expected: fail because existing recap assumes `target_per_week`.

- [ ] **Step 3: Implement period-aware recap**

Update `recap_action_rows`, `weekly_goal_action_summary`, and goal-card payload generation to use normalized goal actions. Weekly target multiplies by `horizon_weeks`; `3_month` target uses units directly.

- [ ] **Step 4: Verify**

Run: `pytest tests/test_calendar_interface.py -q`

Expected: pass.

### Task 3: Activity Family Target Validation

**Files:**
- Modify: `src/generation/validate.py`
- Modify: `src/generation/activity_blueprint.py`
- Test: `tests/test_validation.py`
- Test: `tests/test_activity_blueprint.py`

- [ ] **Step 1: Write failing validation tests**

Add tests that fail when an activity family lacks `care_domain`, lacks `family_target`, or has a substitution with a different counted goal contribution from the primary.

- [ ] **Step 2: Run tests to verify red**

Run: `pytest tests/test_validation.py::test_validation_rejects_family_without_target tests/test_validation.py::test_validation_rejects_substitution_that_does_not_count_toward_family_target -q`

Expected: fail because validation does not check these yet.

- [ ] **Step 3: Implement validation**

Add deterministic checks:

- valid `care_domain` in the five care domains
- `family_target.period` in `weekly`, `3_month`
- family target references a known `goal_action_id` or legacy `weekly_goal_action_id`
- substitutions that count must reference the same action ID as the primary/family target
- every flattened activity has `activity_family_id`

- [ ] **Step 4: Verify**

Run: `pytest tests/test_validation.py tests/test_activity_blueprint.py -q`

Expected: pass.

### Task 4: Five Care-Domain Prompt Assembly

**Files:**
- Modify: `scripts/assemble_prompts.py`
- Modify: `prompts/stages/05A_activity_family_blueprint.prompt.md`
- Modify: `prompts/stages/05_activity_family_batch.prompt.md`
- Modify: `prompts/fragments/activity_schema.prompt.md`
- Test: `tests/test_activity_blueprint.py`

- [ ] **Step 1: Write failing prompt assembly test**

Update the prompt assembly test to assert that assembled Stage 05 prompts use exactly five care-domain batch files and do not include standalone travel/adherence batch names.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_activity_blueprint.py::test_assemble_prompts_writes_blueprint_prompt_and_batch_budget -q`

Expected: fail until `BATCHES` is updated.

- [ ] **Step 3: Update `BATCHES`**

Replace the 8-batch list with five care domains:

- `001_metabolic_nutrition`
- `002_cardiorespiratory_fitness`
- `003_strength_mobility_pain`
- `004_recovery_sleep_stress`
- `005_clinical_review_measurement`

- [ ] **Step 4: Update prompt text**

Require `care_domain`, `family_target`, `goal_contributions`, prep dependency fields, substitution reason fields, and UI/audit metadata.

- [ ] **Step 5: Verify**

Run: `python scripts/assemble_prompts.py` then `pytest tests/test_activity_blueprint.py -q`

Expected: assembled prompts contain five care-domain files and tests pass.

### Task 5: Regeneration Readiness Check

**Files:**
- Modify: `scripts/generate_stage05_activity_batches.py`
- Modify: `scripts/generate_stage05_blueprint.py`
- Test: `tests/test_pipeline_story.py`

- [ ] **Step 1: Write failing tests for batch discovery**

Update pipeline-story expectations so Stage 05 source files are selected by current five care-domain batch IDs rather than historical 8-batch names.

- [ ] **Step 2: Run tests to verify red**

Run: `pytest tests/test_pipeline_story.py -q`

Expected: fail until batch selection and generated-file expectations match the new convention.

- [ ] **Step 3: Update scripts for five-domain batch IDs**

Ensure merge/accepted-batch logic uses the same `BATCHES` constant and does not expect old batch IDs.

- [ ] **Step 4: Verify without OpenAI**

Run:

```bash
python scripts/assemble_prompts.py
pytest tests/test_pipeline_story.py tests/test_activity_blueprint.py tests/test_validation.py tests/test_calendar_interface.py tests/test_models.py -q
```

Expected: pass before any API generation.

### Task 6: Stage 05 Generation Gate

**Files:**
- No production edits unless prior tasks pass.

- [ ] **Step 1: Confirm tests are green**

Run: `pytest -q`

Expected: all tests pass or only failures tied to intentionally missing generated data are documented.

- [ ] **Step 2: Generate blueprint**

Run:

```bash
python scripts/generate_stage05_blueprint.py --suffix care_domains_20260527 --accept-valid
```

Expected: valid `data/activity_family_blueprint.json`.

- [ ] **Step 3: Generate activity-family batches**

Run:

```bash
python scripts/generate_stage05_activity_batches.py --suffix care_domains_20260527 --merge
```

Expected: accepted five-domain batches, refreshed `data/activity_families.json`, and refreshed `data/action_plan.json`.

- [ ] **Step 4: Validate and rebuild demo run**

Run:

```bash
python scripts/build_demo_run.py
pytest -q
```

Expected: validation passes, `data/runs/demo-run/00_inputs` exists, and tests pass.

---

## Self-Review

- Spec coverage: Covers period-aware goals, family-level targets, five care domains, UI-required fields, validators, prompt assembly, and generation gate.
- Placeholder scan: No placeholder tasks; generation only happens after local tests and prompt assembly pass.
- Type consistency: New canonical names are `goal_actions`, `goal_action_id`, and `target.period/units`, with legacy `weekly_goal_actions` compatibility.
