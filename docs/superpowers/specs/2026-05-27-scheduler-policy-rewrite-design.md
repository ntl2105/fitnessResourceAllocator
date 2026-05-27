# Scheduler Policy Rewrite Design

## Problem

The current scheduler is a single greedy pass over task instances. It mixes
member availability, travel context, provider windows, substitutions, goal caps,
meal coverage, and UI-facing trace explanations in one placement loop. Recent
fixes made individual symptoms better, but also exposed deeper policy conflicts:

- food coverage must be daily, but meal variety and fallback behavior are being
  handled inside task expansion rather than a daily meal policy
- medications still exist, but supplement timing is tied to one specific
  breakfast family instead of the same day's actual breakfast or dinner
- fitness is technically present on weekdays, but most normal-week sessions
  cluster on weekends because full fitness sessions compete with meals,
  supplements, work blocks, provider availability, and drift behavior
- labs and care check-ins should outrank support tasks and can roll forward, but
  the scheduler currently treats most failures as ordinary unscheduled rows
- travel and WFH are represented as availability blocks, but there is no single
  resolved day policy; travel days can still carry office work blocks

The rewrite should preserve the generated activity universe and audit artifacts,
but replace the scheduling core with explicit policy phases and placement
semantics.

## Goals

- Make daily food coverage an invariant: breakfast, lunch, and dinner must be
  scheduled every day unless an explicit fasting or meal-skip reason applies.
- Make daily medication coverage an invariant: medication/supplement tasks must
  be scheduled daily unless an explicit hold reason applies.
- Anchor medication timing to the same day's actual meal rows when the activity
  says it must be taken with breakfast or dinner.
- Make weekly fitness a weekly dose policy: schedule fitness within its target
  week; if no legal slot exists in that week, mark it missed and do not spill it
  into a later week.
- Let labs and care check-ins take priority over fitness/support tasks and roll
  forward one day at a time until they schedule or exit the planning horizon.
- Resolve member day context before placement: office, WFH, travel hotel,
  fasting, fatigue, provider availability, equipment, and work blocks.
- Keep the generated calendar believable: varied meals, weekday movement when
  realistic, provider-linked care where possible, and clear failure reasons.
- Preserve `decision_traces.json`, `personalized_plan.json`,
  `rejection_summary.json`, and calendar rows as auditable output contracts.

## Non-Goals

- Do not regenerate the entire activity board from scratch.
- Do not add an optimization solver dependency unless the phased scorer proves
  insufficient.
- Do not require new persistent data fields for this one-time demo rewrite.
  Scheduler classification should be derived from existing data plus a small
  code-side map for ambiguous families/actions.
- Do not make support-only tasks count toward clinical goals unless their
  `goal_contributions` already say they count.
- Do not hide unscheduled required work. Required failures should appear as
  explicit missed or delayed trace outcomes.

## Policy Model

### Task Classes

Each task receives one scheduler class before placement:

- `daily_required_food`: meal-slot food activities generated for daily coverage
- `daily_required_medication`: medication and supplement activities with daily
  frequency
- `rolling_priority`: labs, fasted testing, physician/dietitian/physio reviews,
  care-team handoffs, and behavior/coaching check-ins
- `weekly_required_fitness`: cardio, strength, mobility, and recovery fitness
  activities that represent weekly dose
- `weekly_support`: office walking breaks, recovery supports, hydration/CGM
  support, and other non-counting weekly aids
- `opportunistic`: as-needed rows and fallback substitutions that are useful
  only when another activity fails or when capacity remains

Task class is derived from existing activity fields first. Because this is a
one-time scheduler rewrite for a fixed demo dataset, ambiguous classification
should be handled with a small code-side map instead of adding persistent data
fields.

Derived classification rules:

- `daily_required_food`: `activity_type == "food"` and `meal_slot` is one of
  `breakfast`, `lunch`, or `dinner`
- `daily_required_medication`: `activity_type == "medication"` and
  `frequency.type == "daily"`
- `weekly_required_fitness`: `activity_type == "fitness"` and a counted goal
  contribution references `ga_aerobic_conditioning_weekly` or
  `ga_strength_sessions_weekly`
- `weekly_support`: support-only fitness/therapy/medication activities that do
  not count toward a core weekly target
- `opportunistic`: `frequency.type == "as_needed"` or fallback substitutions
  that do not satisfy a required class

Code-side maps cover ambiguous families/actions:

