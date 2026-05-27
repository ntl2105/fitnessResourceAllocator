# Assembled Prompt: Stage 05 Activity Family Batch 005_clinical_review_measurement

Send this prompt to OpenAI.

---

## System Role

# System Role

You are generating synthetic demo data for an Elyx HealthSpan Resource Allocator prototype.

Your job is to produce realistic, internally consistent, schema-valid data for a scheduling and resource-allocation system. The data should help demonstrate how a simple allocator adapts a member's health plan around availability, travel, equipment, providers, food prep, and other constraints.

This is synthetic demo data only. It is not medical advice. Do not claim clinical validity. Do not diagnose the member. Do not invent medical facts beyond plausible scheduling-demo context.

## Output Discipline

- Output only the requested artifact.
- If the requested artifact is JSON, output valid JSON only.
- Do not include Markdown, comments, prose, or explanations outside the JSON unless the stage explicitly asks for Markdown.
- Use stable IDs that are easy to reference later.
- Preserve IDs from previous-stage inputs exactly.
- Do not invent provider, equipment, location, or travel IDs after the resource-universe stage.
- Make constraints realistic enough to produce meaningful scheduler traces.
- Do not make every activity perfectly schedulable.
- Some substitutions, reschedules, and unscheduled tasks should be expected.
- Prefer coherent care logic over superficial variety.

## Synthetic Data Boundary

The generated data should be plausible for a healthspan concierge scheduling demo, but it should not be clinically authoritative. Use language such as "physician review," "approved protocol," "synthetic marker," and "care-team follow-up" rather than definitive medical claims.

---

## Activity Schema Rules

# Activity Schema Rules

Activities are generated inside `ActivityFamily` objects.

Each family contains one primary activity and realistic substitutions when applicable. Substitutions must stay in the same family as the primary activity so intent is preserved.

## Required family fields

Each family must include:

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

`family_validation_notes` must be an array of strings, even when there is only
one note.

`care_domain` must be one of:

- `metabolic_nutrition`
- `cardiorespiratory_fitness`
- `strength_mobility_pain`
- `recovery_sleep_stress`
- `clinical_review_measurement`

`family_target` must describe the goal need this family satisfies:

```json
{
  "goal_action_id": "ga_structured_meals_weekly",
  "period": "weekly",
  "target_units": 2,
  "unit_label": "sessions",
  "substitutions_count": true,
  "support_counts": false
}
```

Use only `weekly` or `3_month` as the target period.

Weekly target example:

```json
{
  "goal_action_id": "ga_strength_sessions_weekly",
  "period": "weekly",
  "target_units": 2,
  "unit_label": "sessions",
  "substitutions_count": true,
  "support_counts": false
}
```

3-month target example:

```json
{
  "goal_action_id": "ga_clinical_review_3month",
  "period": "3_month",
  "target_units": 4,
  "unit_label": "reviews",
  "substitutions_count": true,
  "support_counts": false
}
```

Substitutions that replace the primary should count toward the same family
target unless the family is explicitly support-only.

`substitution_rules` must be an array of JSON objects, not strings. Each object
should include fields such as:

```json
{
  "when": "member traveling and gym equipment is unavailable",
  "prefer_activity_id": "act_example_travel",
  "reason": "Preserves aerobic intent with fewer location and equipment constraints."
}
```

## Required activity fields

Every primary and substitution activity must include:

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

Every activity must include `goal_contributions`. A counted contribution should
include `goal_action_id`, `counts_toward_weekly_target`, `value`, `role`, and
optional `notes`.
Substitution activities that satisfy the family target must carry the same
counted `goal_action_id` as the primary. If a substitution only supports the
primary or prepares for it, set `value: 0` and
`counts_toward_weekly_target: false`. A support task should not count unless
`family_target.support_counts` is true.

Substitution activities should also include these extra metadata fields:

- `substitution_for_activity_id`: the primary activity ID this replaces
- `substitution_reason_codes`: an array using the allowed reason codes below
- `substitution_notes`: concise explanation of why this preserves the same intent

Allowed `substitution_reason_codes`:

- `travel_window`
- `provider_unavailable`
- `facility_unavailable`
- `equipment_unavailable`
- `lower_load_needed`
- `pain_or_fatigue`
- `remote_delivery_needed`
- `time_conflict`
- `prep_unavailable`

Do not use substitutions as unrelated variety. A substitution is an alternate
way to satisfy the same family intent when a specific constraint makes the
primary activity harder or inappropriate. Common triggers include load
adjustment, provider unavailability, facility unavailability, equipment
unavailability, member travel, pain or fatigue, meal prep failure, and time
conflict.

## Title Quality Rules

Activity titles must describe what the member or provider actually does.
Titles must not describe why the activity exists.
Titles also must not include delivery-mode parentheticals such as
`(remote or in-person)`, `(remote)`, `(in-person)`, or similar channel labels.
Put delivery mode in `details`, `remote_allowed`, `allowed_locations`, and
`substitution_rules`.

Do not use these words or phrases in activity titles:

- `fallback`
- `backup`
- `substitution`
- `remote or`
- `remote-or`
- `hotel-gym`
- parenthetical delivery labels such as `(remote or in-person)`

Use `details`, `substitution_rules`, and `family_validation_notes` to explain
that an activity is easier during travel, remote-compatible, lower-load, or
used when a primary activity cannot be scheduled.

Good titles:

- `Bodyweight aerobic session during travel`
- `Travel-compatible breakfast`
- `Hotel-room mobility session`
- `Remote trainer check-in`
- `Lower-load strength circuit`
- `Trainer-physio care-team handoff review`

Bad titles:

- `Travel fallback`
- `Remote or hotel-gym substitution`
- `No-prep fallback`
- `Backup lower-body session`
- `Trainer-physio care-team handoff review (remote or in-person)`

## Goal contribution metadata

Activities may include an extra `goal_contributions` field to support weekly and 3-month goal coverage review.

Use it when the activity meaningfully contributes to a member goal:

```json
{
  "goal_contributions": [
    {
      "goal_id": "metabolic_health",
      "goal_action_id": "ga_structured_meals_weekly",
      "role": "core",
      "counts_toward_weekly_target": true,
      "unit": "activity",
      "value": 1,
      "notes": "Directly supports weekly metabolic-health coverage."
    }
  ]
}
```

Allowed roles:

- `core`
- `support`
- `prerequisite`
- `recovery`
- `measurement`

Only `core` or explicitly justified `measurement` activities should normally count toward goal targets. Do not mark every supplement, hydration task, reminder, or habit block as full goal coverage.

Substitutions may count toward the same goal action when they preserve the family intent. Their `goal_contributions` should explain whether they count fully or partially.

Every `goal_contributions` item that counts toward goal coverage should reference a valid `goal_action_id` from `member_profile.goal_actions`.

The family-level `goal_action_ids` should list the goal actions the family can satisfy. Activity-level `goal_contributions` should describe whether the specific primary or substitution activity counts fully, partially, or only as support.

Target-counting rules:

- actual meal consumption can count toward a meal action
- actual training can count toward strength or cardio actions
- actual recovery execution can count toward recovery actions
- labs, assessments, or clinician reviews can count toward measurement actions when due
- prep, planning, reminders, logging, handoffs, protocol checks, ordering precommitments, and supplement-only activities should normally be support with `counts_toward_weekly_target: false`

If an activity supports a goal action but should not count toward the denominator, include the same `goal_action_id` with:

```json
{
  "goal_action_id": "ga_structured_meals_weekly",
  "role": "support",
  "counts_toward_weekly_target": false,
  "value": 0
}
```

## Supported activity types

Every activity must map to exactly one of:

- `fitness`
- `food`
- `medication`
- `therapy`
- `consultation`

## Food activity requirements

Food activities must represent actual consumption or preparation, not only supplements.

Use meal-specific food activities where relevant:

- breakfast
- lunch
- dinner

The meal slot can be expressed through clear titles and details, and may also be included as an extra metadata field such as `"meal_slot": "breakfast"`. Extra metadata is allowed when it makes audit and calendar review clearer.

Supplements that are taken with breakfast may depend on a breakfast activity, but they do not replace breakfast as a food activity.

Food timing should respond to realistic constraints. For example, a fasted blood panel later in the day should affect earlier meals, meal timing, and related medication or supplement dependencies.

## Supported load levels

Use exactly one of:

- `low`
- `medium`
- `high`

## Frequency format

Frequency must be explicit enough to expand into task instances.

Examples:

```json
{
  "type": "weekly",
  "count": 3,
  "preferred_days": ["monday", "wednesday", "saturday"],
  "preferred_time_windows": ["06:30-08:00", "18:45-20:00"]
}
```

```json
{
  "type": "daily",
  "count": 1,
  "preferred_time_windows": ["08:00-09:00"]
}
```

```json
{
  "type": "once",
  "target_date": "2026-06-04",
  "window_days": 7,
  "preferred_time_windows": ["07:00-10:00"]
}
```

## Dependencies

Dependencies may include:

- food preparation before food consumption
- fasting before lab work
- lab results before physician consultation
- food before medication or supplements that require a meal
- hydration before sauna or high-load therapy
- lower-load adjustment after travel over 3 hours

Food-prep example:

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

## Substitution rules

Substitutions must:

- be in the same activity family as the primary activity
- share at least one goal tag with the primary activity
- preserve the primary activity's intent
- reduce at least one scheduling constraint under the relevant friction
- not require unknown provider, equipment, or location IDs

Example substitution reasons:

- member traveling
- primary provider unavailable
- equipment unavailable
- high-load activity unsafe after poor sleep or travel
- food prep cannot be completed

When the reason is travel, the substituted activity should normally still count
toward the underlying meal, cardio, strength, recovery, consultation, or
measurement weekly action. Travel is the context for the adaptation, not a
separate core denominator.

## Care handoff metadata

Activities involving providers should include useful `care_context_required` and `share_with_provider_types`.

Examples:

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

Do not require raw clinical data unless the activity genuinely involves physician or lab review.

---

## Batch Instructions

# Batch Instructions

Activities should be generated in small coherent batches of activity families.

Each batch should contain the exact number of activity families requested by
the batch scope.

Each family should contain:

- exactly one primary activity
- zero to three substitution activities when realistic
- substitution rules when substitutions exist

## Batch coherence

Each batch should focus on a care stream, not a date range.

Good batch themes:

- cardiovascular fitness and mobility
- strength and knee-safe training
- nutrition and metabolic health
- medication and supplement adherence
- sleep and recovery therapy
- PT, trainer, physician, and dietitian consultations
- lab testing and physician follow-up
- travel adaptations inside the relevant care stream
- adherence adaptations inside the relevant care stream

Chronology belongs to the scheduler, not the batch.

## Cross-batch requirements

Across all generated batches, the final flattened `action_plan.json` must contain:

- at least 100 scheduler-facing activity prescriptions
- exactly 50 primary activity families
- substitutions counted separately and linked to families
- all five activity types represented

Do not inflate counts with low-value duplicate substitutions.

## ID rules

Use stable, non-overlapping IDs.

Examples:

- `fam_strength_001`
- `act_strength_001_primary`
- `act_strength_001_remote_travel`

If a batch index or ID prefix is provided, use it exactly.

## Avoid duplicates

Before generating a batch, use the provided existing activity summaries to avoid duplicating the same prescription.

Similar activities are allowed only when they serve distinct purposes, phases, frequencies, providers, or constraints.

---

## Client Profile Rules

# Client Profile Context Rules

The member profile is the source of coherence for the entire synthetic dataset.

Every later artifact should trace back to this profile's goals, preferences, constraints, baseline metrics, journey phases, location rhythm, and travel windows.

## The profile must support realistic scheduling complexity

The member should have enough detail to justify all five activity modalities:

- fitness
- food
- medication
- therapy
- consultation

Do not create fake clinical complexity just to cover categories. Instead, create a plausible executive-healthspan context where these modalities naturally arise.

## Five activity category definitions

Every generated activity must map to exactly one of these five categories. Use
the category that describes what the member is actually doing during the
scheduled block, not why the activity exists.

### `fitness`

Use `fitness` for physical training, conditioning, strength, mobility,
activation, warmups, cool-downs, and member-led exercise execution.

Examples:

- trainer-led strength session
- Zone 2 bike, swim, walk, or aerobic circuit
- bodyweight travel workout
- member-led mobility, activation, stretching, or movement prep

Mobility or stretching is still `fitness` when it is member-led exercise or
training preparation. Do not classify it as `therapy` merely because it is
knee-safe, lower-load, recovery-oriented, or modified for travel.

### `food`

Use `food` for actual meal consumption or an active meal task performed by the
member.

Examples:

- high-protein breakfast
- structured office lunch
- chef-prepped dinner eaten at home
- restaurant, hotel buffet, or room-service meal during travel
- member-assembled meal when Marcus actively prepares or assembles food

Food activities should usually be breakfast, lunch, or dinner when food is part
of the member's goal coverage. Chef/cook work is normally food-source context,
not a separate member calendar activity. A scheduled food row should say what
Marcus eats and where he eats it; metadata should explain whether it was
chef-prepped, office-delivered, packed, restaurant-based, hotel buffet, room
service, or member-assembled.

### `medication`

Use `medication` for medications, supplements, CGM checks, hydration/electrolyte
protocols, adherence logging, and other protocol tasks that are not meals,
training, therapy, or provider consultations.

Examples:

- morning supplement protocol with breakfast
- evening medication protocol with dinner
- CGM check and log
- hydration/electrolyte protocol

Medication and supplement activities may depend on food timing, but they do not
replace breakfast, lunch, or dinner and should not count as meal completion.

### `therapy`

Use `therapy` only for therapeutic or recovery interventions that are genuinely
clinical, provider-directed, or treatment-like rather than ordinary exercise.

Examples:

- physiotherapist-led rehabilitation session
- clinician-directed knee or back therapy
- massage, sauna, cold/heat therapy, breathwork, or other recovery therapy when
  generated as a treatment or recovery intervention
- pain-escalation therapy session

Do not use `therapy` for ordinary member-led mobility, stretching, warmups,
activation, or low-load strength. Those belong in `fitness` unless a clinician
is actively delivering a therapeutic intervention.

### `consultation`

Use `consultation` for provider meetings, lab/measurement appointments, reviews,
care-team handoffs, and remote or in-person expert guidance where the main work
is assessment, discussion, coordination, or decision-making.

Examples:

- physician review after labs
- dietitian consultation
- physiotherapy reassessment
- trainer or care-team planning check-in
- blood draw, lab panel, CGM review, or other measurement appointment

A consultation can create dependencies for later activities, but it is not a
substitute for the execution activity itself. For example, a remote trainer
check-in does not count as an aerobic or strength session unless Marcus actually
performs the training during that scheduled block.

### Cross-category rules

- Travel adaptation is not a sixth category. Travel-compatible work should
  remain `fitness`, `food`, `medication`, `therapy`, or `consultation` based on
  what Marcus actually does.
- Travel adaptations should normally be substitutions or alternate delivery
  modes for underlying meal, cardio, strength, recovery, adherence, or
  consultation goals.
- Substitution status is not a category. A substitution keeps the same modality
  as the activity it replaces unless the actual member action changes.
- Prep, planning, reminders, logs, handoffs, and protocol checks should not
  masquerade as core completion of meals, training, recovery, or consults.
- If an activity appears to fit two categories, choose the category of the
  scheduled member action and put the secondary rationale in `details`,
  `goal_contributions`, dependencies, or care handoff metadata.

## Required profile characteristics

The member profile must include:

- a member ID
- name
- timezone
- age range
- occupation
- typical work hours
- goals
- weekly goal actions
- preferences
- dietary access plan
- constraints
- baseline metrics
- scheduling rules
- journey phases
- location rhythm
- travel windows

The member must have:

- planned monthly travel
- at least one last-minute travel window
- realistic work constraints
- a preference or constraint that affects scheduling
- enough provider needs to justify trainer, physiotherapist, dietitian, physician, lab/phlebotomist, and chef/cook resources

## Weekly and 3-month goal targets and actions

Goals should be measurable at the week level and across the full 3-month horizon because the calendar review reports both.

Each goal should define:

- a weekly and/or 3-month minimum and preferred target
- the activity types or activity roles that count directly
- the activity types or roles that are only support or prerequisites
- whether substitutions can count toward the same goal

Avoid goals where every low-complexity recurring task counts as full progress. For example, a daily supplement may support metabolic health, but breakfast, lunch, dinner quality, Zone 2 work, labs, or clinician review are stronger direct coverage signals.

In addition to goal-level targets, the profile must include a top-level `goal_actions` array.

Use goal actions as the bridge from goals to activity families:

```text
goals -> goal_actions -> activity_families -> task_instances -> weekly and 3-month coverage
```

Each action defines a reviewable denominator, such as:

- 14 structured meal actions
- 3 aerobic conditioning actions
- 2 strength actions
- 1 recovery or mobility action after long travel
- 4 measurement or provider-review actions over 3 months

Mark support-only actions explicitly so they can be displayed without inflating core goal coverage.

Do not make travel adaptation an independent core goal action by default.
Travel-adapted meals, hotel-gym sessions, bodyweight sessions, and remote
consults should satisfy the same underlying meal, cardio, strength, recovery, or
consultation action they replace. If a travel continuity action is included, it
should normally be `support_only: true`.

## Dietary access plan

The member profile must make food logistics explicit. Include a
`dietary_access_plan` that states what food the member can actually access at
home, at the office, during normal dining out, and during travel.

For Marcus Tan, use these assumptions unless the user overrides them:

- He has Singapore home cook/private chef support.
- He can receive chef-prepped or dietitian-approved office lunches during work
  blocks.
- Office lunch is a low-complexity eating activity and should not require the
  member to leave work or personally prep food at midday.
- Dinner is usually home chef-prepped, structured restaurant dining, or a
  travel-compatible meal depending on location.
- Marcus personally assembles food at most 2 times per week.
- Non-travel restaurant meals are allowed but limited; travel weeks naturally
  use more restaurant/hotel meals.
- Meal prep/provider work should be represented as food source context unless
  Marcus actively participates.

## Coherence Requirements

Goals should explain why activities later exist.

Examples:

- A goal to increase lean muscle mass can justify trainer-led strength, physio assessment, protein meals, recovery, and strength metrics.
- A goal to improve metabolic health can justify labs, nutrition planning, glucose-related metrics, cardio, and physician review.
- A goal to improve sleep can justify recovery therapy, caffeine cutoff, evening routines, and travel sleep protection.
- Frequent travel can justify hotel-gym substitutions, remote consultations, meal fallbacks, and rescheduling.
- Travel over 3 hours can justify lower-load substitutions, recovery emphasis, and reduced same-day scheduling after arrival.
- A mild physical limitation can justify physiotherapist involvement, modified training, and high-load skip adjustments.

## Avoid

- Diagnosing the member.
- Creating severe medical conditions that would require real clinical guidance.
- Creating a profile so complex that the first scheduler cannot plausibly handle it.
- Creating preferences that make every resource perfectly available.
- Requiring exact transportation or commute-time modeling for this version; travel should affect state and location, especially fatigue after trips over 3 hours.

---

## Realism Rules

# Realism Rules

The goal is realistic synthetic data, not maximum variety.

The final dataset should feel like one coherent member journey over 3 months.

## General realism

- Activities should be tied to member goals.
- Activities should reflect member preferences and constraints.
- Frequencies should be plausible.
- Durations should be plausible.
- Consultations and labs should not occur unrealistically often.
- High-load activities should not dominate the plan.
- Medication and supplement activities should be low-load and dependency-aware.
- Food activities should include real breakfast, lunch, and dinner prescriptions where they matter to the member journey. Supplements do not count as meals.
- Food activities may be frequent, but avoid creating dozens of duplicate meal rows.
- Therapy should be occasional or recovery-driven unless the profile clearly justifies more.
- Travel should cause realistic adaptation, not just labels.
- Weekly goal coverage should be interpretable. Low-complexity daily habits should not inflate the apparent progress toward major goals.

## Frequency realism

Plausible patterns:

- medication/supplement: daily, weekly, or protocol-based
- food: daily or several times per week
- fitness: 2-5 times per week depending on load
- high-load fitness: not daily
- therapy: occasional, weekly, or recovery-triggered
- consultation: once, monthly, weekly for coaching, or milestone-based
- labs: once, monthly, or quarterly, not daily

## Load realism

- High-load activities should be limited.
- High-load lower-body training should respect knee and travel constraints.
- Recovery and mobility should appear after travel or high-load weeks.
- Poor sleep, pain escalation, and long flights should bias toward lower-load alternatives.
- Travel over 3 hours should create arrival-day or next-day fatigue logic. Do not treat a new-location day like an ordinary day.

## Travel realism

Planned travel may have:

- hotel gym
- hotel pool
- remote consultations
- limited local provider continuity
- limited lab access

Last-minute travel may have:

- hotel room only
- unreliable gym access
- restaurant meals
- higher work stress
- reduced sleep
- remote support only
- post-arrival fatigue after travel over 3 hours

## Resource realism

- Provider calendars should be independent from member preferences.
- Equipment may have maintenance or location constraints.
- Chef/cook availability should be limited.
- Lab availability should be constrained and usually morning-based.
- Locations should obey travel compatibility.

## Substitution realism

A substitution should not be random. It should preserve intent.

Good examples:

- in-person trainer strength session -> remote hotel-gym strength session
- high-load lower-body session after knee discomfort -> low-load mobility or cycling
- prepared breakfast when chef unavailable -> no-prep high-protein breakfast
- sauna unavailable -> breathwork or mobility recovery

Bad examples:

- lab test -> sauna
- medication -> cardio
- physician review -> protein shake
- strength training -> unrelated journaling

## Metrics realism

Metrics should fit the activity type.

Examples:

- fitness: RPE, heart rate, sets/reps, knee discomfort, completion
- food: meal completion, protein servings, fiber servings, post-meal energy, CGM note
- medication: completion, miss reason, side-effect flag
- therapy: recovery score, sleep quality next day, completion
- consultation: provider notes, next actions, completion

---

## member_profile.json

