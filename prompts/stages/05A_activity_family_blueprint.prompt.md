# Stage 05A: Plan Activity Family Blueprint

You are planning the semantic shape of the activity board before full activity JSON is generated.

Do not generate complete activities yet. Generate a compact blueprint that proves the board can support the member's goals without overproducing repetitive or conflicting prescriptions.

## Inputs

You will receive:

- `member_profile.json`
- `resource_universe.json`
- `known_frictions.json`
- `goal_action_budget.json`
- stage and realism rules

## Output

Return one JSON object only:

```json
{
  "activity_family_blueprints": []
}
```

Each item in `activity_family_blueprints` must include:

- `activity_family_id`: final family ID, using the exact batch prefix
- `batch_id`: one of the configured batch IDs
- `care_domain`: one of the five configured care-domain IDs
- `family_target`: object with `goal_action_id`, `period` (`weekly` or `3_month`), `target_units`, `unit_label`, `substitutions_count`, and `support_counts`
- `goal_action_ids`: goal actions this family supports
- `primary_role`: one of `core`, `support`, `prerequisite`, `recovery`, or `measurement`
- `primary_activity_type`: one of `fitness`, `food`, `medication`, `therapy`, or `consultation`
- `primary_intent`: concise semantic intent, such as `breakfast`, `zone2`, `trainer_strength`, `lab`, `supplement_protocol`, or `post_travel_recovery`
- `primary_counts_toward_weekly_target`: boolean
- `primary_frequency`: compact frequency object describing cadence, count, days/windows, and whether it is normal-week, due-week, monthly, travel-window, or phase-scoped
- `primary_weekly_frequency_estimate`: number used for goal math; use 0 for support-only, monthly, or due-week-only work unless it is expected every normal week
- `meal_slot`: `breakfast`, `lunch`, `dinner`, or null
- `phase_scope`: journey phase IDs where this family applies
- `location_strategy`: concise strategy, such as `home`, `office`, `gym`, `clinic`, `remote`, `travel_hotel`, or `mixed`
- `substitution_count`: 0-3
- `substitution_reason_codes`: reason codes expected for substitutions
- `travel_context`: boolean
- `semantic_notes`: array of short notes explaining why this family exists and what it must not become

## Blueprint Rules

These are hard validation gates. If you miss any one of these, the output will be rejected automatically.

Generate exactly the family counts required by `goal_action_budget.batch_budgets`.
Do not return fewer families. Do not round down. Do not stop at 47, 48, or 49.

For the current budget, that means:

- `001_metabolic_nutrition`: exactly 12 families
- `002_cardiorespiratory_fitness`: exactly 10 families
- `003_strength_mobility_pain`: exactly 10 families
- `004_recovery_sleep_stress`: exactly 8 families
- `005_clinical_review_measurement`: exactly 10 families

The total must be exactly 50 families.

If your draft is short, add a clinically plausible support or substitution
family inside the undercounted care domain rather than creating a standalone
travel/adherence batch. Useful shortfall fillers include:

- cardiorespiratory fitness: remote coach aerobic progression review, hotel
  walking/aerobic substitution, facility-unavailable cardio substitution
- strength/mobility/pain: lower-load strength adjustment, provider-unavailable
  trainer substitution, pain/fatigue mobility substitution
- clinical review/measurement: biometric review, lab reschedule coordination,
  clinician handoff, dietitian or physiotherapy reassessment

Do not create standalone travel or consolidation batches. Travel, pain escalation,
baseline, and consolidation are journey contexts that belong in `phase_scope`,
`travel_context`, dependencies, substitutions, and semantic notes inside the
care-domain batches above.

The total blueprint must contain at least `minimum_primary_family_count` families.

Plan the board so it is semantically balanced:

- weekly and 3-month target math should be plausible for each goal action
- structured meals should cover breakfast, lunch, and dinner without duplicate normal-week meals competing in the same slot
- medication, hydration, CGM, and supplement protocols are support-only unless the profile explicitly says otherwise
- labs and provider reviews are due-week, monthly, or phase-specific, not ordinary weekly clutter
- travel adaptations preserve underlying goals and usually appear as substitutions or travel-scoped support
- recovery and mobility should not silently replace strength unless pain, fatigue, travel, or provider/equipment constraints justify it
- every family should read as a scheduler hierarchy: primary need, required
  availability/resources, preferred primary activity, then same-family
  substitutions for realistic constraint failures

## Target Frequency Estimate Rules

`primary_weekly_frequency_estimate` is not the activity's possible cadence in every phase. It is the amount this family adds to a normal-week target denominator.

Use the caps in `goal_action_budget.goal_action_budgets` exactly. Map by `goal_action_id`.

Support-only actions must have counting estimate 0. Weekly actions may have
normal-week counting estimates. 3-month actions should usually be due-week,
monthly, phase-scoped, or measurement/review families, with
`primary_weekly_frequency_estimate: 0` unless the activity is also explicitly a
weekly behavior.

Use `0` for support-only, due-week-only, monthly, travel-window-only, and prerequisite work.

It is acceptable, and often desirable, for many of the 50 families to have `primary_counts_toward_weekly_target: false`. The assignment needs a rich activity board, but the goal math must stay conservative.

