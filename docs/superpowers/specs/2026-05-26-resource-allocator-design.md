# Resource Allocator Design Spec

## Assignment Context

The assignment asks for a simple implementation of a Resource Allocator for Elyx's HealthSpan AI. The allocator receives an ordered action plan of health activities and transforms it into daily, weekly, monthly, or yearly tasks while coordinating around availability of travel plans, equipment, specialists, allied health providers, and other constraints.

The required submission must include:

- Realistic sample action-plan data for at least 100 activities, in JSON or CSV.
- Realistic availability data for related resources across 3 months, in JSON or CSV.
- A scheduler that takes the action plan and availability data and outputs a personalized plan.
- A readable calendar-style output.
- A hosted internet-accessible app.
- A GitHub link and documentation of prompts used.

## Product Goal

Build a minimal submission prototype that demonstrates a robust, traceable Resource Allocator for one realistic member profile, while keeping the code modular enough to extend later to multiple profiles, richer policy logic, a database, and a more polished UI.

## Evaluation Focus

The project should be evaluated as:

```text
realistic synthetic client journey
  -> simple explainable allocator
  -> visible adaptations in the calendar and traces
```

The scheduler is intentionally simple. The differentiator is whether the synthetic data is realistic enough to create meaningful scheduling pressure, and whether the output makes adaptations inspectable.

## Non-Goals

- Do not build a polished consumer-grade UI.
- Do not implement a full optimization solver.
- Do not build multi-user authentication.
- Do not store production health data.
- Do not attempt clinical correctness beyond plausible synthetic examples.
- Do not depend on live OpenAI generation at runtime for the hosted demo.

## Recommended Stack

- Python 3.11+
- FastAPI for a small hosted app and API surface.
- Pydantic for schemas, validation, and OpenAI structured-output contracts.
- Jinja2 or simple server-rendered HTML for the readable calendar.
- Markdown rendering for prompt, handoff, and audit summaries.
- JSON as canonical data format, with optional CSV exports for reviewer convenience.
- Render or Railway for hosting.
- OpenAI API for synthetic data generation during the data pipeline step.

Python/FastAPI is preferred because the differentiating work is the traceable synthetic data pipeline and the goal-aware scheduler, not a rich frontend.

## High-Level Architecture

```text
member profile
  -> goals, preferences, constraints
  -> client packet and prompt-composed generation
  -> resource universe and independent availability
  -> OpenAI-assisted activity generation
  -> schema validation and deterministic verification
  -> canonical action plan and availability files
  -> task instances from frequency
  -> scheduler policy
  -> resource placement
  -> scheduled tasks, decision traces, calendar rows
  -> HTML calendar and JSON API
```

The system separates policy decisions from resource placement:

- Policy fit answers whether a task makes sense for a candidate day, week, journey phase, travel state, member goals, and load pattern.
- Resource fit answers whether the concrete member, provider, equipment, location, and delivery mode can support that task at that time.

This separation keeps the allocator explainable and prevents the scheduler from behaving like a generic slot filler. The first implementation should use a deliberately simple greedy scheduler with rich decision traces rather than a complex optimizer.

## Auditable Pipeline Architecture

Every data generation and scheduling run must be auditable through files and through the hosted app. The audit design should stay simple: the detailed generation artifacts remain on disk, while the UI focuses on the major handoffs a reviewer needs to understand.

Each run writes a compact numbered folder:

```text
data/runs/<run_id>/
  00_inputs/
    member_profile.json
    known_frictions.json
    resource_universe.json
    activity_families.json
    action_plan.json
    availability.json
    synthetic_data_quality_report.md
  01_validation/
    validation_report.json
    activity_board_review.md
  02_task_expansion/
    task_instances.json
    expansion_report.md
  03_scheduling/
    personalized_plan.json
    decision_traces.json
    rejection_summary.json
  04_calendar/
    calendar_rows.json
    summary_report.md
```

Generation details are still preserved under `data/generated/`:

- rendered prompts
- prompt fragment hashes
- raw OpenAI responses
- parsed batch outputs
- repair attempts
- generation manifest

The run folder is the reviewer-facing audit trail. It shows how canonical inputs become validated inputs, expanded task instances, scheduled tasks with decision traces, and final calendar rows.

The run config and UI must never expose secrets. `OPENAI_API_KEY` must not be written to run files or rendered in the audit UI.

## File Structure

```text
README.md
requirements.txt
.env.example
prompts/
  fragments/
    system_role.prompt.md
    client_profile.prompt.md
    goals_and_needs.prompt.md
    resource_universe.prompt.md
    known_frictions.prompt.md
    availability_context.prompt.md
    activity_schema.prompt.md
    realism_rules.prompt.md
    conflict_requirements.prompt.md
    batch_instructions.prompt.md
  repair.prompt.md
data/
  member_profile.json
  known_frictions.json
  resource_universe.json
  availability_patterns.json
  activity_families.json
  action_plan.json
  availability.json
  output/
    personalized_plan.json
  generated/
    manifest.json
    rendered_prompts/
    parsed/
    raw/
      activities_batch_001.json
      availability_batch_001.json
  runs/
    <run_id>/
      00_inputs/
      01_validation/
      02_task_expansion/
      03_scheduling/
      04_calendar/
src/
  app.py
  models/
    member.py
    activity.py
    availability.py
    schedule.py
    trace.py
  generation/
    openai_client.py
    prompt_compiler.py
    generate_member_profile.py
    generate_goals_and_needs.py
    generate_resource_universe.py
    generate_known_frictions.py
    generate_activities.py
    generate_availability.py
    normalize.py
    validate.py
    export_csv.py
    run_artifacts.py
  scheduler/
    task_instances.py
    policy.py
    availability.py
    placement.py
    traces.py
    engine.py
  templates/
    calendar.html
scripts/
  generate_data.py
  validate_data.py
  run_scheduler.py
  export_csv.py
tests/
  test_generation_validation.py
  test_task_instances.py
  test_scheduler_policy.py
  test_resource_placement.py
  test_scheduler_engine.py
```

## Seed File Contracts

The first runnable version uses five hand-seeded JSON files. These files are later regenerable through the OpenAI pipeline, but the hosted demo must work from committed JSON alone.

### `data/member_profile.json`

Contains one canonical member profile.

Required content:

