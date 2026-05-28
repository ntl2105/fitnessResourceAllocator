# Stage 02: Generate Resource Universe

You are generating `data/resource_universe.json`.

Use the provided `member_profile.json` as the source of truth.

## Inputs

You will receive:

- `member_profile.json`

## Output

Return one JSON object with these top-level collections:

- `providers`
- `equipment`
- `locations`
- `travel_windows`
- `travel_time_rules`

## Required provider coverage

Include at least one provider for each:

- trainer
- physiotherapist
- dietitian
- physician
- phlebotomist or lab provider
- chef/cook

Additional provider types such as coach or recovery therapist are allowed when useful.

## Required location coverage

Include:

- home
- office
- gym
- clinic
- lab
- travel hotel
- remote

Use stable IDs:

- `home`
- `office`
- `gym`
- `clinic`
- `lab`
- `travel_hotel`
- `remote`

## Travel windows

Copy or normalize travel windows from the member profile. Preserve their meaning. Use stable `travel_window_id` values.

## Transition And Travel-State Rules

Use `travel_time_rules` to represent practical same-day transition buffers that
the scheduler must honor between local locations.

The current schema expects each travel-time rule to include:

- `from_location_id`
- `to_location_id`
- `minutes`

Include transition rules for relevant pairs such as:

- `home` to/from `office`
- `home` to/from `gym`
- `office` to/from `gym`
- `home` or `office` to/from `clinic`
- `home` or `office` to/from `lab`
- `home` to/from `restaurant`

Use realistic but coarse buffers, such as 15-45 minutes. These are not meant to
be a full transportation model; they exist so the scheduler can reject
back-to-back rows in different locations.

Do not model airport transfers as member calendar rows. Travel windows should
still be represented as exact travel-state intervals, and post-arrival fatigue
after travel over 3 hours should remain a scheduling constraint.

## Important constraint

This is the final stage where new provider, equipment, and location IDs may be created.

Later stages must only reference IDs from this file.

## Output format

Return valid JSON only.
