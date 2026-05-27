# Assembled Prompt: Stage 01 Member Profile

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

## Stage Instructions

# Stage 01: Generate Member Profile

You are generating `data/member_profile.json` for the first synthetic Resource Allocator demo.

Use the system role, client profile rules, and original persona seed.

The planning window is fixed:

- planning start date: `2026-06-01`
- planning months: `3`
- planning end date: `2026-08-31`

All journey phases and travel windows must fit inside this June 1, 2026 through August 31, 2026 window.

## Inputs

You will receive:

- system role rules
- client profile rules
- `prompts/inputs/original_persona.md`
- `prompts/examples/member_profile.one_shot_example.json`

Treat the original persona seed as the human-authored source of truth for the member's identity, preferences, constraints, goals, food habits, travel pattern, and care-team needs.

You may enrich missing details only when they are consistent with the persona. Do not replace the persona with a different archetype.

Use the one-shot member profile example only as a structural and style reference for:

- field shapes
- stable ID style
- planning-window dates
- journey phase timeline style
- travel-window shape
- weekly goal action shape

Do not copy the example member identity, goals verbatim, IDs verbatim, locations verbatim, or travel windows verbatim. The generated member must be based on the original persona seed.

## Output

Return one JSON object representing a canonical member profile.

The object must include:

- `member_id`
- `name`
- `timezone`
- `age_range`
- `occupation`
- `typical_work_hours`
- `goals`
- `goal_actions`
- `preferences`
- `dietary_access_plan`
- `constraints`
- `baseline_metrics`
- `scheduling_rules`
- `journey_phases`
- `location_rhythm`
- `travel_windows`

## Required member story

Create one realistic member who is appropriate for an Elyx-style HealthSpan concierge service:

- high-performing professional or executive
- frequent work travel
- motivated by data and expert coordination
- prefers morning exercise
- accepts remote consultations
- has at least one mild physical limitation affecting exercise
- has metabolic-health, sleep/recovery, fitness, adherence, and preventive-care goals
- needs coordination across trainer, physiotherapist, dietitian, physician, lab/phlebotomist, and chef/cook resources

## Dietary access plan

The profile must include a top-level `dietary_access_plan` object. This is the
source of truth for realistic food activity generation and scheduling.

The dietary access plan must specify:

- `home_chef_access`: whether a cook/private chef can prepare meals at home
- `office_meal_access`: whether structured lunches can be packed, delivered,
  or eaten at the office during work blocks
- `chef_capacity_per_week`: realistic count of chef-prepped meal batches or
  meal-support sessions
- `member_assembly_limit_per_week`: how often the member is willing to assemble
  food personally
- `dining_out_allowance_per_week`: how many structured restaurant meals are
  acceptable during non-travel weeks
- `travel_meal_strategy`: how breakfast, lunch, and dinner should be handled in
  planned high-resource travel and last-minute low-resource travel
- `explicit_meal_scheduling`: which meals should appear as calendar activities
  instead of being assumed background behavior
- `food_source_labels`: allowed labels such as `chef_prepped`,
  `office_delivery`, `member_assembled`, `restaurant`, `hotel_buffet`, and
  `room_service`

For Marcus, assume a realistic high-service executive setup:

- home chef/cook support exists in Singapore
- structured office lunch can be chef-prepped, packed, or delivered to the office
- chef support should appear as food source/provider context, not as the member
  attending a separate prep activity
- Marcus may assemble simple food at most 2 times per week
- non-travel dining out is allowed but limited and should still be structured
- travel meals are mostly restaurant, hotel buffet, or room-service choices

## Weekly goal targets and actions

Each goal should include a weekly target definition that later generation stages can use for coverage reporting.

Weekly targets should answer:

- what progress means for this goal in one week
- which kinds of activities count toward it
- which activities are only support, prerequisites, or context
- whether substitutions count as coverage when they preserve the same intent

Example:

```json
{
  "goal_id": "metabolic_health",
  "label": "Improve metabolic health",
  "weekly_target": {
    "unit": "core_activity",
    "minimum": 5,
    "preferred": 7,
    "counts_activity_types": ["food", "fitness", "consultation"],
    "support_activity_types": ["medication"],
    "notes": "Meals and Zone 2 work count directly; supplements support the goal but should not dominate coverage."
  }
}
```

Do not create targets so broad that every daily habit counts as full progress.

Also include a top-level `goal_actions` array. These are the concrete weekly or 3-month action requirements that activity families will later satisfy.

A goal action is not a scheduled event. It defines the denominator for coverage review.

Travel adaptation is not a separate core denominator. Do not create a
core goal action such as "complete travel-compatible physical activity"
unless the member genuinely has an independent travel-specific training goal.
For this assignment, travel-adapted activities should usually count as
substitutions or alternate delivery modes for the existing cardio, strength,
meal, recovery, or consultation actions. If travel continuity is useful
to track, make it `support_only: true` and explain that it does not inflate the
core target denominator.

Each goal action must include:

- `goal_action_id`
- `goal_id`
- `label`
- `role`
- `target`
- `activity_types`
- `substitutions_allowed`
- `counts_substitutions`
- `support_only`
- `notes`

Allowed roles:

- `core`
- `support`
- `prerequisite`
- `recovery`
- `measurement`

Examples:

```json
{
  "goal_action_id": "ga_structured_meals_weekly",
  "goal_id": "metabolic_health",
  "label": "Complete structured metabolic meals",
  "role": "core",
  "target": {"period": "weekly", "units": 14, "unit_label": "meals"},
  "activity_types": ["food"],
  "substitutions_allowed": true,
  "counts_substitutions": true,
  "support_only": false,
  "notes": "Prepared, member-prepped, or no-prep meals may count; supplements do not count."
}
```

```json
{
  "goal_action_id": "ga_adherence_support_weekly",
  "goal_id": "adherence",
  "label": "Complete supplement protocol",
  "role": "support",
  "target": {"period": "weekly", "units": 7, "unit_label": "protocol checks"},
  "activity_types": ["medication"],
  "substitutions_allowed": false,
  "counts_substitutions": false,
  "support_only": true,
  "notes": "Supports adherence but should not inflate core metabolic-health progress."
}
```

Goal actions should be small enough to audit and broad enough to avoid one action per tiny habit.

Goal actions should also define what should *not* count. For each action, make the denominator explicit enough that later stages can distinguish:

- target-counting execution work
- support work
- prerequisite work
- measurement or review work
- extra work beyond the weekly target

Example: `Complete structured metabolic meals` counts actual breakfast, lunch, or dinner consumption. Chef prep, meal planning, fiber checks, protein confirmations, restaurant precommitments, supplement protocols, and reminders support the goal but do not count as completed meals.

Example: `Complete aerobic conditioning` counts actual Zone 2, swimming, cycling, walking-cardio, or equivalent aerobic sessions. Wearable review, step-target review, travel continuity planning, or provider handoff does not count as aerobic conditioning.

The weekly target should be plausible for a normal week. Avoid targets that require the scheduler to place an unrealistic number of core activities.

## Journey phases

`journey_phases` must be a timeline, not a single label.

Each phase must include:

- `phase_id`
- `phase_type`
- `start_date`
- `end_date`
- `trigger`
- `primary_goals`
- `scheduling_biases`

Supported phase types:

- `baseline`
- `travel`
- `pain_escalation`
- `consolidation`

The timeline should cover the full 3-month planning window.

## Travel windows

Include:

- at least one planned monthly travel window
- at least one last-minute travel window
- at least one planned travel case with better facilities, such as hotel gym access
- at least one low-resource travel case

Travel windows should include enough detail to support later scheduling constraints. For now, do not require exact airport transfer or transport-time modeling. Instead, include enough timing detail to identify whether the member has changed location and whether the travel duration was over 3 hours. Travel over 3 hours should create a realistic next-day or same-day fatigue consideration.

## Scheduling rules

Include rules such as:

- planning start date
- planning months
- weekday and weekend session limits
- high-load activity limits
- avoid high-intensity activity after poor sleep
- avoid heavy lower-body work after flights or travel legs over 3 hours
- prefer morning exercise
- compact recurring low-complexity tasks in the calendar