```json
{
  "age_range": "46-50",
  "baseline_metrics": {
    "body_composition": {
      "estimated_body_fat_percent": 23,
      "height_cm": 172,
      "waist_cm": 90,
      "weight_kg": 74
    },
    "fitness": {
      "cardio_pattern": "intermittent, drops during heavy travel",
      "estimated_vo2max_category": "below_average",
      "resting_heart_rate_bpm": 65,
      "strength_level": "intermediate"
    },
    "metabolic": {
      "risk_level": "mildly elevated",
      "synthetic_markers": [
        {
          "name": "fasting_glucose",
          "value": "slightly elevated (synthetic)"
        },
        {
          "name": "LDL-C",
          "value": "borderline (synthetic)"
        }
      ]
    },
    "sleep": {
      "average_bedtime": "23:40",
      "average_sleep_duration_hours": 6.1,
      "main_issue": "work-travel rhythm, investor calls, and late client dinners",
      "wake_time": "06:15"
    },
    "subjective": {
      "afternoon_energy_average": 7.1,
      "morning_energy_average": 6.5,
      "travel_week_energy_average": 5.6
    }
  },
  "constraints": {
    "behavioral": [
      "adherence drops if routines are overly complex or require daily meal prep/logging",
      "low friction is essential for routines to persist during travel",
      "opposes wellness interventions without clear, quantified rationale"
    ],
    "medical_safety": [
      "synthetic demo profile only",
      "abnormal or trend-worsening labs route to physician review",
      "high-intensity or high-load activity avoided after fatigue, travel, or pain"
    ],
    "physical": [
      {
        "constraint_id": "constraint_knee_001",
        "description": "Mild irritation post running or high flexion, aggravated if volume increases abruptly.",
        "implications": [
          "avoid running volume spikes",
          "prefer knee-safe lower body strength",
          "use cycling, rowing, or swimming during flare-ups"
        ],
        "name": "Mild right-knee irritation",
        "severity": "mild"
      },
      {
        "constraint_id": "constraint_back_001",
        "description": "Back tightness emerges often after flights exceeding 3 hours or long conference days.",
        "implications": [
          "schedule mobility or recovery post-travel",
          "avoid heavy deadlifts or loaded movements immediately after flights"
        ],
        "name": "Lower-back tightness after >3h flight or long sitting",
        "severity": "mild"
      }
    ],
    "schedule": [
      "monthly planned travel (2-6 days duration)",
      "occasional last-minute trips to Jakarta or Bangkok (short notice)",
      "morning and evening cross-timezone calls 2-3x/week",
      "client dinners up to 3x per month",
      "inconsistent sleep on travel weeks"
    ]
  },
  "dietary_access_plan": {
    "chef_capacity_per_week": 2,
    "dining_out_allowance_per_week": 3,
    "explicit_meal_scheduling": [
      "breakfast",
      "lunch",
      "dinner"
    ],
    "food_source_labels": [
      "chef_prepped",
      "office_delivery",
      "packed_meal",
      "member_assembled",
      "restaurant",
      "hotel_buffet",
      "room_service"
    ],
    "home_chef_access": true,
    "member_assembly_limit_per_week": 2,
    "normal_week_strategy": {
      "breakfast": "home chef-prepped or low-prep high-protein breakfast",
      "dinner": "home chef-prepped meal, with limited structured restaurant dinners when work or social context requires",
      "lunch": "structured office lunch from chef-prepped packed meal or office delivery"
    },
    "notes": "Chef/provider work should appear as food-source context unless Marcus actively participates. Office lunch should be schedulable while Marcus is at the office.",
    "office_meal_access": "chef-prepped packed lunch or office delivery during work blocks",
    "travel_meal_strategy": {
      "last_minute_low_resource_travel": "restaurant or room-service meals, fewer assumptions about ideal structure, remote dietitian support if adherence risk rises",
      "planned_high_resource_travel": "hotel buffet or room-service breakfast; restaurant or hotel lunch and dinner with dietitian guidance when needed"
    }
  },
  "goal_actions": [
    {
      "activity_types": [
        "food"
      ],
      "counts_substitutions": true,
      "goal_action_id": "ga_structured_meals_weekly",
      "goal_id": "goal_metabolic_health",
      "label": "Complete structured metabolic meals",
      "notes": "Chef-prepped, member-assembled (<2x per week), or travel-compatible meals count as structured. Supplement protocols or meal planning do not count.",
      "role": "core",
      "substitutions_allowed": true,
      "support_only": false,
      "target": {
        "period": "weekly",
        "unit_label": "meals",
        "units": 14
      }
    },
    {
      "activity_types": [
        "fitness"
      ],
      "counts_substitutions": true,
      "goal_action_id": "ga_aerobic_conditioning_weekly",
      "goal_id": "goal_metabolic_health",
      "label": "Complete aerobic conditioning",
      "notes": "Zone 2 \u2018true cardio\u2019, swimming, cycling, or suitable travel/hotel-gym equivalents count directly.",
      "role": "core",
      "substitutions_allowed": true,
      "support_only": false,
      "target": {
        "period": "weekly",
        "unit_label": "sessions",
        "units": 2
      }
    },
    {
      "activity_types": [
        "fitness"
      ],
      "counts_substitutions": true,
      "goal_action_id": "ga_strength_sessions_weekly",
      "goal_id": "goal_strength_and_mobility",
      "label": "Complete knee-modified strength sessions",
      "notes": "Trainer-led, hotel-gym, or bodyweight alternatives count if following knee-safe plan. Mobility substituted only post-travel or pain.",
      "role": "core",
      "substitutions_allowed": true,
      "support_only": false,
      "target": {
        "period": "weekly",
        "unit_label": "sessions",
        "units": 2
      }
    },
    {
      "activity_types": [
        "therapy",
        "fitness",
        "food"
      ],
      "counts_substitutions": true,
      "goal_action_id": "ga_sleep_recovery_weekly",
      "goal_id": "goal_sleep_recovery",
      "label": "Complete sleep and fatigue recovery actions",
      "notes": "Evening mobility, recovery, post-flight stretching, and travel sleep protection actions count. Logging or reminders do not.",
      "role": "recovery",
      "substitutions_allowed": true,
      "support_only": false,
      "target": {
        "period": "weekly",
        "unit_label": "actions",
        "units": 4
      }
    },
    {
      "activity_types": [
        "consultation"
      ],
      "counts_substitutions": true,
      "goal_action_id": "ga_clinical_review_3month",
      "goal_id": "goal_adherence_and_careteam",
      "label": "Complete preventive lab or provider review (when due)",
      "notes": "Only counts on scheduled lab, physician, or dietitian review weeks. Remote or in-person review is valid.",
      "role": "measurement",
      "substitutions_allowed": true,
      "support_only": false,
      "target": {
        "period": "3_month",
        "unit_label": "reviews",
        "units": 4
      }
    },
    {
      "activity_types": [
        "medication",
        "food",
        "consultation"
      ],
      "counts_substitutions": false,
      "goal_action_id": "ga_adherence_support_weekly",
      "goal_id": "goal_adherence_and_careteam",
      "label": "Complete support adherence or supplement protocol",
      "notes": "Daily supplements, check-in logging, and checklist review support adherence but do not count as core outcome progress.",
      "role": "support",
      "substitutions_allowed": false,
      "support_only": true,
      "target": {
        "period": "weekly",
        "unit_label": "protocol checks",
        "units": 7
      }
    },
    {
      "activity_types": [
        "consultation"
      ],
      "counts_substitutions": true,
      "goal_action_id": "ga_care_team_followthrough_3month",
      "goal_id": "goal_adherence_and_careteam",
      "label": "Complete care-team review and decision follow-through",
      "notes": "Counts physician, dietitian, physio, remote care-team handoff, plan-adjustment review, and lab-result follow-up touchpoints. Passive logs and reminders do not count.",
      "role": "care_team",
      "substitutions_allowed": true,
      "support_only": false,
      "target": {
        "period": "3_month",
        "unit_label": "touchpoints",
        "units": 6
      }
    },
    {
      "activity_types": [
        "consultation"
      ],
      "counts_substitutions": true,
      "goal_action_id": "ga_behavior_coaching_weekly",
      "goal_id": "goal_adherence_and_careteam",
      "label": "Complete behavior coaching and friction-resolution touchpoints",
      "notes": "Counts member-facing coaching, adherence barrier review, travel friction planning, post-missed-session coaching, and meal-prep failure resolution. Daily supplement-taking does not count.",
      "role": "coaching",
      "substitutions_allowed": true,
      "support_only": false,
      "target": {
        "period": "weekly",
        "unit_label": "touchpoints",
        "units": 1
      }
    }
  ],
  "goals": [
    {
      "description": "Reduce metabolic risk with structured meals, aerobic conditioning, measured protein, and regular physician and lab review.",
      "goal_id": "goal_metabolic_health",
      "goal_targets": [
        {
          "counts_activity_types": [
            "food",
            "fitness",
            "consultation"
          ],
          "goal_action_ids": [
            "ga_structured_meals_weekly",
            "ga_aerobic_conditioning_weekly"
          ],
          "minimum": 12,
          "notes": "Breakfast, lunch, and dinner structure and aerobic conditioning each count directly; supplement, meal planning, and chef prep are support-only.",
          "period": "weekly",
          "preferred": 14,
          "support_activity_types": [
            "medication"
          ],
          "unit": "support_context"
        }
      ],
      "name": "Improve metabolic health",
      "priority": 1,
      "success_indicators": [
        "14 structured meals completed per week",
        "2+ aerobic sessions/week",
        "improved fasting glucose at review"
      ]
    },
    {
      "description": "Build strength, especially lower-body and core, without aggravating right-knee or lower-back issues.",
      "goal_id": "goal_strength_and_mobility",
      "goal_targets": [
        {
          "counts_activity_types": [
            "fitness"
          ],
          "goal_action_ids": [
            "ga_strength_sessions_weekly"
          ],
          "minimum": 2,
          "notes": "Knee-modified strength or trainer-led sessions count. Mobility or assessment are support-only unless they replace strength after travel or pain.",
          "period": "weekly",
          "preferred": 3,
          "support_activity_types": [
            "therapy",
            "consultation"
          ],
          "unit": "core_activity"
        }
      ],
      "name": "Build and maintain safe, lean strength",
      "priority": 2,
      "success_indicators": [
        "2-3 knee-modified strength sessions",
        "trainer or physio assessment after travel",
        "no pain escalation post-strength work"
      ]
    },
    {
      "description": "Protect sleep duration and quality, especially on high-stress travel or late-call weeks, by targeting recovery, adjusting activity, and using provider support.",
      "goal_id": "goal_sleep_recovery",
      "goal_targets": [
        {
          "counts_activity_types": [
            "therapy",
            "fitness",
            "food"
          ],
          "goal_action_ids": [
            "ga_sleep_recovery_weekly"
          ],
          "minimum": 3,
          "notes": "Stretching, mobility, tailored post-travel routines, and sleep hygiene actions count. Logging or reminders are support-only.",
          "period": "weekly",
          "preferred": 4,
          "support_activity_types": [
            "consultation"
          ],
          "unit": "core_or_recovery_activity"
        }
      ],
      "name": "Preserve energy and consistent sleep, especially around travel",
      "priority": 3,
      "success_indicators": [
        "Sleep average at least 6h/night",
        "Less dropoff in sleep on travel",
        "At least 3 travel/fatigue recovery actions"
      ]
    },
    {
      "description": "Reduce fall-off during heavy travel weeks, ensure timely labs, and improve care-team coordination without increasing friction.",
      "goal_id": "goal_adherence_and_careteam",
      "goal_targets": [
        {
          "counts_activity_types": [
            "consultation"
          ],
          "goal_action_ids": [
            "ga_clinical_review_3month",
            "ga_adherence_support_weekly"
          ],
          "minimum": 1,
          "notes": "Labs and provider review count in due weeks only; adherence tasks and supplement protocols are tracked but don't inflate core coverage.",
          "period": "weekly",
          "preferred": 2,
          "support_activity_types": [
            "medication",
            "food"
          ],
          "unit": "measurement_or_support_activity"
        },
        {
          "goal_action_ids": [
            "ga_clinical_review_3month"
          ],
          "minimum": 1,
          "notes": "Full-horizon target used for 3-month goal attainment review.",
          "period": "3_month",
          "preferred": 4,
          "unit": "completed_actions"
        }
      ],
      "name": "Improve adherence and enable reliable preventive care",
      "priority": 4,
      "success_indicators": [
        "Follow up on scheduled labs and reviews",
        "Adherence logs above 80%",
        "Physician and dietitian reviews completed after screenings"
      ]
    },
    {
      "description": "Adapt core meal, movement, and provider routines while traveling. Accept substitutions as needed, prioritize continuity and quick recovery post-travel.",
      "goal_id": "goal_travel_resilience",
      "goal_targets": [
        {
          "counts_activity_types": [
            "fitness",
            "food"
          ],
          "goal_action_ids": [
            "ga_structured_meals_weekly",
            "ga_aerobic_conditioning_weekly",
            "ga_strength_sessions_weekly",
            "ga_sleep_recovery_weekly",
            "ga_behavior_coaching_weekly"
          ],
          "minimum": 2,
          "notes": "Travel is tracked as adaptation context. Travel meals, training, recovery, and remote care count toward their underlying weekly actions; this goal watches continuity and substitution quality without adding a separate core denominator.",
          "period": "weekly",
          "preferred": 3,
          "support_activity_types": [
            "therapy",
            "consultation"
          ],
          "unit": "core_activity"
        },
        {
          "goal_action_ids": [
            "ga_care_team_followthrough_3month",
            "ga_behavior_coaching_weekly"
          ],
          "minimum": 3,
          "notes": "Full-horizon target used for 3-month goal attainment review.",
          "period": "3_month",
          "preferred": 3,
          "unit": "completed_actions"
        }
      ],
      "name": "Maintain healthspan routines during heavy travel",
      "priority": 5,
      "success_indicators": [
        "1+ physical activity session completed during each travel window",
        "Structured meal adherence 80%+ during travel weeks",
        "At least 2 recovery/mobility sessions per multi-day trip"
      ]
    }
  ],
  "journey_phases": [
    {
      "end_date": "2026-06-18",
      "phase_id": "phase_marcus_001",
      "phase_type": "baseline",
      "primary_goals": [
        "goal_metabolic_health",
        "goal_strength_and_mobility",
        "goal_adherence_and_careteam"
      ],
      "scheduling_biases": [
        "prioritize baseline labs and movement review",
        "avoid sudden increases in lower-body load",
        "use in-person chef and trainer when possible"
      ],
      "start_date": "2026-06-01",
      "trigger": "Start of new HealthSpan plan. Initial labs, chef briefing, and movement review."
    },
    {
      "end_date": "2026-06-25",
      "phase_id": "phase_marcus_002",
      "phase_type": "travel",
      "primary_goals": [
        "goal_travel_resilience",
        "goal_sleep_recovery",
        "goal_metabolic_health"
      ],
      "scheduling_biases": [
        "prioritize aerobic and basic resistance training using hotel equipment",
        "use quick meal check-ins, chef-prepped or no-prep options",
        "avoid lab scheduling; all reviews remote"
      ],
      "start_date": "2026-06-19",
      "trigger": "Planned board meetings in Hong Kong. Use hotel gym and remote consults."
    },
    {
      "end_date": "2026-07-21",
      "phase_id": "phase_marcus_003",
      "phase_type": "consolidation",
      "primary_goals": [
        "goal_metabolic_health",
        "goal_strength_and_mobility",
        "goal_adherence_and_careteam"
      ],
      "scheduling_biases": [
        "reaffirm morning sessions, check-in with dietitian",
        "progress strength work gradually",
        "confirm post-travel sleep/adherence"
      ],
      "start_date": "2026-06-26",
      "trigger": "Return from travel, stabilize routines and monitor metrics."
    },
    {
      "end_date": "2026-07-29",
      "phase_id": "phase_marcus_004",
      "phase_type": "travel",
      "primary_goals": [
        "goal_travel_resilience",
        "goal_sleep_recovery",
        "goal_strength_and_mobility"
      ],
      "scheduling_biases": [
        "accept hotel gym or bodyweight subs",
        "use remote coach/dietitian as needed",
        "schedule mobility after arrival"
      ],
      "start_date": "2026-07-22",
      "trigger": "Planned Tokyo board and investor travel; full week out of Singapore, limited gym."
    },
    {
      "end_date": "2026-08-07",
      "phase_id": "phase_marcus_005",
      "phase_type": "pain_escalation",
      "primary_goals": [
        "goal_strength_and_mobility",
        "goal_sleep_recovery"
      ],
      "scheduling_biases": [
        "substitute strength with mobility; schedule physio consult",
        "minimize high load lower-body training",
        "coordinate handoff for trainer and physiotherapist"
      ],
      "start_date": "2026-08-01",
      "trigger": "Synthetic mild knee and back flare after post-travel overload."
    },
    {
      "end_date": "2026-08-16",
      "phase_id": "phase_marcus_006",
      "phase_type": "travel",
      "primary_goals": [
        "goal_travel_resilience",
        "goal_adherence_and_careteam"
      ],
      "scheduling_biases": [
        "focus on travel-compatible exercises",
        "structured eating mostly by restaurant with check-ins",
        "log fatigue post-travel"
      ],
      "start_date": "2026-08-13",
      "trigger": "Last-minute Jakarta escalation: low-resource, high stress, remote-only support."
    },
    {
      "end_date": "2026-08-31",
      "phase_id": "phase_marcus_007",
      "phase_type": "consolidation",
      "primary_goals": [
        "goal_metabolic_health",
        "goal_strength_and_mobility",
        "goal_sleep_recovery"
      ],
      "scheduling_biases": [
        "complete provider reviews/labs as due",
        "plan travel mitigation for next cycle",
        "avoid last-minute overload"
      ],
      "start_date": "2026-08-17",
      "trigger": "End-of-quarter check, final progress review, and next cycle planning."
    }
  ],
  "location_rhythm": {
    "home_location_id": "marcus_home",
    "office_location_id": "marcus_office",
    "ordinary_weekday_pattern": [
      {
        "likely_location": "marcus_home",
        "notes": "Preferred for home training, remote fitness or nutrition consultation, or chef breakfast.",
        "time_window": "06:00-08:15"
      },
      {
        "likely_location": "marcus_office",
        "notes": "Work focus; only short, low-complexity tasks feasible.",
        "time_window": "08:30-18:30"
      },
      {
        "likely_location": "marcus_home",
        "notes": "Backup evening training window. Sometimes gym or travel-screen.",
        "time_window": "18:45-20:00"
      },
      {
        "likely_location": "marcus_home",
        "notes": "Recovery, low-load habits, and wind down. Avoid strenuous sessions.",
        "time_window": "20:30-22:30"
      }
    ],
    "weekend_pattern": [
      {
        "likely_location": "marcus_gym_or_home",
        "notes": "Longer training with trainer or physiotherapist, or chef prep.",
        "time_window": "08:00-11:00"
      },
      {
        "likely_location": "marcus_home",
        "notes": "Family, meal planning, chef prep, and light movement.",
        "time_window": "12:00-18:00"
      }
    ]
  },
  "member_id": "member_elyx_marcus_001",
  "name": "Marcus Tan",
  "occupation": "Founder-Operator & Regional CEO, Logistics Technology",
  "preferences": {
    "communication_preferences": {
      "detail_level": "medium",
      "preferred_channels": [
        "app",
        "weekly summary"
      ],
      "style": "concise, rational, and progress-focused"
    },
    "consultation_preferences": [
      "prefers concise, actionable summaries",
      "accepts remote consultations (especially travel weeks)",
      "prefers in-person physio and movement review when available"
    ],
    "exercise_timing": {
      "acceptable": [
        "18:45-20:00"
      ],
      "avoid": [
        "after_20:30",
        "during_12:00-14:00"
      ],
      "preferred": [
        "06:30-08:00"
      ]
    },
    "nutrition_preferences": [
      "prefers high-protein, low-effort breakfasts",
      "values practical meal solutions over restrictive tracking",
      "enjoys Singaporean, Japanese, Mediterranean, Indian, and Vietnamese cuisine",
      "willing to cook/assemble at home up to 2x per week; prefers chef or no-prep otherwise",
      "does not want strict calorie counting"
    ],
    "session_length": {
      "weekday_max_minutes": 60,
      "weekend_max_minutes": 90
    },
    "training_preferences": [
      "prefers trainer-led and data-driven strength progressions",
      "needs knee-safe modifications for certain exercises",
      "accepts remote or app-based coaching during travel",
      "dislikes purely treadmill or monotonous cardio"
    ]
  },
  "profile_summary": "Marcus Tan is a driven, analytical Singapore-based CEO, managing technology and logistics teams across multiple Asia-Pacific hubs. With frequent travel and complex coordination demands, he values data-driven, low-friction routines designed to improve metabolic health, maintain functional strength, and optimize energy and sleep on the road\u2014with minimal decision fatigue.",
  "scheduling_rules": {
    "avoid_heavy_lower_body_after_flight_hours": 24,
    "avoid_high_intensity_after_poor_sleep": true,
    "compact_recurring_low_complexity_tasks_in_calendar": true,
    "default_time_granularity_minutes": 15,
    "max_high_load_activities_per_day": 1,
    "max_medium_or_high_load_activities_per_day": 2,
    "min_gap_between_fitness_sessions_hours": 6,
    "planning_months": 3,
    "planning_start_date": "2026-06-01",
    "poor_sleep_threshold_hours": 5.2,
    "prefer_morning_exercise": true,
    "weekday_session_limit_minutes": 60,
    "weekend_session_limit_minutes": 90
  },
  "timezone": "Asia/Singapore",
  "travel_windows": [
    {
      "available_location_ids": [
        "travel_hotel",
        "remote"
      ],
      "destination": "Hong Kong",
      "end": "2026-06-25T20:00:00+08:00",
      "expected_facilities": [
        "hotel_gym",
        "hotel_pool",
        "remote_consultation_supported"
      ],
      "limitations": [
        "no in-person trusted physio or lab",
        "restaurant meals dominant (2+ client dinners)",
        "some jetlag from travel over 3 hours"
      ],
      "member_location_override": "travel_hotel",
      "notes": "Planned high-resource travel. Hotel gym and pool available; care coordination shifts mostly remote except chef-prepped meals.",
      "purpose": "Board and investor meetings",
      "start": "2026-06-19T10:00:00+08:00",
      "travel_id": "travel_hk_2026_06",
      "travel_type": "planned",
      "travel_window_id": "travel_hk_2026_06",
      "type": "planned"
    },
    {
      "available_location_ids": [
        "travel_hotel",
        "remote"
      ],
      "destination": "Tokyo",
      "end": "2026-07-29T21:15:00+09:00",
      "expected_facilities": [
        "basic_hotel_gym",
        "walking_routes",
        "remote_consultation_supported"
      ],
      "limitations": [
        "hotel gym limited equipment",
        "unpredictable meal structure (several client events)",
        "remote-only provider support"
      ],
      "member_location_override": "travel_hotel",
      "notes": "Moderate-resource travel. Meals partly chef-prepped, most fitness sessions require adaptation.",
      "purpose": "Extended board and client visit",
      "start": "2026-07-22T07:15:00+08:00",
      "travel_id": "travel_tokyo_2026_07",
      "travel_type": "planned",
      "travel_window_id": "travel_tokyo_2026_07",
      "type": "planned"
    },
    {
      "available_location_ids": [
        "travel_hotel",
        "remote"
      ],
      "destination": "Jakarta",
      "end": "2026-08-16T21:00:00+07:00",
      "expected_facilities": [
        "hotel_room",
        "remote_consultation_supported"
      ],
      "limitations": [
        "no usable hotel gym",
        "no chef or trusted local providers",
        "most meals restaurant-based",
        "increased work stress and energy drop"
      ],
      "member_location_override": "travel_hotel",
      "notes": "Low-resource travel, mainly supports travel-compatible movement and remote check-ins. Designed to force substitutions and unscheduled support tasks.",
      "purpose": "Urgent client escalation",
      "start": "2026-08-13T06:00:00+08:00",
      "travel_id": "travel_jakarta_2026_08",
      "travel_type": "last_minute",
      "travel_window_id": "travel_jakarta_2026_08",
      "type": "last_minute"
    }
  ],
  "typical_work_hours": {
    "monday_to_friday": {
      "end": "18:30",
      "notes": "In-office core hours; occasional late investor or cross-region calls until 21:00.",
      "start": "08:30"
    },
    "saturday": {
      "end": "12:00",
      "notes": "Catch-up strategy, light work, or personal training/recovery.",
      "start": "09:30"
    },
    "sunday": {
      "end": null,
      "notes": "Reserved for family, meal planning, chef prep, and recovery.",
      "start": null
    }
  }
}
```

---

## resource_universe.json

