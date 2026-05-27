# Review Change Log

This file tracks reviewer-facing issues and implementation changes raised during calendar/data review. Keep it updated as new inconsistencies are found.

## Open Changes

### 1. Separate Member Location From Delivery Mode

Current issue: `location_id` is overloaded. It can mean the member's physical location, the activity delivery mode, or the provider context. This caused confusion such as a trainer-led activity scheduled at `home` while the trainer availability was actually `remote`.

Required change:

- Calendar rows should expose `member_location_id` for where Marcus physically is.
- Calendar rows should expose `delivery_mode`, e.g. `in_person`, `remote`, `hybrid`, or `self_directed`.
- Provider assignment should expose `provider_location_id` or `provider_delivery_mode` separately from member location.
- Existing `location_id` can remain temporarily for compatibility, but should be treated as member location only after migration.
- Remote provider sessions should render as `member at home · trainer remote`, not as if the trainer came to the home.

Scheduler implication:

- Travel-time checks must use `member_location_id`, not provider location or delivery mode.
- In-person provider activities require member location and provider availability location to be compatible.
- Remote provider activities can occur while the member remains at home, office, hotel, or another travel-compatible location.

UI implication:

- Activity cards should show member location and provider/delivery context separately.
- Example: `fitness · member home · trainer remote · medium`.

### 2. Track Member Location Across All Occupied Blocks

Current issue: travel labels are inferred only from scheduled activity rows and some `member_blocked` context. The system does not have a complete member-location timeline for every occupied block.

Required change:

- Every member-occupied block should have a member location:
  - scheduled activity rows
  - work blocks
  - sleep blocks if represented
  - meals
  - consultations
  - remote sessions
  - travel legs
  - travel windows
- Build a daily member-location timeline before final scheduling/debug rendering.
- Travel labels should be derived from consecutive member-location blocks.
- If two adjacent blocks have different member locations and a travel-time rule exists, show the travel movement before the next block.
- If no travel-time rule exists for a physical location transition, flag it in the trace or QA report.

### 3. Provider Availability Must Match Activity Delivery

Current issue: a trainer-led home activity can be placed into a trainer's remote availability window.

Required change:

- For in-person activities, provider availability location must match the scheduled member location or a declared compatible service area.
- For remote activities, provider availability must support remote delivery, and member location should remain physical, e.g. `home`.
- If an activity can be either in-person or remote, the scheduler must record the chosen delivery mode.

### 4. Low-Load Strength Should Be Conditional Or Substitution

Current issue: lower-load knee-safe strength appears as a primary activity and can coexist with high-load strength, creating confusing goal coverage and extra sessions.

Required change:

- Lower-load/post-travel/pain-sensitive strength should usually be a substitution or conditional adjustment for the main strength family.
- It should count toward the strength target only when it replaces the main strength session.
- It should not also inflate recovery targets unless explicitly intended.

### 5. Activity Generation QA Flags Need Prompt Feedback

Current issue: the QA report correctly flags duplicate breakfast primaries, frequency contradictions, missing substitution metadata, travel activities counting toward a travel weekly denominator, and travel-context primary activities that should probably be substitutions.

Required change:

- Feed these QA failures back into the generation prompts before regenerating the activity board.
- Travel-adapted activities should generally be substitutions for fitness/food/therapy families, not their own core weekly target denominator.
- Substitutions must carry `substitution_for_activity_id`, `substitution_reason_codes`, and `substitution_notes`.
- Food families should have one clear primary per meal slot strategy, with substitutions under the same family.

### 6. Dietary Plan Access And Meal Coverage Need First-Class Modeling

Current issue: the schedule misses lunch and dinner on most non-travel days. The current generated profile does not define Marcus's food access model, and food activities rely on generic `chef_or_member` dependencies rather than a realistic dietary plan.

Observed in current demo:

- `wga_structured_meals_001` expects 14 structured meals per week across breakfast, lunch, and dinner.
- Most non-travel weekdays only show breakfast.
- Weekday lunch candidates are rejected because lunch is modeled as a home activity during office work hours and the required prep window overlaps blocked work time.
- Food rows do not visibly show a concrete provider because most meal activities have no `required_provider_ids`; chef is only mentioned inside `prep_task` dependency metadata.