- `member_id`
- `name`
- `timezone`
- `age_range`
- `occupation`
- `typical_work_hours`
- `goals`
- `preferences`
- `constraints`
- `baseline_metrics`
- `scheduling_rules`
- `journey_phases`
- `location_rhythm`
- `travel_windows`

The profile must include planned monthly travel and at least one last-minute travel window either directly in `travel_windows` or through linked travel windows in `resource_universe.json`.

### `data/resource_universe.json`

Defines all providers, equipment, locations, travel windows, and travel-time rules that other files may reference.

Required top-level collections:

- `providers`
- `equipment`
- `locations`
- `travel_windows`
- `travel_time_rules`

Minimum provider coverage:

- trainer
- physiotherapist
- dietitian
- physician
- phlebotomist or lab provider
- chef/cook

Minimum location coverage:

- home
- office
- gym
- clinic
- lab
- travel hotel
- remote

Travel-time rules must include at least one office-to-gym buffer, such as 15 minutes.

### `data/known_frictions.json`

Defines the intentional realistic conflicts the data and scheduler should demonstrate.

Required content:

- planned travel with better facilities, such as hotel gym access
- last-minute travel with limited facilities
- provider availability mismatch with member preferences
- lab or consultation disruption during travel
- food prep dependency requiring chef or member prep
- equipment or facility unavailability
- physical-location travel-time conflict
- skipped or substituted high-load activity requiring recovery adjustment

Each friction should have a stable ID so validation and decision traces can reference it.

### `data/activity_families.json`

Defines generated activity families. Each family contains one primary activity plus realistic substitutions when applicable.

Required family fields:

- `activity_family_id`
- `intent`
- `care_domain`
- `family_target`
- `goal_tags`
- `goal_action_ids`
- `primary_activity`
- `substitution_activities`
- `substitution_rules`
- `family_validation_notes`

The activity family is the unit of goal intent. A family defines the member need the scheduler is trying to satisfy, while the primary activity is the preferred way to satisfy it. Substitutions are alternate ways to satisfy the same need and count toward the same family-level target when scheduled.

The `family_target` object should include:

- `goal_id`
- `weekly_goal_action_id`
- `period`: `weekly` or `3_month`
- `target_units`
- `unit_label`
- `substitutions_count`
- `support_counts`

Supported first-version care domains are:

- metabolic nutrition
- cardiorespiratory fitness
- strength, mobility, and pain resilience
- recovery, sleep, and stress regulation
- clinical review and measurement

Required activity fields:

- `activity_id`
- `priority`
- `goal_tags`
- `goal_contributions`
- `activity_type`
- `title`
- `frequency`
- `duration_minutes`
- `load_level`
- `details`
- `facilitator_type`
- `required_provider_ids`
- `required_equipment_ids`
- `allowed_locations`
- `remote_allowed`
- `prep_required`
- `dependencies`
- `substitution_activity_ids`
- `skip_adjustment`
- `metrics_to_collect`
- `care_context_required`
- `share_with_provider_types`
- `raw_clinical_data_required`
- `journey_phase_applicability`
- `same_day_repeat_allowed`
- `is_primary`
- `activity_family_id`
- `substitution_for_activity_id` for substitutions
- `substitution_reason_codes` for substitutions
- `substitution_notes` or `substitution_reason` for substitutions

Each `goal_contributions` item should include:

- `weekly_goal_action_id`
- `counts_toward_weekly_target`
- `value`
- `role`
- `notes`

Each `frequency` object should include enough UI and scheduler detail to explain cadence:

- `type`
- `count`
- `preferred_days` when relevant
- `preferred_time_windows` when relevant
- `target_date` for once or due-date items

Prep dependencies should be structured, especially for food activities:

- `type`: usually `prep_task`
- `prep_duration_minutes`
- `offset_minutes_min`
- `provider_type`
- `can_be_done_by_member`
- `can_be_done_by_provider`

Count requirements after flattening:

- at least 100 scheduler-facing activities in `action_plan.json`
- enough primary families to represent realistic weekly and 3-month needs for the member profile
- substitutions counted separately and linked to families
- every activity maps to exactly one of `fitness`, `food`, `medication`, `therapy`, `consultation`

The 100+ activity requirement is a flattened action-plan requirement. It should be met by primary activities plus realistic substitutions that come from activity families, not by standalone rows with no family-level goal.

### `data/availability_patterns.json`

Defines compact, auditable 3-month availability patterns for the member and
resources. The OpenAI generation stage produces this file instead of hand-writing
every concrete block.

Required content:

- `planning_start_date`
- `planning_months`
- `patterns`

Patterns may be weekly recurrence rules or exact date ranges. They must use
concrete resource IDs from `member_profile.json` and `resource_universe.json`.

### `data/availability.json`

Defines 3 months of concrete scheduler-facing availability for the member and
resources. This file is generated deterministically from
`availability_patterns.json`.

Required content:

- `planning_start_date`
- `planning_months`
- `availability_blocks`

Each availability block includes:

- `resource_id`
- `resource_type`
- `start`
- `end`
- `timezone`
- `location_id`
- `remote_supported`
- `travel_compatible`
- `notes`

Availability must cover:

- member blocked windows
- provider availability
- chef/cook prep windows
- equipment availability where equipment is constrained
- lab availability
- clinic or facility availability
- planned travel windows
- last-minute travel windows

The expanded file should normally contain roughly 225-375 blocks for the
3-month demo. A much smaller file may parse but is not realistic enough for the
assignment. Equipment should stay compact and should not dominate the block
count. Target distribution:

- provider blocks: 120-200
- member blocked blocks: 70-100
- equipment blocks: 10-30
- location blocks: 10-40
- member travel plus travel-window blocks: 6

## Member Profile

The first version uses one canonical member profile. The schema should support more profiles later, but the submission should schedule one selected profile by default.

`MemberProfile` includes:

- `member_id`
- `name`
- `timezone`
- `age_range`
- `occupation`
- `typical_work_hours`
- `goals`
- `preferences`
- `constraints`
- `baseline_metrics`
- `scheduling_rules`
- `journey_phases`
- `location_rhythm`
- `travel_windows`

Example goals:

- Improve cardiovascular fitness.
- Reduce metabolic risk.
- Improve sleep consistency.
- Maintain strength and mobility while traveling.
- Improve supplement and medication adherence.
- Complete preventive screenings and consultations.

Example preferences and constraints:

- Prefers morning exercise.
- Accepts remote consultations.
- Avoids high-intensity activity after poor sleep.
- Has periodic work travel.
- Has occasional last-minute travel.
- Has a mild knee limitation.
- Prefers sessions under 60 minutes on weekdays.

The profile also defines the member's ordinary location rhythm, such as home in the morning and evening, office during working hours, and access to gym, clinic, lab, or remote sessions around those blocks.

`journey_phases` is a timeline, not a single label. Each phase includes:

- `phase_id`
- `phase_type`
- `start_date`
- `end_date`
- `trigger`
- `primary_goals`
- `scheduling_biases`

Supported first-version phase types are `baseline`, `travel`, `pain_escalation`, and `consolidation`. The activity board review validates that activities and priorities make sense within this timeline.

## Synthetic Journey Requirements

Based on the assignment framing, the scheduler itself can remain simple and deterministic. The differentiating work is the realism of the synthetic test data.

This prototype is designed to show that the generated dataset captures the hard parts of Elyx-style healthspan coordination:

- evolving client goals over a multi-month journey
- provider-specific availability and handoffs
- travel disrupting continuity of care
- substitutions that preserve health intent
- prep work required before activities
- resource constraints that are independent of client preference
- realistic conflicts that force the allocator to adapt
- clear traces explaining why the plan changed

The goal is not to build a globally optimal scheduler. The goal is to create a realistic synthetic client journey rich enough to reveal whether a Resource Allocator behaves sensibly.

## Activity Prescription Model

Each activity prescription represents an ordered action-plan item from HealthSpan AI. It is not yet a scheduled event.

Activity prescriptions are generated inside `ActivityFamily` objects. A family groups a primary activity with its intended substitutions, so alternatives preserve the same goal intent instead of being linked later by guesswork.

An activity family includes:

- `activity_family_id`
- `intent`
- `care_domain`
- `family_target`
- `goal_tags`
- `goal_action_ids`
- `primary_activity`
- `substitution_activities`
- `substitution_rules`
- `family_validation_notes`

The canonical generation artifact is `data/activity_families.json`. The scheduler-facing artifact is the flattened `data/action_plan.json`. Keeping both files lets the audit UI show generated intent families and the exact scheduler input.

The UI and trace drawer depend on the activity family carrying goal context. `family_target` should name the target period, target units, unit label, and whether substitutions satisfy the same target. The flattened activities keep the same family ID so the calendar can explain whether a scheduled item is the primary plan or an adaptation.

Required fields:

- `activity_id`
- `priority`
- `goal_tags`
- `goal_contributions`
- `activity_type`
- `title`
- `frequency`
- `duration_minutes`
- `load_level`
- `details`
- `facilitator_type`
- `required_provider_ids`
- `required_equipment_ids`
- `allowed_locations`
- `remote_allowed`
- `prep_required`
- `dependencies`
- `substitution_activity_ids`
- `skip_adjustment`
- `metrics_to_collect`
- `care_context_required`
- `share_with_provider_types`
- `raw_clinical_data_required`
- `journey_phase_applicability`
- `same_day_repeat_allowed`
- `is_primary`
- `activity_family_id`
- `substitution_for_activity_id` when the activity is a substitution
- `substitution_reason_codes` when the activity is a substitution
- `substitution_notes` or `substitution_reason` when helpful for trace explanation

`goal_contributions` is required for activity-board and recap views. Each contribution includes `weekly_goal_action_id`, `counts_toward_weekly_target`, `value`, `role`, and optional `notes`. A substitution that satisfies the family target should carry the same counted contribution as the primary activity.

Supported activity types:

- `fitness`
- `food`
- `medication`
- `therapy`
- `consultation`

Supported load levels:

- `low`
- `medium`
- `high`

Frequency should be explicit enough to expand into task instances, such as:

```json
{
  "type": "weekly",
  "count": 3,
  "preferred_days": ["monday", "wednesday", "saturday"],
  "preferred_time_windows": ["morning"]
}
```

For due-date or one-time work, such as labs or quarterly review, frequency should include `target_date`. The UI renders frequency labels, weekly coverage, and rejected-slot rationale from these fields.

Substitution activities must be generated in the same family as their primary activity. Example:

```json
{
  "activity_family_id": "fam_pt_knee_strength_001",
  "intent": "Maintain knee-safe lower-body strength while avoiding flare-ups during travel.",
  "goal_tags": ["knee_health", "strength", "mobility"],
  "primary_activity": {
    "activity_id": "act_021",
    "activity_type": "fitness",
    "title": "In-person knee-safe strength session with PT",
    "required_provider_ids": ["provider_pt_home_001"],
    "allowed_locations": ["clinic"],
    "remote_allowed": false
  },
  "substitution_activities": [
    {
      "activity_id": "act_022",
      "activity_type": "fitness",
      "title": "Remote PT-guided knee mobility session",
      "required_provider_ids": ["provider_pt_remote_001"],
      "allowed_locations": ["remote", "travel_hotel"],
      "remote_allowed": true
    }
  ],
  "substitution_rules": [
    {
      "when": "member_traveling_or_primary_provider_unavailable",
      "prefer_activity_id": "act_022"
    }
  ]
}
```

### Prep And Dependencies

Activities can declare dependencies the scheduler must satisfy before placement is accepted.

Dependencies support:

- food preparation before food consumption
- fasting before lab work
- lab results before physician consultation
- food before medication or supplements that require a meal
- hydration before sauna or high-load therapy
- travel-time buffers between physical locations

Food preparation is explicit. If a meal requires preparation, one of these must be true:

- a chef or cook provider can complete the prep before the meal
- the member is willing and available to prepare the food
- a valid no-prep or prepared-food substitution is selected
- the food activity is marked unscheduled with a reason

Example food prep dependency:

```json
{
  "type": "prep_task",
  "must_happen": "before",
  "offset_minutes_min": 30,
  "prep_duration_minutes": 45,
  "provider_type": "chef",
  "can_be_done_by_member": true,
  "can_be_done_by_provider": true
}
```

Prep tasks are normally scheduler-created task instances derived from dependencies, not generated activity prescriptions. They do not count toward the 100 scheduler-facing activities unless they are explicitly generated as primary food activities in `action_plan.json`, such as a recurring "batch cook lunches" activity. The synthetic-data quality report must separately count generated food-prep prescriptions and scheduler-created prep task instances.

### Care Handoff Context

Activities include lightweight care handoff metadata so provider coordination is visible without building a full clinical-record system.

