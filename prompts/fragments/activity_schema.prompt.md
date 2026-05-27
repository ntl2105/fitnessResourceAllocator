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
