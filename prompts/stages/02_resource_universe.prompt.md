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

## Travel-state rules

Keep `travel_time_rules` present for schema compatibility, but keep it minimal for this version.

The current schema expects each travel-time rule to include:

- `from_location_id`
- `to_location_id`
- `minutes`

Use a minimal compatibility rule such as `office` to `gym` with `15` minutes. Do not build a detailed transportation model. The important scheduling constraint for now is member location state and travel fatigue after travel over 3 hours, not exact commute buffers.

## Important constraint

This is the final stage where new provider, equipment, and location IDs may be created.

Later stages must only reference IDs from this file.

## Output format

Return valid JSON only.
