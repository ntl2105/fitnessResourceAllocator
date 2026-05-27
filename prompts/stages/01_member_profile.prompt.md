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
