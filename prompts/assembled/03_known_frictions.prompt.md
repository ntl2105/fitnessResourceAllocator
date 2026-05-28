# Assembled Prompt: Stage 03 Known Frictions

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

## Known Friction Rules

# Known Frictions Rules

Known frictions are intentional, realistic conflicts that the generated data and scheduler should demonstrate.

They are not scheduler decisions. They are scenario constraints that should later appear in activities, availability, substitutions, decision traces, or unscheduled reasons.

Each friction must have a stable `friction_id` so validation and traces can reference it.

## Required friction coverage

Generate frictions covering:

1. planned travel with better facilities, such as hotel gym access
2. last-minute travel with limited facilities
3. provider availability mismatch with member preferences
4. lab or consultation disruption during travel
5. food prep dependency requiring chef or member prep
6. equipment or facility unavailability
7. post-travel fatigue after a location change over 3 hours
8. skipped or substituted high-load activity requiring recovery adjustment

## Friction shape

Each friction should include:

- `friction_id`
- `name`
- `description`
- `linked_resource_ids` or `affected_travel_window_ids` when applicable
- `date_range` when applicable
- `scheduler_expectation`

## Realism rules

Frictions should arise from plausible care coordination:

- A provider's calendar does not always match the member's preferred time.
- A travel destination may have a hotel gym but no trusted local physio.
- A last-minute trip may have only a hotel room and remote support.
- A lab may only be open weekday mornings.
- A food activity may require prep before consumption.
- A sauna or facility may be unavailable during maintenance.
- A high-load session after travel may need a recovery substitution.
- A travel day over 3 hours may make the member lower-readiness even when a location resource exists.

Avoid arbitrary contradictions that exist only to make the data hard.

---

## Stage Instructions

# Stage 03: Generate Known Frictions

You are generating `data/known_frictions.json`.

Known frictions are realistic conflicts the scheduler should later demonstrate.

## Inputs

You will receive:

- `member_profile.json`
- `resource_universe.json`

## Output

Return one JSON object with a top-level key:

- `frictions`

Each friction must include:

- `friction_id`
- `name`
- `description`
- `linked_resource_ids` or `affected_travel_window_ids` where applicable
- `date_range` when applicable
- `scheduler_expectation`

## Required coverage

Generate frictions covering all of the following:

1. planned travel with better facilities, such as hotel gym access
2. last-minute travel with limited facilities
3. provider availability mismatch with member preferences
4. lab or consultation disruption during travel
5. food prep dependency requiring chef or member prep
6. equipment or facility unavailability
7. post-travel fatigue after a location change over 3 hours
8. skipped or substituted high-load activity requiring recovery adjustment

## ID discipline

Use only provider IDs, equipment IDs, location IDs, and travel window IDs from `resource_universe.json`.

Do not invent new resources.

## Realism

Frictions should be plausible and later traceable. Each friction should explain what scheduler behavior it is meant to exercise.

## Output format

Return valid JSON only.

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
      "from_location_id": "home",
      "minutes": 25,
      "to_location_id": "restaurant"
    },
    {
      "from_location_id": "restaurant",
      "minutes": 25,
      "to_location_id": "home"
    },
    {
      "from_location_id": "home",
      "minutes": 25,
      "to_location_id": "gym"
    },
    {
      "from_location_id": "gym",
      "minutes": 25,
      "to_location_id": "home"
    },
    {
      "from_location_id": "office",
      "minutes": 40,
      "to_location_id": "home"
    },
    {
      "from_location_id": "home",
      "minutes": 40,
      "to_location_id": "office"
    },
    {
      "from_location_id": "office",
      "minutes": 15,
      "to_location_id": "gym"
    },
    {
      "from_location_id": "gym",
      "minutes": 15,
      "to_location_id": "office"
    },
    {
      "from_location_id": "clinic",
      "minutes": 30,
      "to_location_id": "home"
    },
    {
      "from_location_id": "home",
      "minutes": 30,
      "to_location_id": "clinic"
    },
    {
      "from_location_id": "lab",
      "minutes": 30,
      "to_location_id": "home"
    },
    {
      "from_location_id": "home",
      "minutes": 30,
      "to_location_id": "lab"
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