## Output format

Return valid JSON only.

---

## Original Persona

# Original Persona Seed

Use this as the source persona for Stage 01 member-profile generation. Expand it into valid `member_profile.json` without copying prose verbatim.

## Persona

Name: Marcus Tan

Location and timezone: Singapore, Asia/Singapore

Age range: 46-50

Occupation: Founder-operator and regional CEO of a logistics technology company with teams in Singapore, Hong Kong, Tokyo, Jakarta, and Sydney.

## Personality And Operating Style

Marcus is analytical, direct, and time-protective. He likes concise recommendations, visible rationale, and quantified progress. He dislikes vague wellness advice and plans that require too many daily decisions. He will follow a plan when it is clearly connected to business travel, energy, strength, and longevity goals.

He is not looking for an extreme transformation. He wants a high-reliability care plan that works during normal office weeks, board-meeting weeks, and messy travel weeks.

## Healthspan Context

This is synthetic demo data only. Do not diagnose Marcus.

Plausible synthetic context:

- Mildly elevated metabolic-risk markers from prior screening.
- Inconsistent aerobic base due to travel and long workdays.
- Mild right-knee irritation after running or deep loaded flexion.
- Lower-back tightness after flights longer than 3 hours.
- Sleep consistency drops during travel weeks and late investor-call weeks.
- Good baseline motivation, but adherence drops when the plan requires cooking, logging, or travel improvisation.

## Goals

Primary goals:

- Improve metabolic health through structured meals, Zone 2 work, strength training, and periodic physician review.
- Build and maintain lean strength without aggravating the knee.
- Preserve energy and sleep quality during frequent travel.
- Make preventive care and care-team coordination reliable without creating more decision fatigue.

The generated profile should translate these goals into weekly goal actions with clear denominators.

Examples:

- structured meal completion
- aerobic conditioning sessions
- knee-safe strength sessions
- recovery or sleep-protection actions
- preventive measurement or clinician-review actions when due
- support-only adherence actions that should not inflate core progress

## Work And Availability Pattern

Normal weekday:

- Usually in office from 08:30 to 18:00 or 18:30.
- Prefers training before work, especially 06:30-08:00.
- Can sometimes accept an evening session from 18:45-20:00.
- Avoids workouts after 20:30.
- Has short windows for low-complexity tasks during office days, but not full sessions.

Weekend:

- Saturday morning can support longer training, physio, or recovery.
- Sunday is best for planning, chef prep, family time, and light movement.

## Food Preferences And Constraints

Marcus likes high-protein breakfasts and practical meals. He enjoys Singaporean, Japanese, Mediterranean, Indian, and Vietnamese food. He dislikes strict calorie tracking.

Food generation should include real meal activities:

- breakfast
- lunch
- dinner

Supplements, protein confirmations, fiber checks, meal planning, chef prep, restaurant ordering precommitments, and reminders support food goals but do not count as completed meals.

Cooking preference:

- Marcus is willing to cook or assemble simple meals at most 2 times per week.
- He prefers chef-prepped or no-prep options during workweeks.
- If chef prep is unavailable, the plan should use realistic no-prep meals rather than pretending food prep happened.

Dietary access:

- At home in Singapore, Marcus has access to cook/private-chef support for structured meals.
- During office days, lunch can be chef-prepped, packed, or delivered to the office; it should not require him to travel home or personally prep food during work.
- Dinner is usually at home with chef-prepped food, or a limited structured restaurant meal when work/social context makes that realistic.
- Non-travel dining out is allowed a few times per week when it can still meet the structured meal intent.
- During planned high-resource travel, breakfast is usually hotel buffet/room service and lunch/dinner are restaurant or hotel meals.
- During last-minute low-resource travel, meals are mostly restaurant or room-service choices with remote dietitian guidance when needed.

Lab/meal interaction:

- Fasting blood panels should affect meal timing and supplement-with-food dependencies.
- A food activity after a fasting panel should be realistic and not scheduled before the fasting requirement is satisfied.

