# Stage 06: Activity Board Final Review

You are reviewing the complete generated activity board after all activity families have been generated, flattened, and structurally validated.

The goal is to assess whether the activity board is a coherent synthetic health journey, not merely a collection of valid rows.

## Inputs

You will receive:

- `member_profile.json`
- `resource_universe.json`
- `known_frictions.json`
- `activity_families.json`
- flattened `action_plan.json`
- deterministic validation summary

## Output

Return Markdown for:

```text
data/runs/<run_id>/01_validation/activity_board_review.md
```

## Review sections

Include:

1. `Status`
2. `Board-level summary`
3. `Priority review`
4. `Goal coverage review`
5. `Journey phase review`
6. `Dependency review`
7. `Substitution review`
8. `Food and meal review`
9. `Known friction coverage`
10. `Care handoff review`
11. `Warnings`
12. `Repair recommendations`

## Review criteria

Check:

- priorities are internally consistent across goals and modalities
- high-priority activities map to the member's stated primary goals
- support activities do not outrank core goal activities without a clear reason
- member goals include weekly and 3-month target definitions that make calendar coverage explainable
- member profile includes `goal_actions` that define concrete weekly and 3-month denominators
- every high-priority goal action is covered by enough primary or substitution activity families
- every family that claims goal coverage references valid `goal_action_id` values
- activity goal tags and `goal_contributions` are specific enough to explain week-level progress
- low-complexity daily habits, supplements, and reminders do not inflate weekly goal coverage
- prep, planning, reminders, logs, handoffs, protocol checks, and ordering precommitments are not counted as core weekly target completion
- goal actions are neither obviously under-supplied nor over-supplied by generated core activity frequency
- if a goal action is over target, extra work is justified as optional, support, or phase-specific rather than counted as required progress
- substitutions are counted as weekly goal coverage only when they preserve the same goal intent
- substitutions include `substitution_for_activity_id`,
  `substitution_reason_codes`, and `substitution_notes`
- travel-adapted activities are substitutions or alternate delivery modes for
  underlying meal, cardio, strength, recovery, consultation, measurement, or
  adherence actions, not their own core goal denominator
- any goal action with travel in the ID or label is `support_only: true`
  unless the member profile provides a specific independent travel training
  goal
- travel-context substitutions count toward the underlying goal action
  they preserve, not toward a separate travel action
- every week should have an inspectable target denominator: scheduled, unscheduled, substituted, and at-risk counts must map back to generated activities
- goal progression is plausible across the 3-month journey
- baseline, travel, pain escalation, and consolidation phase activities fit their phases
- dependencies form a coherent graph
- food prep, lab prerequisites, medication-with-food, and consultation-after-lab requirements are coherent
- food coverage includes real breakfast, lunch, and dinner activities where nutrition is part of the journey
- supplement protocols do not masquerade as meal coverage
- meal timing responds to fasting labs, chef availability, member-prep preferences, travel state, and no-prep fallback conditions
- food support activities such as prep, planning, fiber checks, protein confirmations, and restaurant precommitments do not masquerade as breakfast, lunch, or dinner completion
- substitutions preserve primary activity intent
- substitutions reduce at least one scheduling constraint
- substitution titles read like member-facing activities, while fallback/substitution rationale lives in metadata
- substitutions do not create harder dependencies than the primary unless justified
- lower-load, post-travel, fatigue-sensitive, or pain-sensitive variants are
  substitutions when they replace a normal training session; they should be
  primary activities only when they are independent recovery work
- load distribution supports recovery and avoids unrealistic clustering
- known frictions are represented in activities or scheduling constraints
- travel over 3 hours creates visible lower-load, recovery, or reduced-capacity logic on the arrival day or next day
- activity locations are compatible with WFH dates, exact travel windows, and
  provider/resource availability assumptions
- local transition buffers are expected between different in-person locations;
  the board should not rely on impossible back-to-back home, office, gym,
  restaurant, clinic, or lab rows
- airport transfers should not appear as member-facing calendar tasks
- care handoff metadata is present when provider coordination is needed
- there are no obvious duplicated, contradictory, or clinically implausible prescriptions

## Output discipline

Be specific and actionable.

If the board is acceptable, say so and list accepted limitations.

If repair is needed, provide targeted repair recommendations rather than rewriting the whole board.