```json
{
  "equipment": [
    {
      "availability_required": true,
      "display_name": "Home Dumbbells (5-15kg pairs)",
      "equipment_id": "eq_dumbbells_home",
      "equipment_type": "dumbbells_fixed",
      "location_ids": [
        "home"
      ],
      "notes": "Enables modified strength routines at home.",
      "travel_compatible": false
    },
    {
      "availability_required": false,
      "display_name": "Mini Resistance Bands (portable)",
      "equipment_id": "eq_mini_band",
      "equipment_type": "mini_band_portable",
      "location_ids": [
        "gym",
        "home",
        "office",
        "travel_hotel"
      ],
      "notes": "For hotel/office mobility and knee-safe strength work. Often brought during travel.",
      "travel_compatible": true
    },
    {
      "availability_required": false,
      "display_name": "Yoga/Exercise Mat",
      "equipment_id": "eq_yoga_mat",
      "equipment_type": "mat_portable",
      "location_ids": [
        "gym",
        "home",
        "travel_hotel"
      ],
      "notes": "Facilitates stretching and recovery, including post-travel.",
      "travel_compatible": true
    },
    {
      "availability_required": false,
      "display_name": "Concept2 Rower (Gym)",
      "equipment_id": "eq_rower_gym",
      "equipment_type": "rower_fixed",
      "location_ids": [
        "gym"
      ],
      "notes": "Cardio conditioning option for knee-safe aerobic.",
      "travel_compatible": false
    },
    {
      "availability_required": true,
      "display_name": "Selectorized Strength Machines",
      "equipment_id": "eq_strength_machines_gym",
      "equipment_type": "strength_machine_fixed",
      "location_ids": [
        "gym"
      ],
      "notes": "Supports safe, knee-modified resistance sessions.",
      "travel_compatible": false
    },
    {
      "availability_required": false,
      "display_name": "Hotel Pool (Hong Kong)",
      "equipment_id": "eq_pool_hotel_hk",
      "equipment_type": "pool_fixed",
      "location_ids": [
        "travel_hotel"
      ],
      "notes": "Low-impact aerobic and recovery option during HK trip.",
      "travel_compatible": false
    },
    {
      "availability_required": true,
      "display_name": "Basic Hotel Gym Equipment (Tokyo)",
      "equipment_id": "eq_basic_gym_hotel_tokyo",
      "equipment_type": "basic_gym_fixed",
      "location_ids": [
        "travel_hotel"
      ],
      "notes": "Limited hotel gym: free weights up to 10kg, treadmill, and mat.",
      "travel_compatible": false
    },
    {
      "availability_required": false,
      "display_name": "Bodyweight/No Equipment",
      "equipment_id": "eq_bodyweight",
      "equipment_type": "bodyweight",
      "location_ids": [
        "gym",
        "home",
        "office",
        "travel_hotel"
      ],
      "notes": "Always available as fallback. Used for travel-adapted and flare-up recovery routines.",
      "travel_compatible": true
    },
    {
      "availability_required": true,
      "display_name": "Lab Collection Kit (Clinic/Lab)",
      "equipment_id": "eq_lab_kits",
      "equipment_type": "lab_kit_fixed",
      "location_ids": [
        "clinic",
        "lab"
      ],
      "notes": "Synthetic: used for all on-site lab draws.",
      "travel_compatible": false
    },
    {
      "availability_required": true,
      "display_name": "Home Kitchen Prep Area",
      "equipment_id": "eq_kitchen_home",
      "equipment_type": "kitchen_fixed",
      "location_ids": [
        "home"
      ],
      "notes": "Chef and Marcus use for structured meal prep twice per week.",
      "travel_compatible": false
    }
  ],
  "locations": [
    {
      "available_equipment_ids": [
        "eq_lab_kits"
      ],
      "display_name": "Elyx Partner Clinic (Singapore)",
      "location_id": "clinic",
      "location_type": "clinic",
      "notes": "Clinic consults, in-person physician review, and lab draws.",
      "timezone": "Asia/Singapore",
      "travel_compatible": false
    },
    {
      "available_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band",
        "eq_rower_gym",
        "eq_strength_machines_gym",
        "eq_yoga_mat"
      ],
      "display_name": "Preferred Gym (Singapore)",
      "location_id": "gym",
      "location_type": "gym",
      "notes": "Strength, aerobic, and trainer- or physio-led sessions. Most equipment available.",
      "timezone": "Asia/Singapore",
      "travel_compatible": false
    },
    {
      "available_equipment_ids": [
        "eq_bodyweight",
        "eq_dumbbells_home",
        "eq_kitchen_home",
        "eq_mini_band",
        "eq_yoga_mat"
      ],
      "display_name": "Marcus's Home (Singapore)",
      "location_id": "home",
      "location_type": "home",
      "notes": "Primary training, chef prep, and recovery. Physio visits and remote consults available.",
      "timezone": "Asia/Singapore",
      "travel_compatible": false
    },
    {
      "available_equipment_ids": [
        "eq_lab_kits"
      ],
      "display_name": "Core Clinical Lab (Singapore)",
      "location_id": "lab",
      "location_type": "lab",
      "notes": "Primary location for baseline and periodic labs.",
      "timezone": "Asia/Singapore",
      "travel_compatible": false
    },
    {
      "available_equipment_ids": [
        "eq_bodyweight",
        "eq_mini_band"
      ],
      "display_name": "Marcus's Office (Singapore)",
      "location_id": "office",
      "location_type": "office",
      "notes": "Daytime work hours; short, low-complexity movement or remote consult only.",
      "timezone": "Asia/Singapore",
      "travel_compatible": false
    },
    {
      "available_equipment_ids": [],
      "display_name": "Structured Restaurant Meal",
      "location_id": "restaurant",
      "location_type": "restaurant",
      "notes": "Used for structured restaurant meals during normal Singapore weeks when chef-prepped or office delivery meals are unavailable.",
      "timezone": "Asia/Singapore",
      "travel_compatible": false
    },
    {
      "available_equipment_ids": [],
      "display_name": "Remote/Virtual",
      "location_id": "remote",
      "location_type": "remote",
      "notes": "Used for remote consults, telemedicine, or non-specific travel fallback.",
      "timezone": null,
      "travel_compatible": true
    },
    {
      "available_equipment_ids": [
        "eq_basic_gym_hotel_tokyo",
        "eq_bodyweight",
        "eq_mini_band",
        "eq_pool_hotel_hk",
        "eq_yoga_mat"
      ],
      "display_name": "Hotel (Hong Kong)",
      "location_id": "travel_hotel",
      "location_type": "travel_hotel",
      "notes": "High-resource travel: hotel gym and pool. Trainer, dietitian, and remote coach available by remote.; Moderate-resource travel: limited gym, mainly bodyweight and portable gear. Provider pool remote-only.; Low-resource travel: no gym, minimal equipment, remote only.",
      "timezone": "Asia/Hong_Kong",
      "travel_compatible": true
    }
  ],
  "providers": [
    {
      "care_context_supported": [
        "strength",
        "mobility",
        "aerobic",
        "travel_fitness",
        "post_travel_adaptation"
      ],
      "care_team_role": "performance_trainer",
      "continuity_scope": "Owns strength progression, aerobic training adaptations, and trainer-to-physio handoffs.",
      "credentials": [
        "CSCS",
        "corrective_exercise_specialist"
      ],
      "display_name": "Kai Tan",
      "handoff_partner_provider_ids": [
        "provider_physio_01",
        "provider_physician_01",
        "provider_remote_coach_01"
      ],
      "location_ids": [
        "gym",
        "home",
        "office",
        "remote",
        "travel_hotel"
      ],
      "modalities_supported": [
        "in_person",
        "remote",
        "travel_adapted"
      ],
      "notes": "Specializes in data-driven strength and lower-body modified routines. Supports remote coaching and travel adaptation.",
      "provider_id": "provider_trainer_01",
      "provider_type": "trainer",
      "remote_supported": true,
      "specialties": [
        "strength_and_conditioning",
        "knee_safe_training",
        "travel_fitness_adaptation"
      ],
      "team_group": "allied_health",
      "travel_compatible": true
    },
    {
      "care_context_supported": [
        "strength",
        "mobility",
        "knee_safe_training",
        "provider_unavailable_substitution"
      ],
      "care_team_role": "strength_coach",
      "continuity_scope": "Delivers gym-based strength sessions when the primary performance trainer is unavailable; follows Kai's progression plan.",
      "credentials": [
        "CSCS",
        "strength_and_power_coach"
      ],
      "display_name": "Amelia Wong",
      "handoff_partner_provider_ids": [
        "provider_trainer_01",
        "provider_physio_01",
        "provider_remote_coach_01"
      ],
      "location_ids": [
        "gym",
        "home",
        "remote"
      ],
      "modalities_supported": [
        "in_person",
        "remote"
      ],
      "notes": "Secondary strength coach for gym and home sessions; useful when Kai is unavailable or when extra strength coverage is needed.",
      "provider_id": "provider_strength_coach_01",
      "provider_type": "trainer",
      "remote_supported": true,
      "specialties": [
        "gym_strength_progression",
        "resistance_training_technique",
        "knee_safe_loading"
      ],
      "team_group": "allied_health",
      "travel_compatible": false
    },
    {
      "care_context_supported": [
        "travel_fitness",
        "hotel_gym_substitution",
        "bodyweight_conditioning",
        "equipment_unavailable_substitution"
      ],
      "care_team_role": "travel_trainer",
      "continuity_scope": "Delivers remote and hotel-gym substitutions during travel windows; keeps strength/cardio intent intact when facilities change.",
      "credentials": [
        "NASM-CPT",
        "travel_fitness_specialist"
      ],
      "display_name": "Ravi Patel",
      "handoff_partner_provider_ids": [
        "provider_trainer_01",
        "provider_physio_01",
        "provider_remote_coach_01"
      ],
      "location_ids": [
        "remote",
        "travel_hotel"
      ],
      "modalities_supported": [
        "remote",
        "travel_adapted"
      ],
      "notes": "Travel trainer for hotel-gym and remote sessions when Marcus is away from Singapore or normal facilities are unavailable.",
      "provider_id": "provider_travel_trainer_01",
      "provider_type": "trainer",
      "remote_supported": true,
      "specialties": [
        "hotel_gym_training",
        "bodyweight_conditioning",
        "remote_travel_adaptation"
      ],
      "team_group": "allied_health",
      "travel_compatible": true
    },
    {
      "care_context_supported": [
        "mobility",
        "pain_review",
        "post_travel_recovery"
      ],
      "care_team_role": "physiotherapist",
      "continuity_scope": "Owns pain escalation review, movement restrictions, and rehab-to-training progression.",
      "credentials": [
        "MSc Physiotherapy",
        "sports_rehabilitation"
      ],
      "display_name": "Daniel Koh",
      "handoff_partner_provider_ids": [
        "provider_trainer_01",
        "provider_physician_01",
        "provider_remote_coach_01"
      ],
      "location_ids": [
        "clinic",
        "gym",
        "home",
        "office",
        "remote"
      ],
      "modalities_supported": [
        "in_person",
        "remote"
      ],
      "notes": "Knee and lower-back rehab focus. Coordinates handoff with trainer after pain or travel events.",
      "provider_id": "provider_physio_01",
      "provider_type": "physiotherapist",
      "remote_supported": true,
      "specialties": [
        "knee_pain_rehabilitation",
        "lower_back_resilience",
        "post_travel_mobility"
      ],
      "team_group": "allied_health",
      "travel_compatible": false
    },
    {
      "care_context_supported": [
        "nutrition_review",
        "structured_meals",
        "travel_meal_adaptation"
      ],
      "care_team_role": "registered_dietitian",
      "continuity_scope": "Owns structured meal targets, restaurant/travel food strategy, and nutrition interpretation after labs or CGM review.",
      "credentials": [
        "registered_dietitian",
        "sports_nutrition_certificate"
      ],
      "display_name": "Priya Shah",
      "handoff_partner_provider_ids": [
        "provider_physician_01",
        "provider_chef_01",
        "provider_remote_coach_01"
      ],
      "location_ids": [
        "clinic",
        "home",
        "office",
        "remote",
        "travel_hotel"
      ],
      "modalities_supported": [
        "in_person",
        "remote"
      ],
      "notes": "Provides concise nutrition summaries and meal adaptation, especially for travel and restaurant-heavy weeks.",
      "provider_id": "provider_dietitian_01",
      "provider_type": "dietitian",
      "remote_supported": true,
      "specialties": [
        "metabolic_nutrition",
        "CGM_informed_meal_planning",
        "travel_restaurant_strategy"
      ],
      "team_group": "allied_health",
      "travel_compatible": true
    },
    {
      "care_context_supported": [
        "periodic_review",
        "lab_followup",
        "protocol_modification"
      ],
      "care_team_role": "lead_physician",
      "continuity_scope": "Owns clinical interpretation, preventive screening decisions, and escalation guidance for the Allied Health team.",
      "credentials": [
        "MBBS",
        "MRCGP",
        "preventive_medicine"
      ],
      "display_name": "Dr. Aisha Menon",
      "handoff_partner_provider_ids": [
        "provider_dietitian_01",
        "provider_physio_01",
        "provider_trainer_01",
        "provider_lab_01",
        "provider_remote_coach_01"
      ],
      "location_ids": [
        "clinic",
        "office",
        "remote"
      ],
      "modalities_supported": [
        "in_person",
        "remote"
      ],
      "notes": "Concise review and preventive oversight for metabolic and fitness trending. Remote available during travel windows.",
      "provider_id": "provider_physician_01",
      "provider_type": "physician",
      "remote_supported": true,
      "specialties": [
        "preventive_cardiometabolic_medicine",
        "metabolic_risk_review",
        "clinical_protocol_governance"
      ],
      "team_group": "specialist_clinical",
      "travel_compatible": false
    },
    {
      "care_context_supported": [
        "lab_draw",
        "preventive_screening"
      ],
      "care_team_role": "clinical_lab_partner",
      "continuity_scope": "Owns sample collection logistics and passes lab status to physician and dietitian.",
      "credentials": [
        "MOH_registered_lab_partner"
      ],
      "display_name": "Elyx Partner Lab - Singapore",
      "handoff_partner_provider_ids": [
        "provider_physician_01",
        "provider_dietitian_01",
        "provider_remote_coach_01"
      ],
      "location_ids": [
        "clinic",
        "lab"
      ],
      "modalities_supported": [
        "on_site_lab"
      ],
      "notes": "Handles all synthetic baseline labs and periodic screening. Not available during travel or abroad.",
      "provider_id": "provider_lab_01",
      "provider_type": "phlebotomist",
      "remote_supported": false,
      "specialties": [
        "fasted_blood_draw",
        "preventive_biomarker_panel",
        "sample_coordination"
      ],
      "team_group": "clinical_operations",
      "travel_compatible": false
    },
    {
      "care_context_supported": [
        "meal_prep",
        "nutrition_briefing"
      ],
      "care_team_role": "private_chef",
      "continuity_scope": "Executes dietitian meal briefs during non-travel periods; does not provide clinical advice.",
      "credentials": [
        "private_chef",
        "metabolic_meal_prep"
      ],
      "display_name": "Chef Liyang (Home/Local Meals)",
      "handoff_partner_provider_ids": [
        "provider_dietitian_01",
        "provider_remote_coach_01"
      ],
      "location_ids": [
        "home",
        "office"
      ],
      "modalities_supported": [
        "in_person",
        "prepped_dropoff"
      ],
      "notes": "Prepares metabolic-structured meals, up to 2 home-prepped sessions weekly; non-travel periods only.",
      "provider_id": "provider_chef_01",
      "provider_type": "chef",
      "remote_supported": false,
      "specialties": [
        "high_protein_meal_prep",
        "office_meal_delivery",
        "dietitian_brief_execution"
      ],
      "team_group": "lifestyle_support",
      "travel_compatible": false
    },
    {
      "care_context_supported": [
        "adherence_support",
        "recovery_checkin",
        "routine_travel_fallback"
      ],
      "care_team_role": "health_coach",
      "continuity_scope": "Owns weekly behavior coaching, friction resolution, missed-session follow-up, and care-team coordination prompts.",
      "credentials": [
        "NBC-HWC",
        "behavior_change_coaching"
      ],
      "display_name": "Maya Rao",
      "handoff_partner_provider_ids": [
        "provider_physician_01",
        "provider_dietitian_01",
        "provider_physio_01",
        "provider_trainer_01"
      ],
      "location_ids": [
        "remote",
        "travel_hotel"
      ],
      "modalities_supported": [
        "remote"
      ],
      "notes": "Remote pool supports check-ins, fatigue/mobility logs, travel substitutions, and care-team continuity.",
      "provider_id": "provider_remote_coach_01",
      "provider_type": "remote_coach_pool",
      "remote_supported": true,
      "specialties": [
        "behavior_coaching",
        "adherence_barrier_resolution",
        "travel_friction_planning"
      ],
      "team_group": "allied_health",
      "travel_compatible": true
    }
  ],
  "travel_time_rules": [
    {
      "from_location_id": "office",
      "minutes": 15,
      "to_location_id": "gym"
    }
  ],
  "travel_windows": [
    {
      "arrival_fatigue_risk": "moderate",
      "available_location_ids": [
        "remote",
        "travel_hotel"
      ],
      "destination_label": "Hotel (Hong Kong)",
      "end": "2026-06-25T20:00:00+08:00",
      "estimated_travel_duration_hours": 4,
      "member_location_override": "travel_hotel",
      "notes": "Planned high-resource travel. Hotel gym and pool available; care coordination shifts mostly remote except chef-prepped meals.",
      "origin_location_id": "home",
      "start": "2026-06-19T10:00:00+08:00",
      "travel_type": "planned",
      "travel_window_id": "travel_hk_2026_06"
    },
    {
      "arrival_fatigue_risk": "moderate",
      "available_location_ids": [
        "remote",
        "travel_hotel"
      ],
      "destination_label": "Hotel (Tokyo)",
      "end": "2026-07-29T21:15:00+09:00",
      "estimated_travel_duration_hours": 6.5,
      "member_location_override": "travel_hotel",
      "notes": "Moderate-resource travel. Meals partly chef-prepped, most fitness sessions require adaptation.",
      "origin_location_id": "home",
      "start": "2026-07-22T07:15:00+08:00",
      "travel_type": "planned",
      "travel_window_id": "travel_tokyo_2026_07"
    },
    {
      "arrival_fatigue_risk": "high",
      "available_location_ids": [
        "remote",
        "travel_hotel"
      ],
      "destination_label": "Hotel (Jakarta)",
      "end": "2026-08-16T21:00:00+07:00",
      "estimated_travel_duration_hours": 2,
      "member_location_override": "travel_hotel",
      "notes": "Low-resource travel, mainly supports travel-compatible movement and remote check-ins. Designed to force substitutions and unscheduled support tasks.",
      "origin_location_id": "home",
      "start": "2026-08-13T06:00:00+08:00",
      "travel_type": "last_minute",
      "travel_window_id": "travel_jakarta_2026_08"
    }
  ]
}
```