Example:

```json
{
  "care_context_required": [
    "knee limitation summary",
    "recent physio recommendation",
    "current strength goal"
  ],
  "share_with_provider_types": ["trainer", "physiotherapist"],
  "raw_clinical_data_required": false
}
```

This metadata helps the scheduler and decision traces explain what context a provider needs when an activity is scheduled, substituted, or moved.

## Resource Universe Model

The resource universe defines the concrete resources that activities and availability blocks may reference. It is generated before availability and activity families, then validated before becoming canonical.

Canonical resource data is stored in:

```text
data/resource_universe.json
```

`availability.json` stores free/busy windows for those resources. The resource universe must include these entities:

### Provider

- `provider_id`
- `provider_type`
- `display_name`
- `modalities_supported`
- `location_ids`
- `remote_supported`
- `travel_compatible`
- `care_context_supported`
- `notes`

Provider types include trainer, physiotherapist, dietitian, physician, phlebotomist, therapist, coach, and chef/cook.

### Equipment

- `equipment_id`
- `equipment_type`
- `display_name`
- `location_ids`
- `travel_compatible`
- `availability_required`
- `notes`

### Location

- `location_id`
- `location_type`
- `display_name`
- `timezone`
- `travel_compatible`
- `available_equipment_ids`
- `notes`

### Travel Window

- `travel_window_id`
- `start`
- `end`
- `travel_type`
- `available_location_ids`
- `member_location_override`
- `notes`

All activity references to providers, equipment, and locations must resolve to this resource universe. Availability blocks then describe when these resources can be used.

## Availability Model

Availability data covers 3 months and includes:

- Member blocked windows.
- Travel windows and travel-compatible locations.
- Equipment availability.
- Specialist availability.
- Allied health provider availability.
- Location availability.
- Travel-time rules between simple member locations.

Each availability block includes:

- `resource_id`
- `resource_type`
- `start`
- `end`
- `timezone`
- `location_id`
- `remote_supported`
- `travel_compatible`
- `notes`

Travel is modeled as a real constraint, not just a label. During travel, in-person scheduled rows must use travel-compatible locations unless the activity explicitly allows another location.

Chef or cook support is included in the resource universe when food activities require preparation the member may not complete personally. Chef availability is independent from meal timing and member preferences. The scheduler must connect meal activities to feasible prep windows or select a realistic substitute.

Locations stay simple. The first version uses broad anchors:

- `home`
- `office`
- `gym`
- `clinic`
- `lab`
- `travel_hotel`
- `remote`

Travel time is modeled with a small matrix:

```json
{
  "from_location_id": "office",
  "to_location_id": "gym",
  "minutes": 15
}
```

The scheduler treats travel time as part of member availability. If the member is at the office until 5:00 PM and the gym is 15 minutes away, a 5:00 PM gym session is rejected and a 5:15 PM or later session can be considered. Remote activities use zero travel time.

## OpenAI-Backed Synthetic Data Pipeline

The submission should make strong use of the OpenAI API for realistic activity generation. The API should be used during offline generation, not as a required dependency for the hosted demo.

### Staged Generation Flow

Generation is staged rather than one large prompt. Generation details such as rendered prompts, raw model responses, parsed batch outputs, and repairs are written under `data/generated/`. The compact reviewer-facing run artifacts are written under `data/runs/<run_id>/`.

The generation order is:

1. Generate or curate the member profile.
2. Derive goals, care needs, constraints, location rhythm, and travel pattern.
3. Generate a resource universe needed for those care needs.
4. Generate known frictions that should exercise the allocator.
5. Generate provider, equipment, chef/cook, and facility availability independently from the member's preferences.
6. Generate an activity-family blueprint that allocates family count, goal math, meal slots, travel context, substitutions, and support-only work before full activity JSON exists.
7. Validate the blueprint against `weekly_goal_action_budget.json`.
8. Generate activity families across the five allowed modalities, constrained by the approved blueprint.
9. Flatten activity families into scheduler-facing prescriptions.
10. Validate references, realism, dependencies, conflicts, and modality coverage.
11. Repair invalid batches only when deterministic validation identifies fixable issues.
12. Write canonical scheduler-ready data.

Provider, equipment, and facility availability is an exogenous constraint. The member profile determines which resources are relevant, but not their free/busy windows. The scheduler adapts the member's plan to independently generated calendars.

### Composable Prompt Strategy

The OpenAI prompts are composed from smaller prompt fragments, not hand-written as one large prompt. `src/generation/prompt_compiler.py` renders the fragments into a full prompt for each stage and writes rendered prompts under `data/generated/rendered_prompts/`.

Prompt fragments include:

- `system_role.prompt.md`: role, output discipline, and synthetic-data boundaries.
- `client_profile.prompt.md`: member profile context.
- `goals_and_needs.prompt.md`: goals, constraints, care needs, and preferences.
- `resource_universe.prompt.md`: relevant provider, equipment, and facility expectations.
- `known_frictions.prompt.md`: realistic friction points such as travel disruption, provider mismatch, chef availability, lab timing, equipment gaps, and travel-time buffers.
- `availability_context.prompt.md`: independent availability rules.
- `activity_schema.prompt.md`: required fields and five modality categories.
- `realism_rules.prompt.md`: realistic frequency, load, metrics, and care patterns.
- `conflict_requirements.prompt.md`: required realistic conflicts and travel disruptions.
- `batch_instructions.prompt.md`: per-care-domain generation scope and diversity target.
- `05A_activity_family_blueprint.prompt.md`: whole-board semantic planning before full activity family generation.

The rendered prompt snapshot is the authoritative record of what was sent for a given OpenAI call. The prompt fragments make the generation strategy maintainable; the rendered prompt makes each run auditable.

### Schema-First Generation

All generated objects must target Pydantic schemas. The OpenAI request should use structured outputs so the model response is constrained to the expected JSON shape. Loose prompt-only JSON is not acceptable for the main pipeline.

The generation pipeline should produce:

- One realistic `MemberProfile`.
- At least 100 activity prescriptions conditioned on that profile.
- 3 months of resource availability data conditioned on the profile, travel pattern, activity needs, and provider/resource constraints.

### Prompt Files

Prompts are stored as first-class files:

- `prompts/fragments/system_role.prompt.md`
- `prompts/fragments/client_profile.prompt.md`
- `prompts/fragments/goals_and_needs.prompt.md`
- `prompts/fragments/resource_universe.prompt.md`
- `prompts/fragments/known_frictions.prompt.md`
- `prompts/fragments/availability_context.prompt.md`
- `prompts/fragments/activity_schema.prompt.md`
- `prompts/fragments/realism_rules.prompt.md`
- `prompts/fragments/conflict_requirements.prompt.md`
- `prompts/fragments/batch_instructions.prompt.md`
- `prompts/repair.prompt.md`

The README summarizes which prompt fragments were used. The rendered prompts in `data/generated/rendered_prompts/` are the authoritative prompt log for each run and are linked from `data/generated/manifest.json`.

### Run Manifest

Every generation run writes a manifest entry to `data/generated/manifest.json` with:

- generation run ID
- timestamp
- model name
- prompt fragment paths
- prompt fragment hashes
- rendered prompt path
- schema name
- request purpose
- care domain or generation batch ID
- output file path
- output file hash
- validation status
- repair attempts

### Raw And Canonical Data

Raw model outputs are saved for traceability:

```text
data/generated/raw/
```

Validated canonical files are saved as:

```text
data/member_profile.json
data/known_frictions.json
data/resource_universe.json
data/weekly_goal_action_budget.json
data/activity_family_blueprint.json
data/activity_families.json
data/action_plan.json
data/availability.json
```

The scheduler only reads canonical validated files. `activity_family_blueprint.json` preserves the approved semantic board plan. `activity_families.json` preserves generated intent and substitution grouping. `action_plan.json` is a flattened view optimized for scheduling.

### Synthetic-Data Quality Report

The pipeline writes a human-readable quality report:

```text
data/runs/<run_id>/00_inputs/synthetic_data_quality_report.md
```

This report explains why the synthetic dataset is credible enough for the assignment. It should not claim clinical validity. It should document data quality, traceability, and realism signals.

The report includes:

- member profile summary
- generation model and prompt fragment summary
- counts for activity families, flattened activities, resources, providers, locations, travel windows, and availability blocks
- modality distribution across the five required categories
- primary activity count and substitution count
- goal coverage summary
- load distribution
- frequency distribution
- substitution coverage by activity family
- known friction coverage
- travel scenario coverage, including planned and last-minute travel
- prep dependency coverage, especially for food activities
- resource-reference integrity results
- validation warnings and accepted limitations
- links or file paths to canonical inputs and generation manifest

The quality report is also visible from `/summary` and `/audit`.

### Activity Family Blueprint

Before generating full activity families, the pipeline generates `data/activity_family_blueprint.json` from `prompts/stages/05A_activity_family_blueprint.prompt.md`.

The blueprint is the semantic contract for the activity board. It defines:

- the activity families needed to generate at least 100 flattened scheduler-facing activities
- the care domain for each family
- which goal actions each family supports
- the family-level target period: weekly or 3-month
- the target units required for that period
- whether the primary and substitutions count toward that target
- estimated frequency used for weekly and 3-month goal math
- canonical food meal slots
- whether a family is core, support, prerequisite, recovery, or measurement
- substitution count and allowed substitution reason codes
- travel and adherence context without turning either into a standalone care domain or separate core denominator

`data/weekly_goal_action_budget.json` constrains the blueprint at the goal-action and care-domain level. It prevents the model from creating too many parallel cardio, strength, recovery, lab, or meal families just because the assignment needs 100+ flattened scheduler-facing activities. It should not force travel or adherence into standalone batches.

The blueprint validator fails when:

- a care domain is missing or materially underrepresented for the member's goals
- family targets do not map to a known goal action or member goal
- the flattened plan cannot plausibly reach at least 100 scheduler-facing activities
- a weekly goal action's normal-week counting estimate exceeds its cap
- structured meal coverage does not include breakfast, lunch, and dinner
- travel-context primaries count toward goals that only allow non-travel primaries
- substitutions are planned without reason codes

### Activity Family Batch Generation

Activities are generated as small care-domain batches of activity families, not standalone rows. Each batch contains the activity families listed in the approved blueprint for that care domain. Each family contains one primary activity and 0-3 substitution activities when substitutions are realistic for the intent.

The canonical `action_plan.json` must contain at least 100 scheduler-facing activity prescriptions. Primary activities and valid substitutions may both appear in the flattened file, but the synthetic-data quality report must separately count primary activities and substitutions.

Minimum count rules:

- at least 100 scheduler-facing activities in `action_plan.json`
- all scheduler-facing activities are produced by activity families
- substitutions are counted separately, linked to activity families, and count toward the same family target when scheduled
- support, prep, adherence, and reminders do not create separate top-level targets unless explicitly modeled as a real member-facing activity need

These rules prevent the dataset from meeting the assignment by inflating the count with low-value substitutions.

Each batch should target care-stream coherence across:

- activity type
- health goal
- frequency
- facilitator
- location mode
- metrics
- substitution options
- skip adjustments
- journey phase applicability
- dependencies and prep requirements

Coverage across the five activity modalities is required, but it must be justified by the member profile rather than created for variety's sake. Distribution should be realistic: food and medication tasks may be frequent, fitness may occur several times a week, therapy may be occasional, and consultations should not appear daily unless the profile gives a defensible reason.

Each activity must map to exactly one assignment category:

- `fitness`
- `food`
- `medication`
- `therapy`
- `consultation`

Batching makes retries cheap and makes generation failures easier to inspect.

Thematic batches are care-domain batches, not chronological batches. Chronology belongs to the scheduler. The five generation domains are:

- metabolic nutrition
- cardiorespiratory fitness
- strength, mobility, and pain resilience
- recovery, sleep, and stress regulation
- clinical review and measurement

Travel, adherence, medication support, prep, and provider coordination are cross-cutting context. They should appear inside the relevant care-domain families as substitutions, dependencies, support activities, metrics, or scheduling constraints. They should not become standalone generation domains.

Each family must include an `intent` so validators and reviewers can judge whether substitutions preserve the same purpose.

### Known Frictions

The pipeline generates `data/known_frictions.json` before availability and activity families. This file describes the intentional, realistic frictions the dataset should exercise.

Examples:

- office-to-gym travel requires 15 minutes
- planned monthly travel has a good hotel gym but limited lab access
- last-minute travel has no in-person PT and only basic hotel facilities
- chef is available for batch prep on limited days
- lab is only available weekday mornings
- trainer has limited evening slots despite the member preferring mornings
- sauna equipment is unavailable during a maintenance window

