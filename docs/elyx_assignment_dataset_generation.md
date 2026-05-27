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

The active dataset lives in `data/`. Prompt/model generation intermediates live
in `data/generated/` and are ignored for deployment. Deployable run artifacts
live in `data/runs/demo-run/` and should be committed because the Vercel app is
read-only and serves those JSON/Markdown files at runtime.

## Final Dataset Shape

The accepted generated dataset contains:

| Area | Final count |
| --- | ---: |
| Goal actions in member profile | 8 |
| Activity families | 50 |
| Primary scheduler-facing activities | 49 |
| Scheduler-facing activities | 100 |
| Care-domain batches | 5 |
| Availability blocks | 327 |
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
Most families have one primary activity plus one same-family substitution or
realistic context variant. One originally independent hotel-gym strength activity
is intentionally linked as a substitution in the home-strength family so Tokyo
travel can prefer the hotel gym before falling back to in-room bands/bodyweight.

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

Daily meal coverage, daily medication/supplement adherence, structured meals,
aerobic conditioning, strength, recovery, coaching, and clinical follow-through
are represented as concrete goal actions. The scheduler uses these actions for
weekly and three-month reporting.

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
availability, location/equipment availability, travel windows, WFH override
days, occasional fitness-hour conflicts, and travel-specific equipment such as
Tokyo hotel-gym availability.

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
- a primary activity when the family owns a standalone default option
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

Travel substitutions are also resource-sensitive. For example, Tokyo travel has
`eq_basic_gym_hotel_tokyo`, so strength scheduling now prefers a hotel-gym
strength option before using the lower-resource in-room bands/bodyweight
fallback. Lower-resource travel windows can still use portable equipment or
remote/self-led substitutions.

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
not accepted into the active dataset; the accepted generated intermediates are
kept under `data/generated/`.

The active first run was then repaired by adding realistic same-family
substitution variants to sparse families. This preserved the 50-family design and
raised the final activity count to 100.

Consultation scheduling was raised for high-touch Elyx realism. Clinical and
coaching consultations now use feasible weekly or monthly frequencies, remote
evening windows, and provider availability starts as candidate times. The final
demo calendar includes at least 10 consultation rows across the three-month
horizon.

The provider universe was also expanded so training and remote-coaching rows can
associate to concrete providers where appropriate. Provider spacing policy avoids
back-to-back consultations with the same provider.

### Scheduler Policy Repairs

After initial calendar review, several scheduler behaviors were corrected:

- every day now receives breakfast, lunch, and dinner unless a clear fasting or
  skip reason exists
- medication/supplement tasks remain daily and are not mislabeled as remote
  provider activities
- medium/high-load fitness must end by 20:30 unless explicitly allowed
- substantial fitness sessions cannot stack multiple times on the same day
- member location follows office, WFH, or travel state; during travel, hotel
  location takes precedence
- WFH days are represented as member-location overrides
- weekly validation reports structured meals, member-assembled meal caps,
  estimated chef-prep sessions, aerobic sessions, strength sessions, and
  recovery actions
- calendar rows keep `date` and `compact_group_key` aligned, and rows that move
  off their target date include `original_target_date`
- conditional clinical activities were renamed when no trigger exists, for
  example initial physio assessment instead of pain-escalation language

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
Validation pass: 100 activities, 49 primary
```

The full test suite passed:

```text
152 passed
```

The validation report confirms:

- 100 scheduler-facing activities
- exactly 50 activity families
- 49 primary scheduler-facing activities
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
- deployable run artifacts exist under `data/runs/demo-run/`

Primary validation artifact:

- `data/runs/demo-run/01_validation/validation_report.json`

## Downstream Scheduling Artifacts

After the dataset was accepted, the demo run was rebuilt with:

```bash
python scripts/build_demo_run.py
```

The rebuilt scheduler output currently contains:

- 1,396 expanded task traces
- 526 scheduled calendar rows
- 157 unscheduled task instances
- 713 skipped task instances, primarily because a family primary already
  satisfied the occurrence, a substitution was not needed, or support-only work
  was not a standalone member calendar task
- all five activity modalities represented in the calendar output
- a serialized `goal_report` covering weekly, three-month, and weekly validation
  status

The calendar summary includes:

| Activity type | Scheduled rows |
| --- | ---: |
| consultation | 22 |
| fitness | 79 |
| food | 276 |
| medication | 92 |
| therapy | 57 |

The scheduler now writes weekly and three-month goal coverage into:

- `data/runs/demo-run/03_scheduling/personalized_plan.json`

This makes unmet targets explicit rather than implicit. The current schedule
reports weekly goal coverage by ISO week, three-month clinical/care-team review
targets as separate three-month items, and weekly validation rows for the
assignment-level constraints. Some constrained travel or partial-horizon weeks
can still be marked unmet; the report exposes those misses rather than hiding
them.

## Reviewer Notes

The dataset intentionally favors auditability over hiding the generation process.
Generated prompt/model intermediates remain under `data/generated/` for local
inspection, while the accepted source files in `data/` and the deployable
artifacts in `data/runs/demo-run/` are the source of truth for the assignment
demo.

The most important modeling decision is that substitutions are not loose
alternatives. They remain inside an activity family, preserve the family intent,
and can count toward the same family-level target only when the target rules say
they should. This lets the scheduler make realistic substitutions without losing
the ability to report whether weekly and three-month goals were met.
