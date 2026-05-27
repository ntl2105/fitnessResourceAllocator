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
