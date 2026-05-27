# Stage 03: Generate Known Frictions

You are generating `data/known_frictions.json`.

Known frictions are realistic conflicts the scheduler should later demonstrate.

## Inputs

You will receive:

- `member_profile.json`
- `resource_universe.json`

## Output

Return one JSON object with a top-level key:

- `frictions`

Each friction must include:

- `friction_id`
- `name`
- `description`
- `linked_resource_ids` or `affected_travel_window_ids` where applicable
- `date_range` when applicable
- `scheduler_expectation`

## Required coverage

Generate frictions covering all of the following:

1. planned travel with better facilities, such as hotel gym access
2. last-minute travel with limited facilities
3. provider availability mismatch with member preferences
4. lab or consultation disruption during travel
5. food prep dependency requiring chef or member prep
6. equipment or facility unavailability
7. post-travel fatigue after a location change over 3 hours
8. skipped or substituted high-load activity requiring recovery adjustment

## ID discipline

Use only provider IDs, equipment IDs, location IDs, and travel window IDs from `resource_universe.json`.

Do not invent new resources.

## Realism

Frictions should be plausible and later traceable. Each friction should explain what scheduler behavior it is meant to exercise.

## Output format

Return valid JSON only.