Known frictions are not scheduler decisions. They are scenario constraints that help generation produce useful test data and help the audit UI explain why the final calendar contains substitutions, moves, or unscheduled rows.

### Realistic Conflict Expectations

The generated dataset must include realistic conflicts that exercise the allocator:

- At least one planned monthly travel window with good facilities, such as a hotel gym.
- At least one last-minute travel window with limited facilities.
- At least one in-person provider activity that becomes remote or substituted during travel.
- At least one lab or consultation that must move because of travel.
- At least one equipment conflict.
- At least one provider availability mismatch with member preferences.
- At least one physical activity after an office block that requires travel-time buffering.
- At least one recovery or skip adjustment after a missed or substituted activity.

These conflicts should arise from plausible member context, provider calendars, locations, and travel windows. They should not be random contradictions inserted only to make the data difficult.

### Deterministic Validation

Generated data must pass deterministic validation before it becomes canonical.

Validation checks:

- At least 100 activities.
- Unique IDs.
- Required fields present.
- Valid enum values.
- Realistic frequencies.
- Every activity belongs to an activity family.
- Every activity family maps to one of the five care domains.
- Every family-level target maps to a known member goal or goal action.
- Family-level targets define a weekly or 3-month measurement period.
- No impossible durations.
- Provider and equipment references point to known resources.
- Chef or cook references point to known providers when food prep requires provider support.
- Availability covers the full 3-month planning window.
- Travel windows do not use impossible home-only locations.
- Substitution activity references point to known activities.
- Substitutions are generated in the same activity family as their primary activity.
- Substitutions share at least one goal tag with the primary activity.
- Substitutions preserve the primary activity's family-level target and count toward that target when scheduled.
- Substitutions are no harder to schedule than the primary activity under the relevant conflict scenario.
- Activity mix includes all required activity types.
- High-load fitness activities are not the majority of the plan.
- Metrics are plausible for the activity type.
- Skip adjustments are present and actionable.
- All activities map to exactly one of the five assignment categories.
- All five categories are represented with a plausible reason tied to the member profile.
- All activities are believable science-backed health, wellness, or clinical recommendations for the generated persona and high-end concierge context.
- Activities reflect realistic pain points for the profile, such as travel disruption, provider availability, food prep limits, client dinners, pain/fatigue risk, and limited recovery time.
- Consultation and lab frequencies are realistic.
- Travel-time buffers are computable for physical location changes.
- Prep dependencies are schedulable or have realistic substitutions.
- Medication activities that require food reference a food timing dependency.
- Consultations requiring lab results happen after the relevant lab activity can occur.
- The dataset includes planned monthly travel and at least one last-minute travel window.
- The dataset includes both a higher-resource travel case and a lower-resource travel case.
- The dataset includes at least one conflict or substitution opportunity for scheduler traces.

If validation fails, the pipeline should either:

- ask OpenAI to repair only the invalid batch using `prompts/repair.prompt.md`, or
- fail with a clear validation report.

### Activity Board Final Review

After all activity families are generated, flattened, and structurally validated, the pipeline runs a final whole-board review. This pass validates the activity board as a coherent health journey, not just as a collection of valid rows.

The review writes:

```text
data/runs/<run_id>/01_validation/activity_board_review.md
```

The final review checks:

- priorities are internally consistent across goals and modalities
- high-priority activities map to the member's stated primary goals
- support activities do not outrank core goal activities without a clear reason
- goal progression is plausible across the 3-month journey
- baseline, travel, pain escalation, and consolidation phase activities fit their phases
- dependencies form a valid directed graph with no impossible cycles
- food prep, lab prerequisites, medication-with-food requirements, and consultation-after-lab requirements are coherent
- substitutions preserve the primary activity's intent and reduce at least one scheduling constraint
- substitutions do not create harder dependencies than the primary activity unless explicitly justified
- load distribution supports recovery and avoids unrealistic clustering
- known frictions are actually represented in activities or scheduling constraints
- care handoff metadata is present when activities require provider coordination
- the final board has no obvious duplicated, contradictory, or clinically implausible prescriptions

This review can combine deterministic checks with an optional OpenAI critique pass over compact board summaries. If OpenAI is used, the critique prompt and response are saved under `data/generated/`, while the accepted review conclusions are summarized in `activity_board_review.md`.

### Reproducibility

The repository includes committed canonical sample data, so the hosted app works without an OpenAI key.

Developers can regenerate data with:

```bash
python scripts/generate_data.py
python scripts/validate_data.py
```

`OPENAI_API_KEY` is required only for regeneration.

## Task Instance Expansion

`src/scheduler/task_instances.py` expands prescriptions into candidate task instances across the 3-month planning window.

Responsibilities:

- Interpret family-level target periods and activity frequency definitions.
- Create target occurrence windows for primary family needs.
- Preserve activity priority and goal tags.
- Attach journey phase applicability.
- Track due dates or preferred days when present.
- Avoid creating duplicate same-day instances unless `same_day_repeat_allowed` is true.
- Create dependent prep task instances when a prescription requires scheduled preparation.
- Preserve family and substitution links from `activity_families.json`.
- Preserve whether an occurrence is required demand, scheduled support, or a substitution candidate.

Example output fields:

- `task_instance_id`
- `activity_id`
- `target_week`
- `candidate_date`
- `duration_minutes`
- `priority`
- `goal_tags`
- `required_resources`
- `dependencies`
- `activity_family_id`
- `is_substitution`
- `status`

## Scheduler Policy

`src/scheduler/policy.py` decides whether a task belongs in a candidate slot before resource placement is attempted.

### Daily Policy

- A member cannot be scheduled for two activities whose time intervals overlap.
- The same activity should not appear twice on the same day unless that activity explicitly allows same-day repeats.
- Fitness activities should not be consecutive within a day unless a large gap exists between them.
- Daily planning should avoid stacking too many medium or high load activities when lower-load days are available.
- Recovery, medication, food, and consultation activities can coexist with training, but still need a non-overlapping time window.
- Physical location changes must respect travel-time buffers. A gym activity cannot start immediately after an office block if the gym is 15 minutes away.
- Dependent prep tasks must occur before the activities they support.

### Weekly Policy