---

## known_frictions.json

```json
{
  "frictions": [
    {
      "affected_travel_window_ids": [
        "travel_hk_2026_06"
      ],
      "date_range": {
        "end": "2026-06-25T20:00:00+08:00",
        "start": "2026-06-19T10:00:00+08:00"
      },
      "description": "During the planned Hong Kong travel window, Marcus has access to a well-equipped hotel gym and pool, enabling most fitness routines. However, there is no in-person trusted physio or lab access, and most provider support is remote. Restaurant meals dominate, with only limited chef-prepped options.",
      "friction_id": "friction_planned_travel_better_facilities_001",
      "name": "Planned Travel with Enhanced Facilities",
      "scheduler_expectation": "Scheduler should prioritize hotel gym/pool for fitness, adapt meal planning to restaurant-heavy context, and route all provider consults to remote. In-person labs and physio sessions should not be scheduled during this window."
    },
    {
      "affected_travel_window_ids": [
        "travel_jakarta_2026_08"
      ],
      "date_range": {
        "end": "2026-08-16T21:00:00+07:00",
        "start": "2026-08-13T06:00:00+08:00"
      },
      "description": "During the urgent Jakarta trip, Marcus only has access to his hotel room and remote support. There is no usable hotel gym, no chef or trusted local providers, and most meals are restaurant-based. Increased work stress and energy drop are expected.",
      "friction_id": "friction_last_minute_travel_limited_facilities_001",
      "name": "Last-Minute Travel with Limited Facilities",
      "scheduler_expectation": "Scheduler should substitute all fitness with bodyweight or portable-band routines, rely on remote coach/dietitian, and expect some activities to be unscheduled or substituted. Structured meal adherence may drop; chef-prepped meals are unavailable."
    },
    {
      "date_range": null,
      "description": "Marcus prefers early morning or early evening sessions for fitness and consultations. However, the Elyx Performance Trainer and Physiotherapist have limited early morning slots, and the Dietitian and Physician are only available during office hours. This causes conflicts with Marcus's preferred exercise and review times.",
      "friction_id": "friction_provider_availability_mismatch_001",
      "linked_resource_ids": [
        "provider_trainer_01",
        "provider_physio_01",
        "provider_dietitian_01",
        "provider_physician_01"
      ],
      "name": "Provider Availability Mismatch with Member Preferences",
      "scheduler_expectation": "Scheduler may need to schedule some sessions outside Marcus's preferred windows or delay/reschedule certain provider-led activities. Expect some member-preferred slots to be unavailable."
    },
    {
      "affected_travel_window_ids": [
        "travel_hk_2026_06",
        "travel_tokyo_2026_07",
        "travel_jakarta_2026_08"
      ],
      "date_range": null,
      "description": "Lab draws and in-person physician reviews are only possible at the Singapore clinic or lab. During all travel windows, these services are unavailable. Remote consults are possible, but labs must be rescheduled.",
      "friction_id": "friction_lab_consult_disruption_travel_001",
      "linked_resource_ids": [
        "provider_lab_01",
        "provider_physician_01",
        "clinic",
        "lab"
      ],
      "name": "Lab or Consultation Disruption During Travel",
      "scheduler_expectation": "Scheduler should avoid scheduling lab draws or in-person physician reviews during travel. If due, these should be rescheduled before or after travel, or substituted with remote consults where possible."
    },
    {
      "affected_travel_window_ids": [
        "travel_hk_2026_06",
        "travel_tokyo_2026_07",
        "travel_jakarta_2026_08"
      ],
      "date_range": null,
      "description": "Structured metabolic meals require either chef-prep at home/office or Marcus to assemble meals himself (up to 2x per week). During travel, chef-prepped meals are unavailable, and Marcus is unwilling to do meal prep in hotel settings.",
      "friction_id": "friction_food_prep_dependency_001",
      "linked_resource_ids": [
        "provider_chef_01",
        "eq_kitchen_home",
        "home",
        "office"
      ],
      "name": "Food Prep Dependency on Chef or Member",
      "scheduler_expectation": "Scheduler should only schedule chef-prepped or member-assembled structured meals at home/office, and use restaurant or travel-compatible meal options during travel. Some structured meal targets may be missed during travel."
    },
    {
      "affected_travel_window_ids": [
        "travel_tokyo_2026_07",
        "travel_jakarta_2026_08"
      ],
      "date_range": null,
      "description": "Certain equipment (e.g., strength machines, rower) and facilities (e.g., gym, pool) are only available at home or gym locations. During the Tokyo trip, the hotel gym has only basic equipment. During Jakarta travel, there is no usable gym at all.",
      "friction_id": "friction_equipment_facility_unavailability_001",
      "linked_resource_ids": [
        "eq_strength_machines_gym",
        "eq_rower_gym",
        "eq_basic_gym_hotel_tokyo",
        "eq_pool_hotel_hk",
        "gym",
        "travel_hotel"
      ],
      "name": "Equipment or Facility Unavailability",
      "scheduler_expectation": "Scheduler should substitute unavailable equipment with bodyweight or portable-band routines during travel, and avoid scheduling equipment-dependent activities in locations where the equipment is not present."
    },
    {
      "affected_travel_window_ids": [
        "travel_hk_2026_06",
        "travel_tokyo_2026_07"
      ],
      "date_range": null,
      "description": "After travel windows involving flights over 3 hours (e.g., Singapore to Hong Kong or Tokyo), Marcus experiences moderate fatigue and lower-back tightness. High-load or lower-body training should be avoided for 24 hours post-arrival.",
      "friction_id": "friction_post_travel_fatigue_001",
      "name": "Post-Travel Fatigue After Location Change Over 3 Hours",
      "scheduler_expectation": "Scheduler should avoid scheduling high-load or heavy lower-body activities for 24 hours after arrival, and instead prioritize mobility, stretching, or recovery sessions."
    },
    {
      "date_range": null,
      "description": "If Marcus skips or substitutes a high-load strength or aerobic session (especially after travel or during pain escalation), the plan should automatically schedule a recovery or mobility session and flag for care-team follow-up.",
      "friction_id": "friction_skipped_high_load_recovery_adjustment_001",
      "linked_resource_ids": [
        "provider_trainer_01",
        "provider_physio_01",
        "eq_bodyweight",
        "eq_mini_band"
      ],
      "name": "Skipped or Substituted High-Load Activity Requiring Recovery Adjustment",
      "scheduler_expectation": "Scheduler should detect skipped or substituted high-load activities and insert appropriate recovery/mobility sessions, possibly triggering a remote coach or physio check-in."
    }
  ]
}
```

---

## goal_action_budget.json

```json
{
  "batch_budgets": [
    {
      "batch_id": "001_metabolic_nutrition",
      "prefix": "b01_nutrition",
      "primary_family_budget": 12,
      "theme": "metabolic nutrition, structured meals, meal-source logic, supplements or medication tied to food, CGM or hydration support, and travel meal substitutions"
    },
    {
      "batch_id": "002_cardiorespiratory_fitness",
      "prefix": "b02_cardio",
      "primary_family_budget": 10,
      "theme": "cardiorespiratory fitness, zone 2 work, swimming, cycling, rowing, walking, metabolic conditioning, and travel-safe aerobic substitutions"
    },
    {
      "batch_id": "003_strength_mobility_pain",
      "prefix": "b03_strength",
      "primary_family_budget": 10,
      "theme": "strength, mobility, knee-safe training, physiotherapy-informed pain resilience, hotel or home substitutions, and lower-load adjustments"
    },
    {
      "batch_id": "004_recovery_sleep_stress",
      "prefix": "b04_recovery",
      "primary_family_budget": 8,
      "theme": "recovery, sleep, fatigue management, stress regulation, evening routines, post-travel adjustment, and therapy modalities"
    },
    {
      "batch_id": "005_clinical_review_measurement",
      "prefix": "b05_clinical",
      "primary_family_budget": 10,
      "theme": "clinical review, lab measurements, fasting prerequisites, biometric checks, physician and dietitian review, physiotherapy reassessment, trainer handoff, and care coordination"
    }
  ],
  "global_rules": [
    "Generate an activity-family blueprint before generating full activity-family JSON.",
    "The blueprint is the semantic plan for the board: goal math, primary roles, meal slots, substitutions, and travel context.",
    "Travel is an adaptation context. It should not create a standalone goal denominator except for support-only tracking.",
    "Support, prep, reminders, logs, and medication protocols should not inflate core goal coverage.",
    "Substitutions must preserve the same family intent and only appear after a primary activity is blocked by travel, provider, equipment, facility, fatigue, pain, prep, or time constraints.",
    "Food coverage must be represented by meal activities, not supplements. Breakfast, lunch, and dinner should be explicit where relevant.",
    "Generation should avoid creating multiple normal-week primary activities for the same meal slot unless they apply to different contexts such as weekday, weekend, office, or travel."
  ],
  "goal_action_budgets": [
    {
      "allowed_primary_intents": [
        "breakfast",
        "lunch",
        "dinner",
        "travel_meal",
        "fasting_aware_meal"
      ],
      "canonical_meal_slots": [
        "breakfast",
        "lunch",
        "dinner"
      ],
      "goal_action_id": "ga_structured_meals_weekly",
      "max_counting_primary_weekly_frequency": 14,
      "notes": "Meals count. Supplements, chef prep, and meal-planning support do not count. Travel meals should usually be substitutions or travel-scoped families that also satisfy this underlying action.",
      "primary_family_budget": 12,
      "role": "core",
      "support_family_budget": 3,
      "target": {
        "period": "weekly",
        "unit_label": "meals",
        "units": 14
      },
      "travel_primary_allowed": false
    },
    {
      "allowed_primary_intents": [
        "zone2",
        "swim",
        "bike",
        "walk",
        "travel_cardio_substitution"
      ],
      "canonical_meal_slots": [],
      "goal_action_id": "ga_aerobic_conditioning_weekly",
      "max_counting_primary_weekly_frequency": 2,
      "notes": "Normal weeks should target two cardio sessions, not several parallel cardio prescriptions. Travel variants should be substitutions unless the whole family is explicitly travel-scoped.",
      "primary_family_budget": 8,
      "role": "core",
      "support_family_budget": 2,
      "target": {
        "period": "weekly",
        "unit_label": "sessions",
        "units": 2
      },
      "travel_primary_allowed": false
    },
    {
      "allowed_primary_intents": [
        "trainer_strength",
        "hotel_gym_strength",
        "home_strength",
        "lower_load_strength_substitution"
      ],
      "canonical_meal_slots": [],
      "goal_action_id": "ga_strength_sessions_weekly",
      "max_counting_primary_weekly_frequency": 2,
      "notes": "Strength should be a coherent weekly progression. Mobility is support unless it explicitly substitutes after pain, fatigue, or travel.",
      "primary_family_budget": 8,
      "role": "core",
      "support_family_budget": 3,
      "target": {
        "period": "weekly",
        "unit_label": "sessions",
        "units": 2
      },
      "travel_primary_allowed": false
    },
    {
      "allowed_primary_intents": [
        "sleep_routine",
        "evening_recovery",
        "post_travel_recovery",
        "fatigue_adjustment"
      ],
      "canonical_meal_slots": [],
      "goal_action_id": "ga_sleep_recovery_weekly",
      "max_counting_primary_weekly_frequency": 4,
      "notes": "Recovery actions can count, but logging and reminders are support-only.",
      "primary_family_budget": 8,
      "role": "recovery",
      "support_family_budget": 3,
      "target": {
        "period": "weekly",
        "unit_label": "actions",
        "units": 4
      },
      "travel_primary_allowed": true
    },
    {
      "allowed_primary_intents": [
        "lab",
        "physician_review",
        "dietitian_review",
        "physio_assessment",
        "care_team_review"
      ],
      "canonical_meal_slots": [],
      "goal_action_id": "ga_clinical_review_3month",
      "max_counting_primary_weekly_frequency": 1,
      "notes": "This is due-week logic, not a normal every-week denominator. Labs should create prerequisites for review.",
      "primary_family_budget": 8,
      "role": "measurement",
      "support_family_budget": 2,
      "target": {
        "period": "3_month",
        "unit_label": "reviews",
        "units": 4
      },
      "travel_primary_allowed": false
    },
    {
      "allowed_primary_intents": [
        "supplement_protocol",
        "hydration",
        "cgm_log",
        "adherence_check",
        "meal_linked_protocol"
      ],
      "canonical_meal_slots": [],
      "goal_action_id": "ga_adherence_support_weekly",
      "max_counting_primary_weekly_frequency": 0,
      "notes": "Support-only. These activities may be scheduled and audited but should not count as core outcome progress.",
      "primary_family_budget": 8,
      "role": "support",
      "support_family_budget": 8,
      "target": {
        "period": "weekly",
        "unit_label": "protocol checks",
        "units": 7
      },
      "travel_primary_allowed": true
    },
    {
      "allowed_primary_intents": [
        "remote_handoff",
        "provider_review",
        "lab_followup",
        "plan_adjustment"
      ],
      "canonical_meal_slots": [],
      "goal_action_id": "ga_care_team_followthrough_3month",
      "max_counting_primary_weekly_frequency": 0,
      "notes": "Care-team follow-through touchpoints that count as explicit consultations.",
      "primary_family_budget": 4,
      "role": "care_team",
      "support_family_budget": 4,
      "target": {
        "period": "3_month",
        "unit_label": "touchpoints",
        "units": 6
      },
      "travel_primary_allowed": true
    },
    {
      "allowed_primary_intents": [
        "adherence_checkin",
        "friction_resolution",
        "travel_support",
        "meal_prep_failure_resolution"
      ],
      "canonical_meal_slots": [],
      "goal_action_id": "ga_behavior_coaching_weekly",
      "max_counting_primary_weekly_frequency": 1,
      "notes": "Member-facing behavior coaching and friction-resolution touchpoints.",
      "primary_family_budget": 4,
      "role": "coaching",
      "support_family_budget": 6,
      "target": {
        "period": "weekly",
        "unit_label": "touchpoints",
        "units": 1
      },
      "travel_primary_allowed": true
    }
  ],
  "minimum_primary_family_count": 50,
  "total_primary_family_budget": 50,
  "version": "2026-05-27"
}
```

