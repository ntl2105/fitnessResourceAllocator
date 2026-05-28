# Stage 04: Generate Availability Patterns

You are generating `data/availability_patterns.json`.

Availability patterns define 3 months of member and resource availability in a
compact, auditable format. A deterministic Python expander will convert these
patterns into `data/availability.json`.

## Inputs

You will receive:

- `member_profile.json`
- `resource_universe.json`
- `known_frictions.json`

## Output

Return one JSON object with:

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

`timezone` must always be a non-null IANA timezone string. Use
`"Asia/Singapore"` for remote, Singapore, broad horizon, and synthetic demo
patterns unless a specific travel window requires another timezone.

Weekly patterns must also include:

- `days`
- `start_time`
- `end_time`
- optional `start_date`
- optional `end_date`
- optional `skip_date_ranges`

Date-range or once patterns must also include:

- `start`
- `end`

Return strict JSON only. Do not include comments, markdown fences, explanatory
prose, or placeholder text.

## Allowed `resource_type` Values

- `member_blocked`
- `member_travel`
- `provider`
- `equipment`
- `location`
- `travel_window`

Do not use `resource_type: "member"`. Member work, fatigue, family, travel-day,
and high-stress windows should be `member_blocked`; active travel windows should
be `member_travel`.

## Required Coverage

Availability patterns must cover:

- member blocked windows
- member travel windows
- provider availability
- provider availability for every provider needed by activities
- chef/cook prep windows
- equipment availability where equipment is constrained
- lab availability
- clinic, gym, lab, and facility operating windows
- planned travel windows
- last-minute travel windows
- arrival-day low-readiness context after travel over 3 hours
- WFH date overrides when the member works from home
- occasional member unavailability during otherwise preferred fitness windows

## Resource-Specific Generation

Generate patterns for concrete resource IDs from `resource_universe.json`.

Do not invent provider, equipment, location, member, or travel IDs.

A candidate activity is feasible only when all required resources have
compatible expanded availability:

- member is free
- provider is available, if required
- equipment is available, if required
- location is available, if constrained
- travel state and location compatibility are valid
- remote delivery is supported when used
- WFH dates do not allow office-location activities
- arrival-fatigue windows restrict medium/high-load activity

## Realism Requirements

- Member blocked windows should reflect work hours and travel.
- Provider availability should be limited and not perfectly aligned with member
  preferences.
- Trainer availability should create at least one morning-preference mismatch.
- Lab availability should be weekday mornings only unless the resource universe
  says otherwise.
- Chef/cook prep should be available in limited batch-prep windows.
- Equipment/facility availability should include at least one limitation matching
  known frictions.
- Travel windows should create travel-compatible member/resource availability.
- Travel windows should apply only during their exact start/end timestamps, not
  automatically to the full calendar date.
- Planned travel should have better resources than last-minute travel.
- On the arrival day for any travel window over 3 hours, include a
  `member_blocked` fatigue or low-readiness pattern.
- Use WFH `member_location` date overrides for exactly two non-travel Fridays.
- Do not model airport transfers as scheduled activities. Local commute and
  transition buffers are handled through `resource_universe.travel_time_rules`.

## Output Size

Produce enough patterns that the deterministic expander can create roughly
150-300 concrete availability blocks across the 3-month planning window.

Aim for this expanded block distribution:

- total availability blocks: 225-375
- provider blocks: 120-200
- member_blocked blocks: 70-100
- equipment blocks: 10-30
- location blocks: 10-40
- member_travel plus travel_window blocks: 6

Use weekly patterns for recurring provider/member availability. Use date-range
patterns for exact travel windows and truly broad resource availability.

Provider and member calendars should be the main source of density and conflict.
Equipment should stay compact. Do not create daily equipment blocks for portable,
home, bodyweight, regular gym, or lab equipment unless there is a real
day-specific constraint.

The distribution target is mandatory. Use expansion math before returning:

- weekly pattern with 5 days ~= 65 expanded blocks
- weekly pattern with 3 days ~= 39 expanded blocks
- weekly pattern with 1 day ~= 13 expanded blocks
- date-range pattern = 1 expanded block

Location availability must normally use broad date-range patterns, not weekly
opening-hour patterns. Do not create weekly location patterns for home, office,
gym, clinic, or lab.

Member blocked availability should include one weekday work pattern, recurring
Sunday family/meal-planning time, occasional preferred-fitness-window blockers,
and exact fatigue/travel date ranges.

Provider availability must include no more than 12 total weekly day entries
across all provider patterns, so provider blocks land in the 120-200 range.
Do not create separate in-person and remote weekly patterns for every provider.

Use this target pattern shape unless the input data makes it impossible:

- 5 `member_blocked` patterns: one Monday-Friday work pattern, two recurring
  one-day non-work blockers, and two exact arrival-fatigue date ranges
- 3 `member_travel` date-range patterns, one per travel window
- 8-10 provider weekly patterns with exactly 12 total weekly day entries
- 10 equipment date-range patterns, one per equipment resource
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
- one additional remote travel-support provider slot: 1 weekly day entry

This sums to exactly 12 provider weekly day entries. Do not exceed it.

## Output Format

Return valid JSON only.
