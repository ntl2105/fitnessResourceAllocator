# Availability Pattern Rules

Availability is an exogenous constraint. It should not magically match the
member's preferences.

The LLM generates compact availability patterns, not the final
`availability.json`. A deterministic Python expander converts those patterns
into concrete scheduler-facing `availability_blocks`.

## Required Output Content

Return one strict JSON object with:

- `planning_start_date`
- `planning_months`
- `patterns`

Each pattern must include:

- `pattern_id`
- `type`
- `resource_id`
- `resource_type`
- `timezone`
- `location_id`
- `remote_supported`
- `travel_compatible`
- `notes`

Return strict JSON only. Do not include comments, markdown fences, explanatory
prose, or placeholder text inside the JSON.

`timezone` must always be a non-null IANA timezone string. Use
`"Asia/Singapore"` for remote, Singapore, broad horizon, and synthetic demo
patterns unless a specific travel window requires another timezone.

## Pattern Types

Use `type: "weekly"` for recurring windows. A weekly pattern must include:

- `days`, such as `["monday", "wednesday"]`
- `start_time`, such as `"18:45"`
- `end_time`, such as `"20:15"`
- optional `start_date`
- optional `end_date`
- optional `skip_date_ranges`, where each item has `start` and `end` dates

Use `type: "date_range"` for exact travel windows, broad equipment/location
availability, arrival fatigue windows, and one-off constraints. A date-range
pattern must include:

- `start`
- `end`

Use `type: "once"` only for a one-off block that is not naturally a date range.
It also requires `start` and `end`.

## Allowed Resource Types

- `member_blocked` for member work blocks, fatigue blocks, meals/events, and
  other periods where the member should not be scheduled
- `member_travel` for active travel windows that change the member's location
- `provider` for provider availability
- `equipment` for equipment availability
- `location` for physical or remote location availability
- `travel_window` only when representing a travel-window resource directly

Do not use `resource_type: "member"` because the scheduler does not treat that
as a constraint.

## Required Coverage

Patterns must cover 3 months and include:

- member blocked windows
- member travel windows
- arrival-day low-readiness or fatigue context after travel over 3 hours
- provider availability by provider ID
- chef/cook prep windows by provider ID
- equipment availability where equipment is constrained
- lab availability by lab/provider/equipment/location ID
- clinic, gym, lab, and facility operating windows
- planned travel windows
- last-minute travel windows
- WFH date overrides
- occasional member unavailability during preferred fitness windows

## Realism Rules

- Member work blocks should reflect typical work hours.
- Providers should have limited, realistic availability.
- Trainer availability should not perfectly match the member's preferred
  morning schedule.
- Lab availability should be constrained, usually weekday mornings.
- Physician availability should be limited and not always immediate after labs.
- Dietitian or coach availability can be more remote-friendly but still finite.
- Chef/cook availability should support batch prep but not unlimited daily prep.
- Equipment/facility availability should include at least one unavailability or
  travel limitation matching known frictions.
- Travel windows should create travel-compatible member/resource availability.
- Planned travel should have better resources than last-minute travel.
- Travel over 3 hours should create a fatigue or reduced-readiness context on
  the arrival day.
- Travel location state should apply only inside exact travel-window timestamps,
  not automatically to the whole calendar date.
- WFH days should hard-ban office-location activities.
- Do not model airport transfers as scheduled member activities. Local
  transition buffers are modeled in `resource_universe.travel_time_rules`.

## Expansion Expectations

The expanded `availability.json` should normally contain roughly 150-300
concrete blocks for a 3-month demo. The pattern file should stay readable.

Aim for this expanded block distribution:

- total availability blocks: 225-375
- provider blocks: 120-200
- member_blocked blocks: 70-100
- equipment blocks: 10-30
- location blocks: 10-40
- member_travel plus travel_window blocks: 6

Provider and member calendars should carry most of the scheduling density and
conflict. Equipment availability should stay compact and should not dominate the
block count.

The distribution is a hard target, not a soft preference. Avoid any weekly
pattern that would blow up a category count.

Expansion math:

- a weekly pattern with 5 days expands to about 65 blocks over 3 months
- a weekly pattern with 3 days expands to about 39 blocks
- a weekly pattern with 1 day expands to about 13 blocks
- a date-range pattern expands to 1 block

Member-blocked patterns should be limited to:

- one weekday work pattern, Monday-Friday
- two recurring evening, family/social, or late-call blockers, each on exactly
  one day
- exact travel fatigue date ranges

Do not create separate weekly member blockers for every dinner, call, weekend
event, and work session if that would push `member_blocked` above 100.

Provider patterns must have no more than 12 total weekly day entries across all
providers. For example, one trainer pattern with three days counts as three
weekly day entries. Do not create separate in-person and remote weekly patterns
for every provider. Use notes to explain remote flexibility unless the separate
remote slot is critical to a demo scenario.

Location availability should generally use broad date-range patterns, not weekly
opening-hour patterns. Do not create weekly `location` patterns for home, office,
gym, clinic, or lab unless a location is genuinely constrained by a specific
recurring day. Use provider/equipment availability to constrain actual use.

For this assignment, the safest target shape is:

- 5 `member_blocked` patterns: one Monday-Friday work pattern, two recurring
  one-day non-work blockers, and two exact arrival-fatigue date ranges
- 3 `member_travel` date-range patterns, one per travel window
- 8-10 provider weekly patterns with exactly 12 total weekly day entries
- 10 equipment date-range patterns, one per equipment resource from the resource
  universe
- 7 location date-range patterns, one per canonical location
- 3 `travel_window` date-range patterns, one per travel window ID

Provider target structure:

- trainer: 2 weekly day entries
- physiotherapist: 1 weekly day entry
- dietitian: 1 weekly day entry
- physician: 1 weekly day entry
- lab/phlebotomist: 3 weekly day entries
- chef/cook: 2 weekly day entries
- remote coach pool: 1 weekly day entry
- one additional remote travel-support slot for the provider most relevant to
  travel adaptation: 1 weekly day entry

That sums to exactly 12 provider weekly day entries.

Good compact pattern choices:

- weekly member work blocks
- weekly provider windows
- weekly chef prep windows
- exact travel-window date ranges
- broad date ranges for portable equipment, remote access, or location
  availability when those resources are genuinely broad

Do not hide scheduler-relevant recurrence only in notes. If a provider is
available every Wednesday evening, represent it as a weekly pattern.

Do not expand equipment availability day-by-day unless the equipment is
genuinely constrained by day.

Use broad date-range patterns for:

- portable equipment
- home equipment
- bodyweight equipment
- home kitchen
- regular gym equipment
- lab equipment when tied to lab operating windows

Use specific date-range patterns only for:

- travel-only equipment
- maintenance or unavailability windows
- destination-specific facilities such as a Hong Kong pool or Tokyo basic gym

## Travel Handling

During travel:

- member location should be represented as travel-compatible
- home, office, gym, clinic, and lab should generally not be assumed available
- remote providers can still be available if their provider blocks support
  remote delivery
- travel hotel resources should reflect destination quality
- planned travel may include hotel gym or pool resources
- last-minute travel may include only hotel-room or remote resources
- arrival after travel over 3 hours should bias availability notes toward
  recovery, lower load, or reduced same-day capacity

Do not create travel lab access unless it is explicitly present in the resource
universe.

## Important Distinction

`resource_universe.json` defines what resources exist.

`availability_patterns.json` defines recurring and exact availability rules.

`availability.json` is produced by the deterministic expander and defines when
each resource can actually be used by the scheduler.