---

## Batch Scope

# Batch Scope

Batch ID prefix: `b05_clinical`.

Care domain: 005_clinical_review_measurement.

Theme: clinical review, lab measurements, fasting prerequisites, biometric checks, physician and dietitian review, physiotherapy reassessment, trainer handoff, and care coordination.

Generate exactly 10 activity families. Each family must have exactly one primary activity. Include 0-3 substitutions only when realistic.

Minimum scheduler-facing activities in this batch: 20.

Priority range: 331-430.

Existing activity summaries from previous accepted batches:

```json
[
  {
    "activity_family_id": "b01_nutrition_breakfast_chef_home",
    "activity_type": "food",
    "allowed_locations": [
      "home"
    ],
    "goal_action_ids": [
      "ga_structured_meals_weekly"
    ],
    "intent": "breakfast",
    "meal_slot": "breakfast",
    "primary_activity_id": "act_b01_breakfast_chef_home_primary",
    "primary_title": "Chef-prepared high-protein breakfast"
  },
  {
    "activity_family_id": "b01_nutrition_breakfast_office_delivery",
    "activity_type": "food",
    "allowed_locations": [
      "office"
    ],
    "goal_action_ids": [
      "ga_structured_meals_weekly"
    ],
    "intent": "breakfast",
    "meal_slot": "breakfast",
    "primary_activity_id": "act_b01_breakfast_office_delivery_primary",
    "primary_title": "Office-delivered breakfast"
  },
  {
    "activity_family_id": "b01_nutrition_breakfast_travel_hotel",
    "activity_type": "food",
    "allowed_locations": [
      "travel_hotel"
    ],
    "goal_action_ids": [
      "ga_structured_meals_weekly"
    ],
    "intent": "breakfast",
    "meal_slot": "breakfast",
    "primary_activity_id": "act_b01_breakfast_travel_hotel_primary",
    "primary_title": "Hotel buffet or room-service breakfast (travel)"
  },
  {
    "activity_family_id": "b01_nutrition_lunch_office_delivery",
    "activity_type": "food",
    "allowed_locations": [
      "office"
    ],
    "goal_action_ids": [
      "ga_structured_meals_weekly"
    ],
    "intent": "lunch",
    "meal_slot": "lunch",
    "primary_activity_id": "act_b01_lunch_office_delivery_primary",
    "primary_title": "Chef-prepped or delivered office lunch"
  },
  {
    "activity_family_id": "b01_nutrition_lunch_restaurant_travel",
    "activity_type": "food",
    "allowed_locations": [
      "travel_hotel"
    ],
    "goal_action_ids": [
      "ga_structured_meals_weekly"
    ],
    "intent": "lunch",
    "meal_slot": "lunch",
    "primary_activity_id": "act_b01_lunch_restaurant_travel_primary",
    "primary_title": "Restaurant or hotel lunch (travel)"
  },
  {
    "activity_family_id": "b01_nutrition_lunch_member_assembled_home",
    "activity_type": "food",
    "allowed_locations": [
      "home"
    ],
    "goal_action_ids": [
      "ga_structured_meals_weekly"
    ],
    "intent": "lunch",
    "meal_slot": "lunch",
    "primary_activity_id": "act_b01_lunch_member_assembled_home_primary",
    "primary_title": "Member-assembled lunch at home"
  },
  {
    "activity_family_id": "b01_nutrition_dinner_chef_home",
    "activity_type": "food",
    "allowed_locations": [
      "home"
    ],
    "goal_action_ids": [
      "ga_structured_meals_weekly"
    ],
    "intent": "dinner",
    "meal_slot": "dinner",
    "primary_activity_id": "act_b01_dinner_chef_home_primary",
    "primary_title": "Chef-prepared dinner at home"
  },
  {
    "activity_family_id": "b01_nutrition_dinner_restaurant",
    "activity_type": "food",
    "allowed_locations": [
      "restaurant"
    ],
    "goal_action_ids": [
      "ga_structured_meals_weekly"
    ],
    "intent": "dinner",
    "meal_slot": "dinner",
    "primary_activity_id": "act_b01_dinner_restaurant_primary",
    "primary_title": "Structured restaurant dinner"
  },
  {
    "activity_family_id": "b01_nutrition_dinner_travel_hotel",
    "activity_type": "food",
    "allowed_locations": [
      "travel_hotel"
    ],
    "goal_action_ids": [
      "ga_structured_meals_weekly"
    ],
    "intent": "dinner",
    "meal_slot": "dinner",
    "primary_activity_id": "act_b01_dinner_travel_hotel_primary",
    "primary_title": "Hotel or restaurant dinner (travel)"
  },
  {
    "activity_family_id": "b01_nutrition_fasting_aware_meal_support",
    "activity_type": "food",
    "allowed_locations": [
      "home"
    ],
    "goal_action_ids": [
      "ga_structured_meals_weekly"
    ],
    "intent": "fasting_aware_meal",
    "meal_slot": null,
    "primary_activity_id": "act_b01_fasting_aware_meal_support_primary",
    "primary_title": "Fasting-aware meal timing support"
  },
  {
    "activity_family_id": "b01_nutrition_supplement_protocol_support",
    "activity_type": "medication",
    "allowed_locations": [
      "home",
      "office",
      "travel_hotel"
    ],
    "goal_action_ids": [
      "ga_adherence_support_weekly"
    ],
    "intent": "supplement_protocol",
    "meal_slot": null,
    "primary_activity_id": "act_b01_supplement_protocol_support_primary",
    "primary_title": "Daily supplement protocol with breakfast or dinner"
  },
  {
    "activity_family_id": "b01_nutrition_travel_meal_adherence_check",
    "activity_type": "consultation",
    "allowed_locations": [
      "remote"
    ],
    "goal_action_ids": [
      "ga_behavior_coaching_weekly"
    ],
    "intent": "travel_support",
    "meal_slot": null,
    "primary_activity_id": "act_b01_travel_meal_adherence_check_primary",
    "primary_title": "Remote meal adherence check-in (travel)"
  },
  {
    "activity_family_id": "b02_cardio_zone2_gym",
    "activity_type": "fitness",
    "allowed_locations": [
      "gym"
    ],
    "goal_action_ids": [
      "ga_aerobic_conditioning_weekly"
    ],
    "intent": "zone2",
    "meal_slot": null,
    "primary_activity_id": "act_b02_cardio_zone2_gym_primary",
    "primary_title": "Zone 2 aerobic session at gym (rower or bike)"
  },
  {
    "activity_family_id": "b02_cardio_zone2_home",
    "activity_type": "fitness",
    "allowed_locations": [
      "home"
    ],
    "goal_action_ids": [
      "ga_aerobic_conditioning_weekly"
    ],
    "intent": "zone2",
    "meal_slot": null,
    "primary_activity_id": "act_b02_cardio_zone2_home_primary",
    "primary_title": "Zone 2 aerobic session at home (cycling or brisk walk)"
  },
  {
    "activity_family_id": "b02_cardio_zone2_travel_hotel_gym",
    "activity_type": "fitness",
    "allowed_locations": [
      "travel_hotel"
    ],
    "goal_action_ids": [
      "ga_aerobic_conditioning_weekly",
      "ga_behavior_coaching_weekly"
    ],
    "intent": "travel_cardio_substitution",
    "meal_slot": null,
    "primary_activity_id": "act_b02_cardio_zone2_travel_hotel_gym_primary",
    "primary_title": "Aerobic session in hotel gym (bike or treadmill)"
  },
  {
    "activity_family_id": "b02_cardio_zone2_travel_bodyweight",
    "activity_type": "fitness",
    "allowed_locations": [
      "travel_hotel"
    ],
    "goal_action_ids": [
      "ga_aerobic_conditioning_weekly",
      "ga_behavior_coaching_weekly"
    ],
    "intent": "travel_cardio_substitution",
    "meal_slot": null,
    "primary_activity_id": "act_b02_cardio_zone2_travel_bodyweight_primary",
    "primary_title": "Bodyweight aerobic session in hotel room"
  },
  {
    "activity_family_id": "b02_cardio_swim_pool_hotel_hk",
    "activity_type": "fitness",
    "allowed_locations": [
      "travel_hotel"
    ],
    "goal_action_ids": [
      "ga_aerobic_conditioning_weekly",
      "ga_behavior_coaching_weekly"
    ],
    "intent": "swim",
    "meal_slot": null,
    "primary_activity_id": "act_b02_cardio_swim_pool_hotel_hk_primary",
    "primary_title": "Swimming aerobic session in hotel pool (Hong Kong)"
  },
  {
    "activity_family_id": "b02_cardio_walking_office",
    "activity_type": "fitness",
    "allowed_locations": [
      "office"
    ],
    "goal_action_ids": [
      "ga_aerobic_conditioning_weekly"
    ],
    "intent": "walk",
    "meal_slot": null,
    "primary_activity_id": "act_b02_cardio_walking_office_primary",
    "primary_title": "Short walking or movement break at office"
  },
  {
    "activity_family_id": "b02_cardio_remote_coach_progression_review",
    "activity_type": "consultation",
    "allowed_locations": [
      "remote"
    ],
    "goal_action_ids": [
      "ga_aerobic_conditioning_weekly"
    ],
    "intent": "remote_handoff",
    "meal_slot": null,
    "primary_activity_id": "act_b02_cardio_remote_coach_progression_review_primary",
    "primary_title": "Remote coach review of aerobic progression"
  },
  {
    "activity_family_id": "b02_cardio_cgm_log_support",
    "activity_type": "medication",
    "allowed_locations": [
      "home",
      "office",
      "travel_hotel"
    ],
    "goal_action_ids": [
      "ga_adherence_support_weekly"
    ],
    "intent": "cgm_log",
    "meal_slot": null,
    "primary_activity_id": "act_b02_cardio_cgm_log_support_primary",
    "primary_title": "CGM check and log (as needed)"
  },
  {
    "activity_family_id": "b02_cardio_hydration_protocol_support",
    "activity_type": "medication",
    "allowed_locations": [
      "home",
      "travel_hotel",
      "office"
    ],
    "goal_action_ids": [
      "ga_adherence_support_weekly"
    ],
    "intent": "hydration",
    "meal_slot": null,
    "primary_activity_id": "act_b02_cardio_hydration_protocol_support_primary",
    "primary_title": "Hydration and electrolyte protocol (especially during travel)"
  },
  {
    "activity_family_id": "b02_cardio_facility_unavailable_cardio_substitution",
    "activity_type": "fitness",
    "allowed_locations": [
      "home",
      "travel_hotel",
      "office"
    ],
    "goal_action_ids": [
      "ga_aerobic_conditioning_weekly"
    ],
    "intent": "facility_unavailable_cardio_substitution",
    "meal_slot": null,
    "primary_activity_id": "act_b02_cardio_facility_unavailable_cardio_substitution_primary",
    "primary_title": "Aerobic session using bodyweight/bands (facility unavailable)"
  },
  {
    "activity_family_id": "b03_strength_trainer_gym",
    "activity_type": "fitness",
    "allowed_locations": [
      "gym"
    ],
    "goal_action_ids": [
      "ga_strength_sessions_weekly"
    ],
    "intent": "trainer_strength",
    "meal_slot": null,
    "primary_activity_id": "act_b03_strength_trainer_gym_primary",
    "primary_title": "Trainer-led knee-safe strength session at gym"
  },
  {
    "activity_family_id": "b03_strength_home_strength",
    "activity_type": "fitness",
    "allowed_locations": [
      "home"
    ],
    "goal_action_ids": [
      "ga_strength_sessions_weekly"
    ],
    "intent": "home_strength",
    "meal_slot": null,
    "primary_activity_id": "act_b03_strength_home_strength_primary",
    "primary_title": "Home-based knee-safe strength session"
  },
  {
    "activity_family_id": "b03_strength_hotel_gym_strength",
    "activity_type": "fitness",
    "allowed_locations": [
      "travel_hotel"
    ],
    "goal_action_ids": [
      "ga_strength_sessions_weekly"
    ],
    "intent": "hotel_gym_strength",
    "meal_slot": null,
    "primary_activity_id": "act_b03_strength_hotel_gym_strength_primary",
    "primary_title": "Hotel gym strength session (travel window)"
  },
  {
    "activity_family_id": "b03_strength_bodyweight_travel_substitution",
    "activity_type": "fitness",
    "allowed_locations": [
      "travel_hotel"
    ],
    "goal_action_ids": [
      "ga_strength_sessions_weekly",
      "ga_behavior_coaching_weekly"
    ],
    "intent": "lower_load_strength_substitution",
    "meal_slot": null,
    "primary_activity_id": "act_b03_strength_bodyweight_travel_substitution_primary",
    "primary_title": "Bodyweight/band strength session (low-resource travel)"
  },
  {
    "activity_family_id": "b03_strength_mobility_post_travel",
    "activity_type": "therapy",
    "allowed_locations": [
      "home"
    ],
    "goal_action_ids": [
      "ga_sleep_recovery_weekly",
      "ga_strength_sessions_weekly"
    ],
    "intent": "post_travel_recovery",
    "meal_slot": null,
    "primary_activity_id": "act_b03_strength_mobility_post_travel_primary",
    "primary_title": "Mobility and recovery session after travel"
  },
  {
    "activity_family_id": "b03_strength_physio_assessment_due",
    "activity_type": "consultation",
    "allowed_locations": [
      "home",
      "gym",
      "clinic"
    ],
    "goal_action_ids": [
      "ga_clinical_review_3month"
    ],
    "intent": "physio_assessment",
    "meal_slot": null,
    "primary_activity_id": "act_b03_strength_physio_assessment_due_primary",
    "primary_title": "Initial physiotherapist assessment"
  },
  {
    "activity_family_id": "b03_strength_trainer_remote_substitution",
    "activity_type": "fitness",
    "allowed_locations": [
      "home",
      "remote",
      "travel_hotel"
    ],
    "goal_action_ids": [
      "ga_strength_sessions_weekly"
    ],
    "intent": "trainer_strength",
    "meal_slot": null,
    "primary_activity_id": "act_b03_strength_trainer_remote_substitution_primary",
    "primary_title": "Remote trainer-led strength session (as-needed)"
  },
  {
    "activity_family_id": "b03_strength_lower_load_strength_adjustment",
    "activity_type": "fitness",
    "allowed_locations": [
      "home"
    ],
    "goal_action_ids": [
      "ga_strength_sessions_weekly"
    ],
    "intent": "lower_load_strength_substitution",
    "meal_slot": null,
    "primary_activity_id": "act_b03_strength_lower_load_strength_adjustment_primary",
    "primary_title": "Lower-load strength session after pain or fatigue"
  },
  {
    "activity_family_id": "b03_strength_mobility_pain_recovery_checkin",
    "activity_type": "consultation",
    "allowed_locations": [
      "remote",
      "travel_hotel"
    ],
    "goal_action_ids": [
      "ga_care_team_followthrough_3month"
    ],
    "intent": "remote_handoff",
    "meal_slot": null,
    "primary_activity_id": "act_b03_strength_mobility_pain_recovery_checkin_primary",
    "primary_title": "Remote coach or physio check-in after travel or skipped session"
  },
  {
    "activity_family_id": "b03_strength_provider_unavailable_strength_substitution",
    "activity_type": "fitness",
    "allowed_locations": [
      "home",
      "remote",
      "travel_hotel"
    ],
    "goal_action_ids": [
      "ga_strength_sessions_weekly"
    ],
    "intent": "provider_unavailable_strength_substitution",
    "meal_slot": null,
    "primary_activity_id": "act_b03_strength_provider_unavailable_strength_substitution_primary",
    "primary_title": "Knee-safe strength session when trainer unavailable"
  },
  {
    "activity_family_id": "b04_recovery_evening_mobility_home",
    "activity_type": "therapy",
    "allowed_locations": [
      "home"
    ],
    "goal_action_ids": [
      "ga_sleep_recovery_weekly"
    ],
    "intent": "evening_recovery",
    "meal_slot": null,
    "primary_activity_id": "act_b04_recovery_evening_mobility_home_primary",
    "primary_title": "Evening home-based mobility and recovery session"
  },
  {
    "activity_family_id": "b04_recovery_evening_mobility_travel",
    "activity_type": "therapy",
    "allowed_locations": [
      "travel_hotel"
    ],
    "goal_action_ids": [
      "ga_sleep_recovery_weekly",
      "ga_behavior_coaching_weekly"
    ],
    "intent": "evening_recovery",
    "meal_slot": null,
    "primary_activity_id": "act_b04_recovery_evening_mobility_travel_primary",
    "primary_title": "Hotel-based evening mobility and recovery session"
  },
  {
    "activity_family_id": "b04_recovery_sleep_routine_support",
    "activity_type": "therapy",
    "allowed_locations": [
      "home"
    ],
    "goal_action_ids": [
      "ga_sleep_recovery_weekly"
    ],
    "intent": "sleep_routine",
    "meal_slot": null,
    "primary_activity_id": "act_b04_recovery_sleep_routine_support_primary",
    "primary_title": "Home-based sleep wind-down routine"
  },
  {
    "activity_family_id": "b04_recovery_post_travel_fatigue_adjustment",
    "activity_type": "therapy",
    "allowed_locations": [
      "home"
    ],
    "goal_action_ids": [
      "ga_sleep_recovery_weekly",
      "ga_behavior_coaching_weekly"
    ],
    "intent": "post_travel_recovery",
    "meal_slot": null,
    "primary_activity_id": "act_b04_recovery_post_travel_fatigue_adjustment_primary",
    "primary_title": "Post-travel fatigue recovery session at home"
  },
  {
    "activity_family_id": "b04_recovery_breathwork_support",
    "activity_type": "therapy",
    "allowed_locations": [
      "home"
    ],
    "goal_action_ids": [
      "ga_sleep_recovery_weekly"
    ],
    "intent": "fatigue_adjustment",
    "meal_slot": null,
    "primary_activity_id": "act_b04_recovery_breathwork_support_primary",
    "primary_title": "Breathwork or stress regulation session"
  },
  {
    "activity_family_id": "b04_recovery_remote_coach_recovery_checkin",
    "activity_type": "consultation",
    "allowed_locations": [
      "remote",
      "travel_hotel"
    ],
    "goal_action_ids": [
      "ga_care_team_followthrough_3month"
    ],
    "intent": "remote_handoff",
    "meal_slot": null,
    "primary_activity_id": "act_b04_recovery_remote_coach_recovery_checkin_primary",
    "primary_title": "Remote coach check-in for recovery and sleep (travel)"
  },
  {
    "activity_family_id": "b04_recovery_evening_routine_travel",
    "activity_type": "therapy",
    "allowed_locations": [
      "travel_hotel"
    ],
    "goal_action_ids": [
      "ga_sleep_recovery_weekly"
    ],
    "intent": "sleep_routine",
    "meal_slot": null,
    "primary_activity_id": "act_b04_recovery_evening_routine_travel_primary",
    "primary_title": "Hotel-based evening sleep routine"
  },
  {
    "activity_family_id": "b04_recovery_load_adjustment_after_poor_sleep",
    "activity_type": "therapy",
    "allowed_locations": [
      "home"
    ],
    "goal_action_ids": [
      "ga_sleep_recovery_weekly"
    ],
    "intent": "poor_sleep_load_adjustment",
    "meal_slot": null,
    "primary_activity_id": "act_b04_recovery_load_adjustment_after_poor_sleep_primary",
    "primary_title": "Load adjustment and recovery protocol after poor sleep"
  }
]
```