Required prompt/data change:

- Add a dietary access plan early in member profile generation:
  - home cook/private chef access and weekly capacity
  - office meal delivery or packed lunch availability
  - allowed restaurant/dining-out frequency
  - travel meal strategy by travel type
  - member willingness to assemble food
  - which meals are expected to be explicitly scheduled versus assumed background habits
- Represent meals as eaten meals, not provider prep work:
  - `lunch at office, chef-prepped/delivered`
  - `dinner at home, chef-prepped`
  - `restaurant dinner, approved dining-out allowance`
- Attach provider/support context to meals:
  - either concrete chef provider where relevant, or `prep_source: chef_prepped`, `delivery_source: office_delivery`, `dining_source: restaurant`.
- Scheduler should treat prepared office lunch as compatible with office work block if eating duration is low-complexity and the member is at office.
- UI should display food source/provider context on meal cards.

## Implemented Changes

- Enforced one meal slot per day in scheduler policy.
- Prevented food, meal-slot, and medication tasks from drifting off target date.
- Added activity-board QA flags to `activity_board_review.md`.
- Compacted low-complexity medication/protocol habits in the calendar UI while preserving raw rows.
- Rebuilt demo run: 441 raw calendar rows, 0 duplicate meal-slot days, 0 food/medication target-date drift cases.
- Fixed travel/location bands so member travel spanning a week boundary appears in every overlapping week.
- Added a Recap tab that summarizes three-month goal/action coverage, substitutions, blocked instances, excess scheduling, and remaining gaps.
- Added Provider Universe and Dietary Access sections to the Profile tab.
- Updated member-profile and activity-generation prompts so future generated data models Marcus's dietary access plan, office lunches, dining-out allowance, travel meals, and food source/provider context explicitly.
- Reframed travel continuity as support-only in the current seed profile so travel adaptations no longer add a separate core weekly denominator.
- Updated activity-generation and board-review prompts so travel adaptations are generated as substitutions or delivery adaptations for underlying meal, cardio, strength, recovery, consultation, measurement, or adherence actions.
- Added substitution reason metadata requirements to prompts and scheduler trace output.
- Added activity-board QA flags for missing substitution reason metadata and suspicious travel-context primary activities.
- Added Stage 05A activity-family blueprint generation, weekly goal action budgets, blueprint validation, and Stage 05B prompt constraints so activity-family batches must follow an approved semantic board plan.

## Stage 05 Redesign Notes

The generation pipeline now has a pre-generation planning layer:

- `data/weekly_goal_action_budget.json` defines goal/action budgets, weekly frequency caps, canonical meal slots, support-only actions, and batch family counts.
- `prompts/stages/05A_activity_family_blueprint.prompt.md` asks the model to plan the activity board before writing full activity JSON.
- `src/generation/activity_blueprint.py` validates the blueprint for batch counts, primary count, goal frequency estimates, meal slots, travel-as-context, and substitution reason codes.
- `scripts/validate_activity_blueprint.py` writes `data/runs/demo-run/01_validation/activity_blueprint_report.json`.
- `scripts/generate_stage05_blueprint.py` can generate and accept a valid blueprint using the OpenAI API.
- `scripts/assemble_prompts.py` now writes `prompts/assembled/05A_activity_family_blueprint.prompt.md` and includes approved per-batch blueprints in Stage 05B prompts.

This does not make semantic validation perfect, but it moves the most important semantic decisions earlier, where they are easier to review and reject before the scheduler sees them.

## Next Recommended Implementation Slice

1. Add `member_location_id` and `delivery_mode` to scheduled task/calendar row generation.
2. Add provider delivery compatibility checks in resource placement.
3. Update travel-time checks and UI travel labels to use member-location timeline.
4. Update card display to show member location and provider delivery separately.
5. Regenerate the demo and verify the 07:30 lower-load strength case no longer appears as “trainer at home” unless provider availability is truly in-person at home.
6. Generate Stage 05A activity-family blueprint, validate it, then regenerate Stage 05B batches from that approved blueprint.
