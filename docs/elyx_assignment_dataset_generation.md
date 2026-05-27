# Elyx Assignment Dataset Generation Process

Audience: Elyx reviewers evaluating the resource allocator assignment dataset.

This document explains how the assignment dataset was generated, why the generation
was staged, what was corrected during generation, and which validation checks were
used before treating the dataset as ready.

## Dataset Purpose

The dataset supports a three-month scheduling and resource-allocation demo for the
Elyx member persona Marcus Tan. It is designed to show that the scheduler can:

- translate member goals into concrete activity prescriptions
- reason over weekly and three-month goal targets
- choose activities hierarchically from a primary need, through availability and
  resource constraints, to primary or same-family substitute activities
- preserve clinical and wellness intent when travel, provider availability,
  facility availability, equipment availability, fatigue, pain, or time conflicts
  require substitutions
- generate a schedule that can be audited against goals, resources, and
  constraints

The active dataset lives in `data/`. Generation and audit artifacts live in
`data/generated/`. Superseded or invalid intermediate attempts live in
`data/old/`.

## Final Dataset Shape

The accepted generated dataset contains:

| Area | Final count |
| --- | ---: |
| Goal actions in member profile | 7 |
| Activity families | 50 |
| Primary activities | 50 |
| Scheduler-facing activities | 100 |
| Care-domain batches | 5 |
| Availability blocks | 277 |
| Planning horizon | 3 months |

The active Stage 05 activity-family output is organized into five care-domain
batches:

| Batch | Care domain | Families | Activities |
| --- | --- | ---: | ---: |
| `001_metabolic_nutrition` | Metabolic nutrition | 12 | 24 |
| `002_cardiorespiratory_fitness` | Cardiorespiratory fitness | 10 | 20 |
| `003_strength_mobility_pain` | Strength, mobility, and pain | 10 | 20 |
| `004_recovery_sleep_stress` | Recovery, sleep, and stress | 8 | 16 |
| `005_clinical_review_measurement` | Clinical review and measurement | 10 | 20 |

This gives exactly 50 activity families and 100 scheduler-facing activities.
Each family has one primary activity. Additional scheduler-facing activities are
same-family substitutions or realistic context variants.

## Generation Stages

The dataset was generated as staged artifacts rather than as one large prompt.
This made the assignment data easier to inspect, validate, and repair when the
model output was internally inconsistent.

### Stage 01: Member Profile

The member profile captures Marcus Tan's persona, preferences, constraints,
journey phases, goals, and goal actions. The important output for scheduling is
`member_profile.goal_actions`.

Goal actions are period-aware. The current dataset uses weekly and three-month
targets only. The earlier `weekly_goal_actions`, `target_per_week`, and `wga_*`
contract was replaced for the active generation path because the scheduler needs
to talk concretely about both weekly goals and three-month goals.

The active taxonomy also removes the earlier travel-continuity goal action.
Travel remains an important scheduling context, but it no longer has its own
overlapping denominator. Travel meals, exercise, strength, and recovery
activities count toward their underlying weekly goals. Member-facing coaching
and care-team decision follow-through are represented explicitly through:

- `ga_behavior_coaching_weekly`
- `ga_care_team_followthrough_3month`

Primary artifact:

- `data/member_profile.json`

### Stage 02: Resource Universe

The resource universe defines the concrete providers, locations, and equipment
that activities may reference. Generated activities are not allowed to invent new
resource IDs.

Primary artifact:

- `data/resource_universe.json`

### Stage 03: Known Frictions

Known frictions capture realistic blockers such as travel, time pressure,
provider availability, meal-prep failure, pain, fatigue, and facility or equipment
limitations. These frictions are used by activity substitutions and scheduling
logic.

Primary artifact:

- `data/known_frictions.json`

### Stage 04: Availability

Availability is expanded into concrete scheduler-facing blocks over the
three-month planning horizon. This includes member blocked time, provider
availability, location/equipment availability, and travel windows.

Primary artifacts:

- `data/availability_patterns.json`
- `data/availability.json`

### Stage 05A: Activity Family Blueprint

Stage 05A creates the plan for the activity families before detailed activities
are generated. The blueprint exists to prevent the model from mixing domains,
dropping families, or creating travel/adherence as standalone batches.

The final design uses five care-domain batches:

- metabolic nutrition
- cardiorespiratory fitness
- strength, mobility, and pain
- recovery, sleep, and stress
- clinical review and measurement

Travel, adherence, provider unavailability, facility unavailability, equipment
unavailability, pain, fatigue, and load adjustment are modeled inside these
families as contexts and substitution reasons. They are not standalone Stage 05
batches.

The accepted blueprint has this self-check:

```json
{
  "001_metabolic_nutrition": 12,
  "002_cardiorespiratory_fitness": 10,
  "003_strength_mobility_pain": 10,
  "004_recovery_sleep_stress": 8,
  "005_clinical_review_measurement": 10,
  "total": 50
}
```

Primary artifacts:

- `data/activity_family_blueprint.json`
- `data/generated/stage05_activity_blueprint/activity_family_blueprint_retry1_repaired.json`

### Stage 05B: Activity Family Batches

Stage 05B generates detailed `ActivityFamily` objects from the accepted blueprint.
Each generated family includes:

- family identity and care domain
- family-level target
- goal action IDs
- one primary activity
- zero or more same-family substitutions
- substitution rules
- validation notes

The scheduler-facing hierarchy is:

```text
primary need -> availability/resources -> primary activity -> same-family substitution
```

Substitutions count toward the family target when they preserve the same goal
action and the family target permits substitution counting. This is important for
realistic scheduling: Marcus can still satisfy the intent of a family when the
preferred provider, location, equipment, load, or time window is not available.

Meal substitutions can also be marked as planned variety. These activities are
expanded from the primary meal frequency even when their own frequency is
`as_needed` with `count: 0`, allowing the scheduler to choose restaurant,
member-assembled, low-prep, or travel-compatible meals as deliberate variety
rather than only as failure fallbacks. The scheduler tracks weekly primary caps
inside a family and prefers a planned-variety substitution once the primary cap
has been met.

Primary artifacts:

- `data/generated/stage05_activity_families/batches/`
- `data/activity_families.json`
- `data/action_plan.json`

## Corrections Made During Generation

Several earlier versions of Stage 05 were not accepted because they were not
internally consistent enough for a reviewer-facing assignment dataset.

### Consolidating Batches

An earlier approach separated travel, adherence, and consolidation into their
own batches. That was removed. The final dataset uses only the five care-domain
batches listed above. Travel and adherence now appear where they belong: as
contexts, dependencies, support activities, or substitution triggers within the
relevant activity family.

During reviewer-readiness repair, the overlapping travel-continuity action was
removed from active profile, family, and activity references. Care-team reviews,
provider handoffs, lab follow-ups, and plan-adjustment consultations now count
toward care-team follow-through. Remote coaching, adherence-barrier review, and
travel friction resolution now count toward behavior coaching.

### Repairing the Blueprint

The initial blueprint attempts undercounted families:

- one attempt produced 47 families
- a later attempt produced 45 families

The accepted blueprint was repaired deterministically by adding the missing
families to reach the required care-domain distribution of 12/10/10/8/10, for a
total of 50 families. The repaired blueprint is archived as a generated artifact
and copied into the active dataset as `data/activity_family_blueprint.json`.

### Enforcing 100+ Scheduler-Facing Activities

The first detailed Stage 05 batch generation produced 50 families but only 86
scheduler-facing activities. That was not accepted because the assignment dataset
needs at least 100 activities.

The generator and prompts were updated so each batch has a minimum activity
floor equal to two scheduler-facing activities per family. The short output was
archived in:

- `data/old/generated/stage05_activity_families_first_short/`

The active first run was then repaired by adding realistic same-family
substitution variants to sparse families. This preserved the 50-family design and
raised the final activity count to 100.

Consultation scheduling was raised for high-touch Elyx realism. Clinical and
coaching consultations now use feasible weekly or monthly frequencies, remote
evening windows, and provider availability starts as candidate times. The final
demo calendar includes at least 10 consultation rows across the three-month
horizon.

The repair is reproducible in:

- `scripts/repair_stage05_first_run.py`

## Validation

The final dataset was validated with:

```bash
python scripts/validate_data.py
pytest -q
```

The canonical validation report passed:

```text
Validation pass: 100 activities, 50 primary
```

The full test suite passed:

```text
131 passed
```

The validation report confirms:

- 100 scheduler-facing activities
- exactly 50 activity families
- all activity IDs are unique
- all five modalities are present: consultation, fitness, food, medication, and
  therapy
- provider references resolve
- equipment references resolve
- location references resolve
- substitution references resolve
- activity goal action references resolve
- activity family goal action references resolve
- family targets are complete
- substitutions preserve family-level counted targets
- the availability horizon covers June, July, and August 2026
- availability density and resource distribution are within target ranges

Primary validation artifact:

- `data/runs/demo-run/01_validation/validation_report.json`

## Downstream Scheduling Artifacts

After the dataset was accepted, the demo run was rebuilt with:

```bash
python scripts/build_demo_run.py
```

The rebuilt scheduler output contains:

- 738 expanded task instances
- 347 scheduled calendar rows
- 147 unscheduled task instances
- 244 skipped task instances, primarily because a family primary already
  satisfied the occurrence or support-only work was not a standalone member
  calendar task
- all five activity modalities represented in the calendar output
- a serialized `goal_report` covering weekly and three-month goal status

The calendar summary includes:

| Activity type | Scheduled rows |
| --- | ---: |
| consultation | 1 |
| fitness | 54 |
| food | 149 |
| medication | 92 |
| therapy | 51 |

The scheduler now writes weekly and three-month goal coverage into:

- `data/runs/demo-run/03_scheduling/personalized_plan.json`

This makes unmet targets explicit rather than implicit. For example, the current
schedule reports weekly goal coverage by ISO week and the three-month clinical
review target as a separate three-month goal item.

## Reviewer Notes

The dataset intentionally favors auditability over hiding the generation process.
Superseded outputs are archived under `data/old/` so reviewers can see what was
rejected and why. The accepted files in `data/` are the source of truth for the
assignment demo.

The most important modeling decision is that substitutions are not loose
alternatives. They remain inside an activity family, preserve the family intent,
and can count toward the same family-level target only when the target rules say
they should. This lets the scheduler make realistic substitutions without losing
the ability to report whether weekly and three-month goals were met.