```python
ROLLING_PRIORITY_FAMILIES = {
    "b05_clinical_lab_draw_due_week",
    "b05_clinical_physician_review_due_week",
    "b05_clinical_dietitian_lab_followup",
    "b05_clinical_remote_care_team_handoff",
    "b05_clinical_dietitian_review_monthly",
    "b05_clinical_biometric_review_support",
}

OFFICE_BREAK_FAMILIES = {
    "b02_cardio_walking_office",
}

FITNESS_DOSE_ACTIONS = {
    "ga_aerobic_conditioning_weekly",
    "ga_strength_sessions_weekly",
}
```

The derivation rules and any map-based classification should be deterministic
and reported in traces.

### Retry And Spillover Rules

- `daily_required_food`: must schedule on its target date. It never spills.
- `daily_required_medication`: must schedule on its target date. It never spills.
- `rolling_priority`: tries its target date first, then the next date, repeating
  until scheduled or the planning horizon ends.
- `weekly_required_fitness`: can try any legal slot inside its target ISO week.
  It never spills into another week.
- `weekly_support`: can try any legal slot inside its target ISO week. It can be
  skipped when higher-priority work consumes the week.
- `opportunistic`: only schedules when policy explicitly enables it as a fallback
  or when all required classes have been placed for the relevant day/week.

## Day Policy

Before placing tasks, the scheduler builds a `DayPolicy` for every planning date.

### Location Resolution

The resolved member location for a date is:

1. `travel_hotel` when a `member_travel` block overlaps that date
2. `home` when a `member_location` WFH override exists
3. `office` for ordinary weekdays
4. `home` for ordinary weekends

Travel weekdays still have core work blocks, but those blocks are located in the
travel/hotel remote-work context, not the office. This means the member is still
working during weekday travel, but office-only activities should not be allowed
merely because the old recurring office block exists.

### Work Blocks

Day policy should derive work blocks from resolved context instead of relying on
expanded recurring office blocks:

- ordinary weekday: `08:30-18:30`, location `office`
- WFH weekday: `08:30-18:30`, location `home`
- travel weekday: `08:30-18:30`, location `travel_hotel` or `remote`
- weekend: no core work block unless an explicit block exists
- Wednesday late call: `20:30-22:00`, location `home` unless travel context
  requires it to be treated as remote/hotel
- Sunday family block: `09:00-13:00`, location `home`, except travel policy may
  suppress it or convert it to an explicit remote/family block only if the source
  data says so

Work blocks are not all-or-nothing. They allow low-complexity food, medication,
short office/WFH movement breaks, and short remote care check-ins when the
activity policy permits it. They block full fitness, in-person labs, and
high-load sessions.

### Meal Policy

For each date, generate three required meal anchors:

- breakfast
- lunch
- dinner

Location selection:

- travel day during active travel interval: `travel_hotel`
- WFH day: home meal options, with restaurant as dinner variety when allowed
- ordinary office weekday: breakfast at home, lunch at office, dinner at home or
  restaurant
- weekend: home or restaurant

Meal placement can use variety scoring, but coverage wins over variety. If a
planned-variety meal fails, the scheduler must fall back to another eligible
same-slot meal before declaring the slot missing.

Fasted metabolic testing may suppress or delay breakfast only when a lab/testing
activity carries an explicit fasting dependency for that date. The trace must
state that breakfast was skipped or delayed for fasting.

### Medication Policy

Daily medication rows must be placed every date. If a medication activity says it
is taken with breakfast or dinner, the scheduler anchors it to the same day's
scheduled breakfast or dinner row:

- default supplement timing: immediately after breakfast
- fallback timing: immediately after dinner when breakfast is unavailable due to
  fasting/testing or travel fatigue
- medication cannot satisfy its dependency from a prior date's meal

The UI may still compact medication rows into a "Habits" line, but the underlying
calendar row remains `activity_type = medication`.

### Fitness Policy

Weekly fitness should be scheduled by week-level dose, not by independent family
drift. The policy should distinguish:

- full aerobic session
- strength session
- mobility/recovery fitness
- short office/WFH movement break

Full sessions need realistic spacing and non-work windows unless they are
explicitly low-load and work-compatible. Short office/WFH movement breaks are
allowed inside work blocks when they are low-load, member-led, and short.

Weekly fitness cannot spill into a later week. If no legal slot exists in its
target week, the trace should record `fitness_missed_week` with the dominant
blocking reasons.

### Rolling Priority Policy

Labs and care check-ins are higher priority than weekly fitness and support. They
should roll forward day by day:

- lab and fasted testing attempts should prefer morning clinical/provider slots
- physician/dietitian/physio follow-ups should prefer provider availability
- remote care check-ins can use work-compatible short remote windows
- once scheduled, dependent follow-ups should re-evaluate from the scheduled date

If rolling priority work cannot schedule before the horizon ends, the trace
should record `rolling_priority_expired`.

## Placement Architecture

### Inputs

The scheduler consumes:

- task instances from the existing task-expansion step
- activity metadata from `action_plan.json`
- availability patterns or expanded availability blocks
- member profile scheduling rules and travel-time rules
- generated day policies

### Phases

The placement engine runs in deterministic phases:

1. Build day policies for the planning horizon.
2. Place labs and fasted testing anchors.
3. Place daily meals for every date.
4. Place daily medication anchored to same-day meals.
5. Place rolling care check-ins and consultations, allowing day-by-day rollover.
6. Place weekly fitness inside each target week only.
7. Place weekly support tasks, including office/WFH movement breaks.
8. Place opportunistic substitutions and variety rows only when legal capacity
   remains.

### Candidate Scoring

Candidate slots should be scored rather than accepted as first-valid. Score
components:

- required class priority
- same-day or same-week fit
- resolved member location match
- provider/resource fit
- meal/medication anchor fit
- work-block compatibility
- travel and fatigue compatibility
- movement spacing
- variety contribution
- lower conflict risk with future higher-priority tasks

The trace should include the selected score factors and the top rejection
reasons for rejected candidates.

## Availability Source Cleanup

The source availability model can remain unchanged for this one-time rewrite,
but the scheduler should stop treating recurring office work blocks as
authoritative during travel dates. Instead:

- keep travel windows as member-location overrides
- keep WFH dates as member-location overrides
- derive work blocks from `DayPolicy`
- preserve explicit blocks such as fatigue, late calls, and family time

This avoids contradictory states where the member is simultaneously in an office
block and a travel hotel context.

## Output Semantics

Traces should distinguish:

- `scheduled`
- `skipped_optional`
- `missed_required`
- `delayed_rolling`
- `expired_rolling`
- `blocked_by_policy`

Recommended reason codes:

- `meal_missing_without_skip_reason`
- `medication_missing_without_hold_reason`
- `fitness_missed_week`
- `rolling_priority_delayed`
- `rolling_priority_expired`
- `provider_unavailable`
- `member_work_block`
- `member_travel_context`
- `arrival_fatigue`
- `fasting_required`
- `meal_anchor_unavailable`
- `movement_spacing`

Existing JSON shape can be preserved initially by mapping these statuses into
the current `final_status` and adding richer summary fields. A follow-up UI pass
can render the more specific status labels after the scheduler semantics are
stable.

## Testing Strategy

Unit tests should verify:

- travel weekdays derive hotel/remote work blocks, not office work blocks
- WFH weekdays derive home work blocks
- ordinary weekdays derive office work blocks
- every day receives breakfast, lunch, and dinner unless a fasting skip reason is
  present
- daily medication schedules every day and anchors to same-day breakfast or
  dinner
- medication does not satisfy a same-day meal dependency from a prior date
- weekly fitness does not spill into the next week
- short office movement breaks can schedule inside ordinary office work blocks
- full/high-load fitness cannot schedule inside work blocks
- rolling labs/check-ins roll forward until scheduled

Demo-level tests should verify:

- no missing meal slots across the three-month run
- no missing medication dates across the three-month run
- fitness appears in a realistic weekday/weekend distribution
- travel meals and travel medications use hotel context during active travel
- provider-linked sessions still use available providers
- traces include explicit missed/delayed reasons for unscheduled required work

## Migration Plan

The rewrite should be implemented incrementally:

1. Add `DayPolicy` builder and tests without changing placement.
2. Move meal and medication placement onto the day-policy path.
3. Add rolling-priority placement for labs/check-ins.
4. Add weekly fitness dose placement with no spillover.
5. Move support tasks and office movement breaks to the support phase.
6. Make policy evaluation prefer derived day-policy work blocks over
   contradictory expanded recurring office blocks.
7. Regenerate demo artifacts and update UI labels only where status semantics
   changed.

## Open Decisions Resolved

- Travel weekdays keep core work blocks.
- Travel weekday work blocks are hotel/remote context, not office context.
- Food is daily required.
- Medication is daily required.
- Fitness is weekly required but cannot spill over.
- Labs and care check-ins outrank fitness/support and can roll forward day by
  day.