## Travel Pattern

Planned monthly travel:

- Hong Kong or Tokyo for board meetings or investor meetings.
- Planned trips usually have a good hotel gym, hotel pool, and reliable remote consultations.
- Local trusted physiotherapy and labs are usually not available during travel.

Last-minute travel:

- Jakarta or Bangkok client escalation.
- Lower resource quality, more restaurant meals, higher work stress, and less reliable sleep.
- Remote care is usually the only reliable provider option.

Travel rule:

- Do not model detailed airport transfers or commute buffers for this version.
- Travel over 3 hours should create same-day or next-day fatigue/readiness effects.
- High-load lower-body training should normally be avoided after travel over 3 hours unless explicitly justified.

## Care Team Needs

The generated profile should justify coordination across:

- trainer
- physiotherapist
- dietitian
- physician
- lab or phlebotomist
- chef or cook

Care handoff should matter. For example:

- trainer needs knee limitation and physio guidance
- dietitian needs travel meal constraints and metabolic goals
- physician needs lab context
- chef needs meal goals, prep windows, and food preferences

## Generation Priorities

The generated profile should create a realistic scheduling problem, not a perfect plan.

Include:

- independent provider availability later in the pipeline
- meal prep friction
- travel-compatible substitutions
- post-travel fatigue adjustments
- provider handoff context
- weekly goal actions that separate core progress from support work

Avoid:

- severe medical diagnoses
- unrealistic daily high-load training
- counting support habits as completed goal actions
- making every provider perfectly available
- variety for its own sake

---

## One-Shot Structural Example