Approved activity family blueprints for this batch:

```json
[
  {
    "activity_family_id": "b05_clinical_lab_draw_due_week",
    "batch_id": "005_clinical_review_measurement",
    "care_domain": "consultation",
    "family_target": {
      "goal_action_id": "ga_clinical_review_3month",
      "period": "3_month",
      "substitutions_count": 1,
      "support_counts": false,
      "target_units": 1,
      "unit_label": "reviews"
    },
    "goal_action_ids": [
      "ga_clinical_review_3month"
    ],
    "location_strategy": "clinic",
    "meal_slot": null,
    "phase_scope": [
      "phase_marcus_001",
      "phase_marcus_007"
    ],
    "primary_activity_type": "consultation",
    "primary_counts_toward_weekly_target": false,
    "primary_frequency": {
      "cadence": "due-week",
      "count": 0,
      "days": [],
      "window": "lab-due"
    },
    "primary_intent": "lab",
    "primary_role": "measurement",
    "primary_weekly_frequency_estimate": 0,
    "semantic_notes": [
      "Lab draw at clinic during due week for metabolic review.",
      "Reschedule if travel or facility unavailable."
    ],
    "substitution_count": 1,
    "substitution_reason_codes": [
      "travel_window",
      "facility_unavailable",
      "time_conflict"
    ],
    "travel_context": false
  },
  {
    "activity_family_id": "b05_clinical_physician_review_due_week",
    "batch_id": "005_clinical_review_measurement",
    "care_domain": "consultation",
    "family_target": {
      "goal_action_id": "ga_care_team_followthrough_3month",
      "period": "3_month",
      "substitutions_count": 1,
      "support_counts": false,
      "target_units": 1,
      "unit_label": "reviews"
    },
    "goal_action_ids": [
      "ga_clinical_review_3month"
    ],
    "location_strategy": "clinic",
    "meal_slot": null,
    "phase_scope": [
      "phase_marcus_001",
      "phase_marcus_007"
    ],
    "primary_activity_type": "consultation",
    "primary_counts_toward_weekly_target": false,
    "primary_frequency": {
      "cadence": "due-week",
      "count": 0,
      "days": [],
      "window": "review-due"
    },
    "primary_intent": "physician_review",
    "primary_role": "measurement",
    "primary_weekly_frequency_estimate": 0,
    "semantic_notes": [
      "Physician review after labs during due week.",
      "Substitute with remote review if travel or provider unavailable."
    ],
    "substitution_count": 1,
    "substitution_reason_codes": [
      "travel_window",
      "provider_unavailable",
      "remote_delivery_needed"
    ],
    "travel_context": false
  },
  {
    "activity_family_id": "b05_clinical_dietitian_review_monthly",
    "batch_id": "005_clinical_review_measurement",
    "care_domain": "consultation",
    "family_target": {
      "goal_action_id": "ga_clinical_review_3month",
      "period": "3_month",
      "substitutions_count": 1,
      "support_counts": false,
      "target_units": 1,
      "unit_label": "reviews"
    },
    "goal_action_ids": [
      "ga_clinical_review_3month"
    ],
    "location_strategy": "home",
    "meal_slot": null,
    "phase_scope": [
      "phase_marcus_001",
      "phase_marcus_003",
      "phase_marcus_007"
    ],
    "primary_activity_type": "consultation",
    "primary_counts_toward_weekly_target": false,
    "primary_frequency": {
      "cadence": "monthly",
      "count": 0,
      "days": [],
      "window": "monthly"
    },
    "primary_intent": "dietitian_review",
    "primary_role": "measurement",
    "primary_weekly_frequency_estimate": 0,
    "semantic_notes": [
      "Dietitian review monthly for nutrition and meal adaptation.",
      "Substitute with remote review if provider unavailable or during travel."
    ],
    "substitution_count": 1,
    "substitution_reason_codes": [
      "provider_unavailable",
      "remote_delivery_needed"
    ],
    "travel_context": false
  },
  {
    "activity_family_id": "b05_clinical_physio_reassessment_post_travel",
    "batch_id": "005_clinical_review_measurement",
    "care_domain": "consultation",
    "family_target": {
      "goal_action_id": "ga_care_team_followthrough_3month",
      "period": "3_month",
      "substitutions_count": 1,
      "support_counts": false,
      "target_units": 1,
      "unit_label": "reviews"
    },
    "goal_action_ids": [
      "ga_clinical_review_3month"
    ],
    "location_strategy": "remote",
    "meal_slot": null,
    "phase_scope": [
      "phase_marcus_002",
      "phase_marcus_004",
      "phase_marcus_006"
    ],
    "primary_activity_type": "consultation",
    "primary_counts_toward_weekly_target": false,
    "primary_frequency": {
      "cadence": "post-travel",
      "count": 0,
      "days": [],
      "window": "travel"
    },
    "primary_intent": "physio_assessment",
    "primary_role": "measurement",
    "primary_weekly_frequency_estimate": 0,
    "semantic_notes": [
      "Physio reassessment after travel or pain escalation.",
      "Remote if provider unavailable or travel context."
    ],
    "substitution_count": 1,
    "substitution_reason_codes": [
      "travel_window",
      "provider_unavailable",
      "remote_delivery_needed"
    ],
    "travel_context": true
  },
  {
    "activity_family_id": "b05_clinical_lab_reschedule_coordination",
    "batch_id": "005_clinical_review_measurement",
    "care_domain": "consultation",
    "family_target": {
      "goal_action_id": "ga_care_team_followthrough_3month",
      "period": "3_month",
      "substitutions_count": 0,
      "support_counts": false,
      "target_units": 0,
      "unit_label": "reviews"
    },
    "goal_action_ids": [
      "ga_clinical_review_3month"
    ],
    "location_strategy": "remote",
    "meal_slot": null,
    "phase_scope": [
      "phase_marcus_002",
      "phase_marcus_004",
      "phase_marcus_006"
    ],
    "primary_activity_type": "consultation",
    "primary_counts_toward_weekly_target": false,
    "primary_frequency": {
      "cadence": "as_needed",
      "count": 0,
      "days": [],
      "window": "lab-reschedule"
    },
    "primary_intent": "care_team_review",
    "primary_role": "support",
    "primary_weekly_frequency_estimate": 0,
    "semantic_notes": [
      "Care-team coordination for lab rescheduling if travel or facility unavailable.",
      "Support-only; does not count as a review."
    ],
    "substitution_count": 0,
    "substitution_reason_codes": [],
    "travel_context": true
  },
  {
    "activity_family_id": "b05_clinical_biometric_review_support",
    "batch_id": "005_clinical_review_measurement",
    "care_domain": "consultation",
    "family_target": {
      "goal_action_id": "ga_care_team_followthrough_3month",
      "period": "3_month",
      "substitutions_count": 0,
      "support_counts": false,
      "target_units": 0,
      "unit_label": "reviews"
    },
    "goal_action_ids": [
      "ga_clinical_review_3month"
    ],
    "location_strategy": "remote",
    "meal_slot": null,
    "phase_scope": [
      "phase_marcus_001",
      "phase_marcus_003",
      "phase_marcus_007"
    ],
    "primary_activity_type": "consultation",
    "primary_counts_toward_weekly_target": false,
    "primary_frequency": {
      "cadence": "monthly",
      "count": 0,
      "days": [],
      "window": "monthly"
    },
    "primary_intent": "care_team_review",
    "primary_role": "support",
    "primary_weekly_frequency_estimate": 0,
    "semantic_notes": [
      "Biometric review and summary by care team.",
      "Support-only; does not count as a review."
    ],
    "substitution_count": 0,
    "substitution_reason_codes": [],
    "travel_context": false
  },
  {
    "activity_family_id": "b05_clinical_trainer_physio_handoff",
    "batch_id": "005_clinical_review_measurement",
    "care_domain": "consultation",
    "family_target": {
      "goal_action_id": "ga_care_team_followthrough_3month",
      "period": "3_month",
      "substitutions_count": 0,
      "support_counts": false,
      "target_units": 0,
      "unit_label": "reviews"
    },
    "goal_action_ids": [
      "ga_clinical_review_3month"
    ],
    "location_strategy": "remote",
    "meal_slot": null,
    "phase_scope": [
      "phase_marcus_005"
    ],
    "primary_activity_type": "consultation",
    "primary_counts_toward_weekly_target": false,
    "primary_frequency": {
      "cadence": "phase-specific",
      "count": 0,
      "days": [],
      "window": "pain_escalation"
    },
    "primary_intent": "care_team_review",
    "primary_role": "support",
    "primary_weekly_frequency_estimate": 0,
    "semantic_notes": [
      "Trainer-physio handoff after pain escalation or travel.",
      "Support-only; does not count as a review."
    ],
    "substitution_count": 0,
    "substitution_reason_codes": [],
    "travel_context": false
  },
  {
    "activity_family_id": "b05_clinical_adherence_checkin_support",
    "batch_id": "005_clinical_review_measurement",
    "care_domain": "consultation",
    "family_target": {
      "goal_action_id": "ga_adherence_support_weekly",
      "period": "weekly",
      "substitutions_count": 0,
      "support_counts": true,
      "target_units": 0,
      "unit_label": "protocol checks"
    },
    "goal_action_ids": [
      "ga_adherence_support_weekly"
    ],
    "location_strategy": "remote",
    "meal_slot": null,
    "phase_scope": [
      "phase_marcus_001",
      "phase_marcus_003",
      "phase_marcus_007"
    ],
    "primary_activity_type": "consultation",
    "primary_counts_toward_weekly_target": false,
    "primary_frequency": {
      "cadence": "weekly",
      "count": 0,
      "days": [],
      "window": "normal-week"
    },
    "primary_intent": "adherence_check",
    "primary_role": "support",
    "primary_weekly_frequency_estimate": 0,
    "semantic_notes": [
      "Weekly adherence check-in by remote coach.",
      "Support-only; does not count as a review."
    ],
    "substitution_count": 0,
    "substitution_reason_codes": [],
    "travel_context": false
  },
  {
    "activity_family_id": "b05_clinical_dietitian_lab_followup",
    "batch_id": "005_clinical_review_measurement",
    "care_domain": "clinical_review_measurement",
    "family_target": {
      "goal_action_id": "ga_care_team_followthrough_3month",
      "period": "3_month",
      "substitutions_count": true,
      "support_counts": false,
      "target_units": 4,
      "unit_label": "reviews"
    },
    "goal_action_ids": [
      "ga_clinical_review_3month"
    ],
    "location_strategy": "remote",
    "meal_slot": null,
    "phase_scope": [
      "phase_marcus_003",
      "phase_marcus_005"
    ],
    "primary_activity_type": "consultation",
    "primary_counts_toward_weekly_target": false,
    "primary_frequency": {
      "cadence": "post_lab_due_week",
      "count": 1,
      "type": "monthly"
    },
    "primary_intent": "dietitian_lab_followup",
    "primary_role": "measurement",
    "primary_weekly_frequency_estimate": 0,
    "semantic_notes": [
      "Adds a nutrition-focused clinical follow-up after lab or CGM review.",
      "Counts only toward the 3-month clinical review package, not a weekly denominator."
    ],
    "substitution_count": 1,
    "substitution_reason_codes": [
      "provider_unavailable",
      "remote_delivery_needed",
      "time_conflict"
    ],
    "travel_context": false
  },
  {
    "activity_family_id": "b05_clinical_remote_care_team_handoff",
    "batch_id": "005_clinical_review_measurement",
    "care_domain": "clinical_review_measurement",
    "family_target": {
      "goal_action_id": "ga_care_team_followthrough_3month",
      "period": "3_month",
      "substitutions_count": true,
      "support_counts": false,
      "target_units": 4,
      "unit_label": "reviews"
    },
    "goal_action_ids": [
      "ga_clinical_review_3month",
      "ga_care_team_followthrough_3month"
    ],
    "location_strategy": "remote",
    "meal_slot": null,
    "phase_scope": [
      "phase_marcus_004",
      "phase_marcus_006",
      "phase_marcus_007"
    ],
    "primary_activity_type": "consultation",
    "primary_counts_toward_weekly_target": false,
    "primary_frequency": {
      "cadence": "phase_scoped",
      "count": 1,
      "type": "monthly"
    },
    "primary_intent": "remote_care_team_handoff",
    "primary_role": "measurement",
    "primary_weekly_frequency_estimate": 0,
    "semantic_notes": [
      "Adds explicit care-team handoff logic when travel or remote delivery changes the plan.",
      "Supports travel continuity while preserving the clinical review target as the counting action."
    ],
    "substitution_count": 1,
    "substitution_reason_codes": [
      "travel_window",
      "provider_unavailable",
      "remote_delivery_needed"
    ],
    "travel_context": true
  }
]
```