- Weekly frequency should be distributed across the week when feasible.
- A 2x/week activity should normally land on two different days, not back-to-back in the same morning.
- Higher-priority health goals receive coverage before lower-priority support activities fill the calendar.
- Substitution activities preserve the same goal intent as the primary activity and still obey spacing and load rules.

### Monthly And Journey Policy

- The calendar should show progression toward the member's goals across the journey phase.
- Supported first-version phases are:
  - `baseline`
  - `travel`
  - `pain_escalation`
  - `consolidation`
- Journey phases can bias which activities are appropriate.
- Decision traces explain why a task was moved, substituted, skipped, or escalated.

### Travel Policy

- During an active travel window, in-person scheduled rows must use travel-compatible locations such as hotel gyms, partner labs, or remote-friendly care settings.
- Remote sessions are valid during travel when the activity and facilitator support remote delivery.
- Studio, office, home, or lab locations should not be used during travel unless explicitly marked travel-compatible.
- Activities that require travel should not be scheduled outside the travel window.
- Planned travel and last-minute travel can produce different placement behavior. Planned travel may have good hotel facilities and limited in-person support; last-minute travel may force remote care or substitution activities.

## Resource Availability

`src/scheduler/availability.py` answers whether concrete resources can cover a candidate slot.

It checks:

- member availability
- provider availability
- allied health availability
- specialist availability
- equipment availability
- location availability
- remote support
- travel compatibility
- travel-time buffers between member locations
- dependency feasibility, including prep windows and prerequisite tasks

This module should not decide whether the task is healthy or appropriate for the day. It only answers resource feasibility.

## Placement Engine

`src/scheduler/placement.py` attempts to assign policy-approved task instances to concrete calendar slots.

The scheduler is deliberately simple but highly explainable. It should prefer predictable rules, deterministic ordering, and clear rejection reasons over global optimization. The goal is to demonstrate allocation reasoning, not to prove an optimal calendar.

Placement order:

1. Sort family need occurrences by priority and target period.
2. For each family occurrence, attempt the primary activity first.
3. Generate candidate slots from member preferences and availability.
4. Run scheduler policy checks.
5. Run resource availability checks.
6. Check dependency feasibility for the candidate slot, including prep windows and prerequisite tasks.
7. Provisionally reserve the candidate slot and any required prep or prerequisite slots.
8. Commit the primary activity only if all required slots can be placed without conflicts.
9. If primary placement fails, try substitutions from the same activity family according to `substitution_rules`.
10. If a substitution is scheduled, count it as satisfying the same family-level target as the primary.
11. If all substitutions fail, mark the family occurrence as unmet.
12. Emit a decision trace for scheduled, substituted, skipped, and unmet occurrences.

The first version uses a greedy algorithm. It must not claim to be globally optimal.

## Goal Attainment Reporting

The scheduler must report goal attainment across weekly and full 3-month periods. This report is derived from family-level targets, not from loose activity counts.

For each goal action and period, the report includes:

- `required_units`: target demand generated from activity-family targets
- `scheduled_primary_units`: demand satisfied by primary activities
- `scheduled_substitution_units`: demand satisfied by substitutions
- `unmet_units`: demand not satisfied by any primary or substitution
- `support_scheduled_units`: non-counting support, prep, adherence, or coordination work
- `attainment_status`: met, partially_met, unmet, or overfilled
- source family IDs, activity IDs, and trace IDs

Substitutions count toward the same target as their primary family. Support-only activities are shown separately so the report can distinguish health-goal attainment from operational support.

## Decision Traces

Every scheduled or adapted task includes a trace explaining both policy fit and resource fit.

Trace fields:

- `task_instance_id`
- `activity_id`
- `activity_family_snapshot`
- `activity_prescription_snapshot`
- `task_instance_snapshot`
- `final_status`
- `selected_slot`
- `policy_fit_summary`
- `resource_fit_summary`
- `constraint_checks`
- `rejected_candidates`
- `substitution_reason`
- `dependency_checks`
- `provider_handoff_summary`
- `skip_adjustment_applied`
- `source_artifact_paths`

Policy failures appear in `constraint_checks`, so reviewers can see why a candidate was rejected before placement tried another slot.

Example constraint check:

```json
{
  "name": "travel_location_compatibility",
  "passed": false,
  "reason": "Home gym is unavailable during active travel window; hotel gym or remote option required."
}
```

Every final calendar row links to a `trace_id`. A reviewer should be able to inspect why a task was placed, moved, substituted, skipped, or left unscheduled.

Example provider handoff summary:

```json
{
  "provider_handoff_summary": "Trainer should avoid loaded knee flexion this week due to recent PT note; use hotel-gym substitution during travel."
}
```

## Scheduler Output

The scheduler writes:

```text
data/output/personalized_plan.json
data/output/goal_attainment_report.json
```

Each scheduled calendar row includes:

- date
- start time
- end time
- activity title
- activity type
- goal tags
- load level
- facilitator or provider
- equipment
- location
- remote or in-person mode
- metrics to collect
- prep required
- substitution status
- decision trace ID

Unscheduled tasks are included with clear reasons, not silently dropped.

The goal attainment report lets reviewers make concrete statements about weekly and 3-month targets. It should answer whether each target was met by the preferred primary plan, met by substitution, partially met, or missed.

## Demo Scenarios The Calendar Must Show

The generated dataset and scheduler output should visibly demonstrate:

1. A planned travel week where in-person training becomes hotel-gym or remote training.
2. A last-minute travel window where at least one activity becomes unscheduled or substituted.
3. A lab test moved because labs are not travel-compatible.
4. A physician or dietitian consultation scheduled only after prerequisite lab results.
5. A food activity requiring prep, with chef or member prep scheduled before the meal.
6. An office-to-gym transition where a 15-minute travel buffer rejects an earlier slot.
7. A provider mismatch where the preferred trainer or PT is unavailable and another slot or substitution is used.
8. A skipped high-load activity that triggers a recovery or lower-load adjustment.

These scenarios should be visible in `/calendar`, `/summary`, and relevant decision traces.

## Calendar Readability Rule

Daily or highly repetitive activities such as medication, supplements, hydration, and recurring meals may be compacted in the HTML calendar view. The raw JSON must still include every scheduled instance, but the calendar can group recurring low-complexity tasks into readable habit blocks unless a task is substituted, skipped, moved, or creates a dependency.

Examples:

- `Daily supplement protocol, 08:00, home, Mon-Fri`
- `Prepared metabolic breakfast, weekdays, linked to chef prep block`
- `Travel-week mobility routine, daily during planned trip`