For `ga_structured_meals_weekly`, the total normal-week counting estimate should be exactly 14, not 21. Marcus is not expected to have every breakfast, lunch, and dinner count as an explicit structured meal every week.

Use a plausible split such as:

- breakfast strategies totaling 5 weekly counting units
- lunch strategies totaling 5 weekly counting units
- dinner strategies totaling 4 weekly counting units

Additional food families can exist, but they must be support-only, travel-window-only, fasting-aware, restaurant-review, or substitution context with `primary_counts_toward_weekly_target: false` and `primary_weekly_frequency_estimate: 0`.

Any family with `primary_activity_type: "food"` and
`primary_counts_toward_weekly_target: true` must set `meal_slot` to exactly
`breakfast`, `lunch`, or `dinner`. If the family is a sleep, recovery, stress,
hydration, supplement, or routine behavior rather than an actual meal, do not
use `primary_activity_type: "food"` for a counting family; use `therapy`,
`medication`, or `consultation` as appropriate, or mark it support-only with
`primary_weekly_frequency_estimate: 0`.

## Substitution Planning

Substitutions should be planned inside the same family as the primary activity.

Use only these substitution reason codes:

- `travel_window`
- `provider_unavailable`
- `facility_unavailable`
- `equipment_unavailable`
- `lower_load_needed`
- `pain_or_fatigue`
- `remote_delivery_needed`
- `time_conflict`
- `prep_unavailable`

Do not invent new reason codes. Map specific situations to the allowed codes:

- dining out because chef/food prep is unavailable: `prep_unavailable`
- dining out because the normal meal slot is blocked: `time_conflict`
- fasting or lab timing changes: use dependency notes, or `time_conflict` if a meal must move
- provider cannot cover the desired slot: `provider_unavailable`
- provider is unavailable or remote-only: `provider_unavailable` or `remote_delivery_needed`
- facility is closed, inaccessible, or not available during the needed window: `facility_unavailable`
- equipment is missing at home, office, gym, hotel, or travel location: `equipment_unavailable`
- load needs to be adjusted because of pain, fatigue, recent long travel, or poor sleep: `lower_load_needed` plus `pain_or_fatigue` when clinically relevant

Do not create title-level labels such as `fallback`, `backup`, `remote or`, or `hotel-gym`. The full generation step will put delivery mode and fallback logic in metadata, not titles.

If a planned substitution replaces a counting primary, it should preserve the
same `goal_action_id` and count toward the same `family_target` when
`substitutions_count` is true. If it is support-only, it should not count unless
`support_counts` is true.

## Travel Planning

Travel is context, not a separate core goal denominator.

For any family with `travel_context: true`:

- use `primary_counts_toward_weekly_target: false` unless the matching weekly goal action budget explicitly allows travel primaries
- use `primary_weekly_frequency_estimate: 0` unless the budget explicitly allows travel primaries
- prefer planning travel variants as substitutions through `substitution_count` and `substitution_reason_codes`
- if the family supports `ga_travel_continuity_3month`, it must be support-only and counting estimate must be 0

Travel meal, cardio, and strength adaptations preserve underlying intent, but they should not add an extra normal-week target.

## Food Planning

Plan actual meals:

- breakfast
- lunch
- dinner

Use the member's dietary access plan to decide whether each meal is chef-prepped, office-delivered, member-assembled, restaurant, hotel buffet, or room service.

Chef prep should usually be context metadata for the meal, not a separate member-facing calendar activity.

If a fasting lab affects a day, represent the fasting effect as a dependency or meal timing constraint in the later full activity generation step.

Every counting food family must set `meal_slot` to exactly one of `breakfast`, `lunch`, or `dinner`.

Do not create a counting food family with `meal_slot: null`.

Do not create a generic counting food family such as `member_assembled_meal`. If it counts, it must be a specific breakfast, lunch, or dinner strategy. If it is just a support strategy, set `primary_counts_toward_weekly_target: false` and `primary_weekly_frequency_estimate: 0`.

Use non-counting support families for grocery, chef briefing, dietitian planning, restaurant review, fasting-aware timing support, or travel meal backup logic.

## Required Count Self-Check

Before returning JSON, count the families by `batch_id`.

Do not return the response until the counts are:

```json
{
  "001_metabolic_nutrition": 12,
  "002_cardiorespiratory_fitness": 10,
  "003_strength_mobility_pain": 10,
  "004_recovery_sleep_stress": 8,
  "005_clinical_review_measurement": 10
}
```

Then count the total: it must be 50 families. The full activity generation step
will expand these families into 100+ scheduler-facing activities.

Also include a final top-level `count_self_check` object after
`activity_family_blueprints`:

```json
{
  "count_self_check": {
    "001_metabolic_nutrition": 12,
    "002_cardiorespiratory_fitness": 10,
    "003_strength_mobility_pain": 10,
    "004_recovery_sleep_stress": 8,
    "005_clinical_review_measurement": 10,
    "total": 50
  }
}
```

The self-check must match the actual number of blueprint items exactly.

## Final Self-Check

Before returning JSON, check internally:

- Does every goal action have a coherent path from goal to family to future scheduled instances?
- Are there exactly 50 activity families, with no family invented purely to inflate count?
- Are substitutions linked to realistic constraint failures?
- Are travel activities adaptation logic inside the five care domains, not a separate sixth modality?
- Would a reviewer understand why the board exists before seeing the calendar?
