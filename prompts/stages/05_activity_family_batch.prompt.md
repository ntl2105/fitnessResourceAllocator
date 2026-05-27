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