## Hosted App

The FastAPI app exposes:

- `GET /` redirects to `/calendar`.
- `GET /calendar` returns a readable 3-month calendar/list view.
- `GET /api/member` returns the member profile.
- `GET /api/action-plan` returns canonical activities.
- `GET /api/availability` returns canonical availability data.
- `GET /api/plan` returns the scheduled plan.
- `GET /api/traces/{trace_id}` returns a decision trace.
- `GET /summary` returns a reviewer-oriented run summary.
- `GET /audit` returns a simplified file-backed pipeline journey view.
- `GET /audit/stages/{stage_id}` renders one of the five compact audit stages.
- `GET /api/runs/latest` returns the latest run manifest.
- `GET /api/runs/latest/files/{stage_id}/{filename}` returns a safe view of an auditable artifact file.

The calendar page should include:

- Member summary.
- Reviewer story summary with counts for resources, activity families, flattened activities, task instances, scheduled rows, substitutions, and unscheduled rows.
- Three-month grouped schedule by week and day.
- Event rows with activity, time, location, facilitator, metrics, and substitution notes.
- Summary counts:
  - scheduled activities
  - unscheduled activities
  - substitutions
  - activity-type distribution
  - resource conflicts
  - travel-period events

The UI should be readable and functional, not decorative.

The audit page shows five compact stages: inputs, validation, task expansion, scheduling, and calendar. Each stage shows status, key counts, warnings, and links to the small set of relevant files. Markdown files are rendered for readability. JSON files are pretty-printed. Detailed prompt and raw model artifacts can be linked from the generation manifest but do not need their own UI stage. Secret-bearing environment variables must never be displayed.

## Documentation

The README should include:

- Assignment summary.
- Architecture overview.
- Setup instructions.
- How to run the data generator.
- How to validate generated data.
- How to inspect a run through `data/runs/<run_id>/`.
- How to run the scheduler.
- How to run the web app locally.
- How to use the `/audit` page.
- Deployment instructions.
- Link to the hosted app.
- Link to the GitHub repository.
- OpenAI prompt usage summary.
- Known limitations.

## Testing And Verification

The project should include focused tests around the important behavior.

Required tests:

- Generated data validates against schemas.
- Canonical data includes at least 100 activities.
- Canonical data includes family-level targets across weekly and 3-month periods.
- Activity IDs are unique.
- Activity families include primary activities, substitutions, and substitution rules.
- Activity families map to one of the five care domains and to member goals.
- Substitutions share the family intent and at least one goal tag with the primary activity.
- Substitutions count toward the same family-level target when scheduled.
- Frequencies expand into expected task instances.
- Food prep dependencies create feasible prep tasks or realistic substitutions.
- Same activity is not scheduled twice in one day unless allowed.
- Member events do not overlap.
- Physical location changes respect travel-time buffers.
- Travel windows reject non-travel-compatible in-person locations.
- Remote activities can be scheduled during travel when allowed.
- Planned and last-minute travel produce different valid scheduling behavior.
- Higher-priority activities are placed before lower-priority activities.
- Unscheduled tasks include reasons.
- Decision traces include both policy and resource checks.
- Goal attainment reports distinguish required, primary-scheduled, substitution-scheduled, support-scheduled, and unmet units.
- Demo scenarios are represented in calendar rows and traces.
- Calendar HTML compacts repetitive low-complexity tasks while JSON preserves every instance.
- Audit run folders include required stage artifacts.
- Synthetic-data quality report includes modality, goal, substitution, friction, travel, prep, and validation summaries.

Manual verification:

- Run data validation.
- Review `activity_board_review.md` for board-level consistency.
- Run scheduler.
- Open `/calendar`.
- Confirm the calendar shows 3 months of readable events.
- Confirm `/api/plan` returns JSON.
- Confirm traces exist for substituted or unscheduled tasks.
- Open `/summary` and confirm the synthetic-data quality report and reviewer counts are visible.
- Open `/audit` and confirm the five compact stages show their files, including the validation report and activity board review.

## Deployment

The submission should deploy the FastAPI app to Render or Railway.

The deployed app should use committed canonical data files so it does not require `OPENAI_API_KEY` at runtime.

Environment variables:

- `OPENAI_API_KEY`: required only for data regeneration.
- `PLANNING_START_DATE`: optional override for schedule generation.
- `PLANNING_MONTHS`: defaults to `3`.

## Acceptance Criteria

The assignment is complete when:

- The repo contains one member profile.
- The repo contains at least 100 validated activities.
- The repo contains 3 months of realistic availability data.
- The OpenAI-backed generation pipeline is documented and runnable.
- Prompt fragments are committed under `prompts/fragments/`.
- Rendered prompts are saved under `data/generated/`.
- Generation manifest records traceability metadata.
- Run folders use the compact `00_inputs` through `04_calendar` audit structure.
- A synthetic-data quality report is generated and visible in the UI.
- A final activity board review validates priorities, goal progression, dependencies, substitutions, and journey logic.
- The repo contains `resource_universe.json`, `activity_families.json`, `known_frictions.json`, and flattened `action_plan.json`.
- `action_plan.json` contains at least 100 scheduler-facing activities produced by activity families.
- The scheduler outputs a personalized 3-month plan.
- The scheduler outputs weekly and 3-month goal attainment summaries.
- The scheduler includes policy checks before resource placement.
- The scheduler respects travel-time buffers between simple locations.
- The scheduler respects prep dependencies for food and other prerequisite activities.
- Scheduled and unscheduled tasks include decision traces.
- The hosted app includes a readable simplified `/audit` view of auditable files.
- The calendar page is readable.
- The app is hosted online.
- The README includes setup, deployment, GitHub, and prompts-used details.

## Implementation Phases

Implementation should proceed in phases so the first successful build runs from committed data without any OpenAI call:

1. Schemas and committed sample data.
2. Validator and synthetic-data quality report.
3. Task expansion.
4. Simple scheduler and decision traces.
5. Calendar, summary, audit UI, and API.
6. OpenAI regeneration pipeline.
7. Tests and deployment polish.

## Future Extensions

- Multiple member profiles.
- Richer journey progression.
- Database-backed persistence.
- Interactive calendar UI.
- Admin view for provider and equipment schedules.
- Optimization-based placement.
- Automated quality scoring for generated synthetic data.
- Export to Google Calendar or ICS.