Target counts remaining: final merged board needs at least 100 scheduler-facing activities from activity families across all accepted care-domain batches. This batch must provide at least 20 scheduler-facing activities while preserving exactly 10 families. Use the requested prefix exactly and avoid duplicate activity/family IDs.

Every family must include `care_domain` and `family_target`. The family target must use a weekly or 3-month period, map back to a member goal action, and state whether substitutions count toward the same target.

---

## Stage Instructions

# Stage 05: Generate Activity Family Batch

You are generating one batch of `ActivityFamily` objects for `data/activity_families.json`.

Activities are not scheduled events yet. They are prescriptions that the scheduler will later expand into task instances.

## Inputs

You will receive:

- `member_profile.json`
- `resource_universe.json`
- `known_frictions.json`
- goal actions from `member_profile.goal_actions`
- `goal_action_budget.json`
- care-domain batch scope and theme
- approved activity family blueprints for this batch
- existing activity summaries from previous batches
- target counts remaining

## Output

Return one JSON object with:

- `activity_families`

Each family must include:

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

`family_validation_notes` must be a JSON array of strings, not a single string.

`substitution_rules` must be a JSON array of objects, not strings. Use object
fields such as `when`, `prefer_activity_id`, and `reason`.

Every activity must include all fields from the activity schema fragment.

## Batch size

Generate exactly the activity families listed in the approved blueprint for this batch.

Do not invent extra families.

Do not omit blueprint families.

If the batch scope says no approved blueprint file is present, stop and return:

```json
{
  "activity_families": [],
  "generation_blocked_reason": "Stage 05B requires a validated Stage 05A activity family blueprint."
}
```

Each generated family must preserve the blueprint's:

- `activity_family_id`
- `care_domain`
- `family_target`
- `goal_action_ids`
- `primary_role`
- `primary_activity_type`
- `primary_intent`
- `primary_counts_toward_weekly_target`
- `primary_frequency`
- `meal_slot`
- `phase_scope`
- `substitution_count`
- `substitution_reason_codes`
- `travel_context`

You may add implementation detail, dependencies, resources, metrics, and concise titles, but you must not change the semantic role or weekly/3-month goal math from the blueprint.

Each family must have exactly one primary activity.

Include 0-3 substitution activities when substitutions are realistic. The final
merged board must contain 100+ scheduler-facing activities from these 50
families. Each batch should contribute enough substitutions, support
variants, and context-specific alternatives to expand beyond one activity per
family without inventing unrelated variety.

The batch scope includes a minimum scheduler-facing activity count for this
batch. Meet or exceed that number using same-family substitutions or realistic
context variants. Do not add extra families to reach the minimum.

## Scheduler decision hierarchy

Design each family as a hierarchical scheduling decision tree:

```text
primary need -> availability/resources -> primary activity -> same-family substitution
```

The scheduler should be able to try the primary activity first, then choose a
same-family substitution when circumstances make the primary unrealistic.
Substitutions count as meeting the family target when they preserve the same
goal action and `family_target.substitutions_count` is true.

## Activity modality

Each activity must map to exactly one of:

- `fitness`
- `food`
- `medication`
- `therapy`
- `consultation`

Use the requested batch theme to decide which modalities should appear. Do not force all five categories into every batch.

## Food activity requirements

Food activities must include actual meals when the batch scope touches nutrition or metabolic health.

Generate meal-specific prescriptions for:

- breakfast
- lunch
- dinner

Do not satisfy food coverage with supplement protocols alone. A supplement that is taken with food should depend on a meal, not replace it.

Meal activities should be realistic for the member's preferences and resources:

- if the member likes to cook, include limited member-prep activities, such as 2x/week
- if the chef/cook is available, prepared meals may depend on chef prep
- if chef prep is unavailable and the member does not want to cook, generate a realistic no-prep meal alternative
- use `member_profile.dietary_access_plan` to decide whether meals are
  chef-prepped, office-delivered, member-assembled, restaurant, hotel buffet, or
  room service
- weekday office lunches should usually be `allowed_locations: ["office"]` with
  food source metadata such as `"prep_source": "chef_prepped"` or
  `"delivery_source": "office_delivery"`; they should not require Marcus to
  travel home during office hours
- home dinners should usually be `allowed_locations: ["home"]` with
  `"prep_source": "chef_prepped"` or a realistic dining-out substitution
- travel meals should use travel-compatible sources such as `hotel_buffet`,
  `restaurant`, or `room_service`
- if a fasted blood panel is scheduled later in the day, meal timing and dependencies should reflect the fasting requirement

When useful for auditability, include extra metadata fields on food activities:

- `meal_slot`: `breakfast`, `lunch`, or `dinner`
- `prep_source`: `chef_prepped`, `member_assembled`, `none`
- `delivery_source`: `office_delivery`, `packed_meal`, `none`
- `dining_source`: `home`, `office`, `restaurant`, `hotel_buffet`, `room_service`
- `food_provider_id`: concrete provider ID when a named chef/dietitian source is relevant

These food-source fields should explain where the meal came from. They do not
mean the provider must be physically present while Marcus eats.

Medication or supplement activities that are described as being taken "with
breakfast", "with lunch", "with dinner", or "with food" must include a
`food_timing` or `prerequisite_activity` dependency that binds them to the
matching meal. They should not float to a disconnected time window after the
meal unless the details explicitly say the supplement can be taken after eating.

Do not require the chef provider to be present during the meal-eating activity
when `can_be_done_by_member` is true. Put chef availability in a `prep_task`
dependency or a separate prep-support activity. The scheduled food activity
itself should require only the member, the meal location, and necessary
equipment unless the provider is actively present for that exact time window.

If a meal is chef-prepped in advance, packed, or delivered to the office, do not
add a member prep dependency that overlaps work hours. Use food-source metadata
instead. The scheduler should be able to place a low-complexity office lunch
during a work block when the member is already at the office.

Do not create standalone member calendar activities titled like `Chef batch meal
prep`. If the chef prepared food, the member-facing activity should be the meal,
such as `Chef-prepared dinner`, with details/dependencies saying the chef
prepared it. Provider-only prep belongs in dependency/context metadata unless
the member must actively participate at that time.

Titles should describe the actual activity, such as `High-protein breakfast`, `Travel-compatible lunch`, or `Chef-prepped recovery dinner`. Do not put implementation labels such as `fallback`, `backup`, `substitution`, `remote or`, `remote-or`, or `hotel-gym` in the title. Do not put delivery-mode parentheticals such as `(remote)`, `(in-person)`, or `(remote or in-person)` in titles. Put that reasoning in `details`, dependencies, allowed locations, remote flags, or substitution rules.

## Resource ID discipline

All `required_provider_ids`, `required_equipment_ids`, and `allowed_locations` must reference IDs from `resource_universe.json`.

Do not invent new provider, equipment, location, or travel IDs.

## Substitution rules

Substitutions must stay inside the same family as the primary activity.

A substitution must:

- preserve the family intent
- share at least one goal tag with the primary activity
- reduce at least one scheduling constraint
- be easier during load adjustment, provider unavailability, facility
  unavailability, equipment unavailability, travel, prep failure, poor sleep,
  pain, fatigue, or time conflict

Every substitution activity must include:

- `substitution_for_activity_id`: the primary activity ID it replaces
- `substitution_reason_codes`: one or more of `travel_window`,
  `provider_unavailable`, `facility_unavailable`, `equipment_unavailable`,
  `lower_load_needed`, `pain_or_fatigue`, `remote_delivery_needed`,
  `time_conflict`, or `prep_unavailable`
- `substitution_notes`: one concise sentence explaining the preserved intent

Substitutions should usually share the primary activity's
`goal_action_id` and `goal_contributions`. If a substitution only
supports the primary but does not replace it, set
`counts_toward_weekly_target: false`.

If a substitution replaces a counting primary, it must carry the same
`goal_action_id` and a counted contribution unless the substitution is explicitly
partial. If it is support-only, use `value: 0`. Do not let support tasks count
unless `family_target.support_counts` is true.

## Dependency rules

Include dependencies when realistic:

- food prep before meals
- food timing for medication/supplements
- fasting before labs
- lab before physician follow-up
- hydration before sauna or cold/heat therapy
- lower-load substitution after travel over 3 hours, poor sleep, or pain escalation
- support check-ins that say they happen before or after a workout must include
  a `prerequisite_activity` dependency or be titled as a standalone planning
  check-in. Do not generate a "before/after session" activity that can float on
  the calendar with no nearby core session.

Do not overuse dependencies.

Do not create passive fasting windows as long scheduled activities. Fasting
before a blood panel should normally be represented as a `fasting` dependency
on the lab task and as meal-timing constraints, not as a 8-10 hour consultation,
therapy, medication, food, or fitness activity. Only create an active task if
the member or provider must actively do something during that exact window.

## Travel-time buffer demonstration

If the batch includes ordinary Singapore gym-based fitness, include at least one
primary gym activity with evening preferred windows that let the scheduler
demonstrate the office-to-gym travel buffer:

- include `18:30-19:30` as an attempted after-office window
- include a later feasible window such as `18:45-20:00`
- keep the activity realistic for the member, provider, and equipment

This allows the scheduler to reject an immediate post-office gym candidate when
`resource_universe.travel_time_rules` requires travel time, then choose a later
candidate.

## Travel-specific activity rules

Travel-specific activities are not ordinary weekly remote tasks.

Travel adaptation is a context for substitution, not a sixth activity category
and not a standalone progress denominator. In most cases, put the
travel-compatible activity in `substitution_activities` under the relevant
meal, cardio, strength, recovery, lab/consultation, or adherence family.

If an activity is only meant for a current travel window, make that clear in the
activity metadata and keep the frequency scoped to travel context:

- use travel-window language in `details`, not vague title prefixes
- include travel goal tags only when the activity is actually travel-specific
- use `allowed_locations` such as `travel_hotel` or `remote` only when that
  remote delivery is valid during active travel
- do not generate a travel-specific primary activity with a normal weekly
  frequency across the entire planning horizon
- do not let a `remote` allowed location make a travel-only activity schedulable
  on non-travel days
- do not make travel adaptation its own core goal contribution when the
  activity is really substituting for cardio, strength, recovery, meals, or
  consultations; map it to the underlying goal action it preserves
- do not generate a primary activity that counts toward a `travel` goal
  action unless that action is explicitly `support_only`

For titles, prefer concise names such as `Restaurant lunch`, `Hotel mobility
session`, or `Travel care-team check-in`. Put the travel-window constraint in
`details`, `journey_phase_applicability`, dependencies, and substitution rules.

## Priority rules

Activities should be priority-ordered across the board.

Within a batch:

- core goal activities outrank support activities
- prerequisite activities outrank dependent follow-ups
- high-impact recurring activities outrank optional nice-to-haves
- fasting labs and other prerequisite measurements outrank meals or consults
  that depend on their results, so the scheduler can place them before normal
  morning routines

Use the provided priority range if one is supplied.

## Goal coverage rules

Activities should make weekly and 3-month goal coverage interpretable.

When an activity directly advances a goal, include `goal_contributions` metadata that identifies:

- the goal ID
- the goal action ID it satisfies
- whether the activity is `core`, `support`, `prerequisite`, `recovery`, or `measurement`
- whether it counts toward the target
- the contribution value

Use this conservatively. Daily supplements, hydration, generic reminders, and low-complexity support tasks should usually be `support` and should not inflate goal coverage.

Substitutions can count toward the same goal only when they preserve the primary intent. If they are lower-load or partial substitutes, mark the contribution accordingly in the notes.

Each activity family should include `goal_action_ids`, using only IDs from `member_profile.goal_actions`.

Do not invent goal action IDs. If the batch scope needs a goal action that does not exist, call that out in `family_validation_notes` rather than creating a new ID.

## Core vs support contribution rules

Do not use `goal_contributions` as loose tagging.

Only mark `counts_toward_weekly_target: true` when the activity is the thing the member must actually complete for that goal action.

Examples:

- `High-protein breakfast`, `Structured metabolic lunch`, and `Chef-prepped recovery dinner` may count toward a structured-meal goal action.
- `Chef batch prep`, `Weekend meal planning review`, `Fiber target check`, `Protein target confirmation`, and `Restaurant ordering precommitment` support nutrition but do not count as meals.
- `Zone 2 stationary bike`, `Swim aerobic session`, and `Incline walking cardio` may count toward aerobic conditioning.
- `Wearable data review`, `Daily step target review`, and `Travel continuity check-in` support cardio adherence but do not count as aerobic conditioning.
- `Trainer-led lower-body strength session` may count toward strength work.
- `Trainer onboarding`, `Physio note handoff`, and `Movement assessment` support strength but do not count as strength execution.

For each weekly goal action, generate enough primary activity frequency to plausibly meet the target in a normal week, but avoid generating core activity frequency far above the target. For each 3-month goal action, generate enough due-week, monthly, phase-scoped, or measurement work to plausibly meet the full-horizon target. If the board needs related support work, mark it as support with `value: 0`.

Substitution activities should usually share the same `goal_action_id` as the primary. Count them only when they replace the primary execution, not when they are merely an alternate option, prep, or reminder.

The scheduler will cap core weekly goal actions at their weekly target. Do not
generate many redundant core activities expecting all of them to appear on the
calendar. Extra candidates should represent meaningful alternatives that may be
skipped once the weekly target is met.

Support activities should not appear as standalone substitutions unless they are
linked to a concrete scheduled activity through a dependency or clear timing
rule. A warmup, movement prep, activation, or care handoff is context for a
main session; it should not float independently on the calendar.

Use modality names consistently. Member-led mobility, activation, stretching,
or exercise preparation should usually be `fitness` unless it is a provider-led
clinical intervention. Reserve `therapy` for sessions that are genuinely
therapeutic or clinician-directed.

## Avoid duplicates

Use the existing activity summaries to avoid repeating the same activity.

If a similar activity is necessary, make the distinction clear in title, intent, phase, frequency, provider, or constraint.

## Output format

Return valid JSON only.