{
  "member_id": "member_elyx_001",
  "name": "Arjun Mehta",
  "timezone": "Asia/Singapore",
  "age_range": "45-49",
  "occupation": "Regional technology executive",
  "profile_summary": "Arjun is a Singapore-based technology executive who travels frequently across Asia. He wants a data-driven healthspan plan that improves strength, metabolic health, sleep, and travel resilience without creating more decision fatigue.",
  "typical_work_hours": {
    "monday_to_friday": {
      "start": "08:30",
      "end": "18:30",
      "notes": "Often has early Europe calls and occasional US evening calls."
    },
    "saturday": {
      "start": "10:00",
      "end": "13:00",
      "notes": "Light work or investor calls twice per month."
    },
    "sunday": {
      "start": null,
      "end": null,
      "notes": "Generally reserved for family, recovery, meal planning, and light movement."
    }
  },
  "goals": [
    {
      "goal_id": "goal_strength",
      "name": "Increase lean muscle mass safely",
      "priority": 1,
      "description": "Build strength and preserve long-term mobility without worsening knee discomfort.",
      "success_indicators": [
        "2-3 strength sessions/week",
        "improved lower-body strength scores",
        "no knee flare-ups over 48 hours"
      ],
      "weekly_target": {
        "unit": "core_activity",
        "minimum": 2,
        "preferred": 3,
        "counts_activity_types": [
          "fitness"
        ],
        "support_activity_types": [
          "consultation",
          "therapy"
        ],
        "weekly_goal_action_ids": [
          "wga_strength_sessions_001"
        ],
        "notes": "Strength coverage is based on knee-safe strength work, not every mobility or consult task."
      }
    },
    {
      "goal_id": "goal_metabolic",
      "name": "Improve metabolic health",
      "priority": 2,
      "description": "Reduce early metabolic risk through nutrition, resistance training, cardio, and follow-up labs.",
      "success_indicators": [
        "improved fasting glucose trend",
        "better post-meal energy",
        "stable or reduced waist circumference"
      ],
      "weekly_target": {
        "unit": "core_activity",
        "minimum": 5,
        "preferred": 7,
        "counts_activity_types": [
          "food",
          "fitness",
          "consultation"
        ],
        "support_activity_types": [
          "medication"
        ],
        "weekly_goal_action_ids": [
          "wga_metabolic_meals_001",
          "wga_cardio_sessions_001"
        ],
        "notes": "Meals and aerobic work count directly; supplements are support only."
      }
    },
    {
      "goal_id": "goal_sleep",
      "name": "Improve sleep consistency and recovery",
      "priority": 3,
      "description": "Improve sleep timing, recovery, and next-day energy despite travel and work stress.",
      "success_indicators": [
        "earlier average bedtime",
        "higher morning energy",
        "reduced late caffeine"
      ],
      "weekly_target": {
        "unit": "core_or_recovery_activity",
        "minimum": 3,
        "preferred": 4,
        "counts_activity_types": [
          "therapy",
          "fitness",
          "food"
        ],
        "support_activity_types": [
          "consultation"
        ],
        "weekly_goal_action_ids": [
          "wga_sleep_recovery_001"
        ],
        "notes": "Recovery and sleep protection count when they directly reduce fatigue or improve readiness."
      }
    },
    {
      "goal_id": "goal_cardio_travel",
      "name": "Maintain cardiovascular fitness while traveling",
      "priority": 4,
      "description": "Keep cardio consistent using hotel gyms, walking, swimming, or other low-impact options.",
      "success_indicators": [
        "2 cardio sessions/week",
        "Zone 2 maintained during travel weeks"
      ],
      "weekly_target": {
        "unit": "core_activity",
        "minimum": 2,
        "preferred": 3,
        "counts_activity_types": [
          "fitness"
        ],
        "support_activity_types": [
          "food",
          "therapy",
          "consultation"
        ],
        "weekly_goal_action_ids": [
          "wga_cardio_sessions_001",
          "wga_travel_continuity_001"
        ],
        "notes": "Travel continuity is separated from core cardio completion unless the activity is aerobic."
      }
    },
    {
      "goal_id": "goal_adherence_prevention",
      "name": "Improve adherence and preventive care",
      "priority": 5,
      "description": "Make recurring health actions easier to follow and coordinate with meals, labs, and consults.",
      "success_indicators": [
        "adherence above 85%",
        "preventive labs completed",
        "follow-up consultation completed after labs"
      ],
      "weekly_target": {
        "unit": "measurement_or_support_activity",
        "minimum": 1,
        "preferred": 2,
        "counts_activity_types": [
          "consultation"
        ],
        "support_activity_types": [
          "medication",
          "food"
        ],
        "weekly_goal_action_ids": [
          "wga_preventive_measurement_001",
          "wga_adherence_protocol_001"
        ],
        "notes": "Preventive reviews count when due; daily support protocols are tracked separately."
      }
    }
  ],
  "preferences": {
    "exercise_timing": {
      "preferred": [
        "06:30-08:00"
      ],
      "acceptable": [
        "18:45-20:00"
      ],
      "avoid": [
        "12:00-14:00",
        "after_20:30"
      ]
    },
    "session_length": {
      "weekday_max_minutes": 60,
      "weekend_max_minutes": 90
    },
    "training_preferences": [
      "prefers trainer-led strength when learning new movements",
      "likes data-driven progression",
      "dislikes treadmill-only cardio",
      "accepts remote coaching during travel"
    ],
    "nutrition_preferences": [
      "prefers high-protein breakfasts",
      "likes Indian, Japanese, Mediterranean, and Vietnamese food",
      "dislikes strict calorie counting",
      "accepts meal prep if it reduces weekday decision fatigue"
    ],
    "consultation_preferences": [
      "accepts remote follow-up consults",
      "prefers in-person physio and movement assessments",
      "likes concise summaries and next actions"
    ],
    "communication_preferences": {
      "style": "concise and action-oriented",
      "detail_level": "medium",
      "preferred_channels": [
        "app",
        "weekly summary"
      ]
    }
  },
  "constraints": {
    "physical": [
      {
        "constraint_id": "constraint_knee_mild",
        "name": "Mild right knee discomfort",
        "severity": "mild",
        "description": "Occasional discomfort after running, deep knee flexion, or sudden lower-body volume increases.",
        "implications": [
          "avoid sudden running volume increases",
          "prefer knee-safe strength progressions",
          "use cycling, walking, or swimming during flare-ups"
        ]
      },
      {
        "constraint_id": "constraint_back_tightness",
        "name": "Occasional lower-back tightness",
        "severity": "mild",
        "description": "Tightness after long flights and long seated work blocks.",
        "implications": [
          "add mobility after flights",
          "avoid heavy deadlift progression immediately after travel"
        ]
      }
    ],
    "schedule": [
      "frequent work travel",
      "early-morning calls twice per week",
      "occasional last-minute travel",
      "client dinners two to four times per month"
    ],
    "behavioral": [
      "loses consistency during travel",
      "often defaults to 6 or 7 out of 10 on energy ratings",
      "may skip logging when tired or stressed"
    ],
    "medical_safety": [
      "synthetic demo data only",
      "abnormal labs route to physician review",
      "reduce high-intensity activity after poor sleep or pain escalation"
    ]
  },
  "baseline_metrics": {
    "body_composition": {
      "weight_kg": 78,
      "height_cm": 176,
      "estimated_body_fat_percent": 24,
      "waist_cm": 92
    },
    "fitness": {
      "resting_heart_rate_bpm": 68,
      "estimated_vo2max_category": "average",
      "strength_level": "intermediate",
      "cardio_pattern": "inconsistent"
    },
    "sleep": {
      "average_sleep_duration_hours": 6.3,
      "average_bedtime": "23:45",
      "wake_time": "06:30",
      "main_issue": "late work and travel"
    },
    "metabolic": {
      "risk_level": "mildly elevated",
      "synthetic_markers": [
        {
          "name": "fasting_glucose",
          "value": "slightly elevated"
        },
        {
          "name": "apoB",
          "value": "borderline"
        }
      ]
    },
    "subjective": {
      "morning_energy_average": 6.7,
      "afternoon_energy_average": 7.2,
      "travel_week_energy_average": 5.8
    }
  },
  "scheduling_rules": {
    "planning_start_date": "2026-06-01",
    "planning_months": 3,
    "default_time_granularity_minutes": 15,
    "max_high_load_activities_per_day": 1,
    "max_medium_or_high_load_activities_per_day": 2,
    "min_gap_between_fitness_sessions_hours": 6,
    "avoid_high_intensity_after_poor_sleep": true,
    "poor_sleep_threshold_hours": 5.5,
    "avoid_heavy_lower_body_after_flight_hours": 24,
    "prefer_morning_exercise": true,
    "weekday_session_limit_minutes": 60,
    "weekend_session_limit_minutes": 90,
    "compact_recurring_low_complexity_tasks_in_calendar": true
  },
  "journey_phases": [
    {
      "phase_id": "phase_001",
      "phase_type": "baseline",
      "start_date": "2026-06-01",
      "end_date": "2026-06-21",
      "trigger": "New 3-month plan starts.",
      "primary_goals": [
        "goal_strength",
        "goal_metabolic",
        "goal_adherence_prevention"
      ],
      "scheduling_biases": [
        "complete labs",
        "complete movement assessment",
        "avoid excessive high-load training before physio review"
      ]
    },
    {
      "phase_id": "phase_002",
      "phase_type": "consolidation",
      "start_date": "2026-06-22",
      "end_date": "2026-07-21",
      "trigger": "Baseline assessments are complete.",
      "primary_goals": [
        "goal_strength",
        "goal_metabolic",
        "goal_cardio_travel"
      ],
      "scheduling_biases": [
        "progress strength",
        "increase Zone 2 consistency",
        "use dietitian feedback"
      ]
    },
    {
      "phase_id": "phase_003",
      "phase_type": "travel",
      "start_date": "2026-07-22",
      "end_date": "2026-08-15",
      "trigger": "Planned Tokyo travel followed by low-resource last-minute Jakarta travel.",
      "primary_goals": [
        "goal_cardio_travel",
        "goal_sleep",
        "goal_adherence_prevention"
      ],
      "scheduling_biases": [
        "prefer remote and hotel-compatible care",
        "avoid labs",
        "reduce load after flights"
      ]
    },
    {
      "phase_id": "phase_004",
      "phase_type": "pain_escalation",
      "start_date": "2026-08-16",
      "end_date": "2026-08-22",
      "trigger": "Synthetic knee discomfort after travel fatigue and missed lower-body session.",
      "primary_goals": [
        "goal_strength",
        "goal_sleep"
      ],
      "scheduling_biases": [
        "replace high-load lower-body work with mobility",
        "schedule physio review",
        "resume gradually"
      ]
    },
    {
      "phase_id": "phase_005",
      "phase_type": "consolidation",
      "start_date": "2026-08-23",
      "end_date": "2026-08-31",
      "trigger": "End-of-quarter routine review.",
      "primary_goals": [
        "goal_strength",
        "goal_metabolic",
        "goal_sleep"
      ],
      "scheduling_biases": [
        "review progress",
        "prepare next-quarter plan",
        "avoid last-week overload"
      ]
    }
  ],
  "location_rhythm": {
    "home_location_id": "home",
    "office_location_id": "office",
    "ordinary_weekday_pattern": [
      {
        "time_window": "06:00-08:15",
        "likely_location": "home",
        "notes": "Best for home mobility, remote coaching, or nearby gym."
      },
      {
        "time_window": "08:30-18:30",
        "likely_location": "office",
        "notes": "Work block; only short tasks feasible."
      },
      {
        "time_window": "18:45-20:15",
        "likely_location": "gym",
        "notes": "Backup training window if not blocked."
      },
      {
        "time_window": "20:30-22:30",
        "likely_location": "home",
        "notes": "Recovery and evening routine only."
      }
    ],
    "weekend_pattern": [
      {
        "time_window": "08:00-11:00",
        "likely_location": "gym",
        "notes": "Longer training, physio, or assessments."
      },
      {
        "time_window": "12:00-18:00",
        "likely_location": "home",
        "notes": "Family, meal prep, recovery, walking."
      }
    ]
  },
  "travel_windows": [
    {
      "travel_window_id": "travel_hk_2026_06",
      "travel_id": "travel_hk_2026_06",
      "travel_type": "planned",
      "type": "planned",
      "destination": "Hong Kong",
      "start": "2026-06-17T08:00:00+08:00",
      "end": "2026-06-21T21:00:00+08:00",
      "purpose": "Investor meetings",
      "available_location_ids": [
        "travel_hotel",
        "remote"
      ],
      "member_location_override": "travel_hotel",
      "expected_facilities": [
        "hotel_gym",
        "hotel_pool",
        "remote_consultation_supported"
      ],
      "limitations": [
        "no trusted in-person physiotherapist",
        "no lab access planned",
        "two likely client dinners"
      ],
      "notes": "Higher-resource planned travel case with useful hotel facilities but limited provider continuity."
    },
    {
      "travel_window_id": "travel_tokyo_2026_07",
      "travel_id": "travel_tokyo_2026_07",
      "travel_type": "planned",
      "type": "planned",
      "destination": "Tokyo",
      "start": "2026-07-22T07:30:00+08:00",
      "end": "2026-07-29T22:30:00+08:00",
      "purpose": "Board meetings and client visits",
      "available_location_ids": [
        "travel_hotel",
        "remote"
      ],
      "member_location_override": "travel_hotel",
      "expected_facilities": [
        "basic_hotel_gym",
        "walking_routes",
        "remote_consultation_supported"
      ],
      "limitations": [
        "limited equipment",
        "unpredictable dinners",
        "likely reduced sleep"
      ],
      "notes": "Moderate-resource planned travel case."
    },
    {
      "travel_window_id": "travel_jakarta_2026_08",
      "travel_id": "travel_jakarta_2026_08",
      "travel_type": "last_minute",
      "type": "last_minute",
      "destination": "Jakarta",
      "start": "2026-08-12T06:30:00+08:00",
      "end": "2026-08-15T23:00:00+08:00",
      "purpose": "Urgent client escalation",
      "available_location_ids": [
        "travel_hotel",
        "remote"
      ],
      "member_location_override": "travel_hotel",
      "expected_facilities": [
        "hotel_room",
        "remote_consultation_supported"
      ],
      "limitations": [
        "no reliable gym",
        "no known allied health provider",
        "high work stress",
        "restaurant-based meals"
      ],
      "notes": "Low-resource last-minute travel case designed to force substitutions or unscheduled tasks."
    }
  ],
  "weekly_goal_actions": [
    {
      "weekly_goal_action_id": "wga_strength_sessions_001",
      "goal_id": "goal_strength",
      "label": "Complete knee-safe strength work",
      "role": "core",
      "target_per_week": 2,
      "activity_types": [
        "fitness"
      ],
      "required_meal_slots": [],
      "substitutions_allowed": true,
      "counts_substitutions": true,
      "support_only": false,
      "notes": "Trainer-led, gym, hotel-gym, or knee-safe substitutions count when they preserve strength intent."
    },
    {
      "weekly_goal_action_id": "wga_metabolic_meals_001",
      "goal_id": "goal_metabolic",
      "label": "Complete structured metabolic meals",
      "role": "core",
      "target_per_week": 14,
      "activity_types": [
        "food"
      ],
      "required_meal_slots": [
        "breakfast",
        "lunch",
        "dinner"
      ],
      "substitutions_allowed": true,
      "counts_substitutions": true,
      "support_only": false,
      "notes": "Prepared, member-prepped, travel-compatible, or no-prep meals may count; supplement-only protocols do not count."
    },
    {
      "weekly_goal_action_id": "wga_cardio_sessions_001",
      "goal_id": "goal_cardio_travel",
      "label": "Complete aerobic conditioning",
      "role": "core",
      "target_per_week": 2,
      "activity_types": [
        "fitness"
      ],
      "required_meal_slots": [],
      "substitutions_allowed": true,
      "counts_substitutions": true,
      "support_only": false,
      "notes": "Zone 2, swim, bike, walk, and travel-compatible aerobic substitutions count when load and intent match."
    },
    {
      "weekly_goal_action_id": "wga_sleep_recovery_001",
      "goal_id": "goal_sleep",
      "label": "Complete recovery and sleep protection actions",
      "role": "recovery",
      "target_per_week": 4,
      "activity_types": [
        "therapy",
        "fitness",
        "food"
      ],
      "required_meal_slots": [],
      "substitutions_allowed": true,
      "counts_substitutions": true,
      "support_only": false,
      "notes": "Recovery, mobility, sleep environment, caffeine, alcohol, and post-travel lower-load actions count when they directly protect sleep or readiness."
    },
    {
      "weekly_goal_action_id": "wga_preventive_measurement_001",
      "goal_id": "goal_adherence_prevention",
      "label": "Complete preventive measurement or review when due",
      "role": "measurement",
      "target_per_week": 1,
      "activity_types": [
        "consultation"
      ],
      "required_meal_slots": [],
      "substitutions_allowed": true,
      "counts_substitutions": true,
      "support_only": false,
      "notes": "Labs, physician reviews, dietitian reviews, physio reviews, and care handoff reviews count only in weeks where they are due."
    },
    {
      "weekly_goal_action_id": "wga_adherence_protocol_001",
      "goal_id": "goal_adherence_prevention",
      "label": "Complete support protocol actions",
      "role": "support",
      "target_per_week": 7,
      "activity_types": [
        "medication",
        "food",
        "consultation"
      ],
      "required_meal_slots": [],
      "substitutions_allowed": false,
      "counts_substitutions": false,
      "support_only": true,
      "notes": "Supplements, logging, reminders, and checklists support adherence but should not inflate core metabolic or fitness coverage."
    },
    {
      "weekly_goal_action_id": "wga_travel_continuity_001",
      "goal_id": "goal_cardio_travel",
      "label": "Maintain travel-compatible continuity",
      "role": "support",
      "target_per_week": 3,
      "activity_types": [
        "fitness",
        "food",
        "therapy",
        "consultation"
      ],
      "required_meal_slots": [],
      "substitutions_allowed": true,
      "counts_substitutions": true,
      "support_only": true,
      "notes": "Travel adaptations are shown separately as continuity support unless they also satisfy a core weekly action."
    }
  ]
}
