# Known Frictions Rules

Known frictions are intentional, realistic conflicts that the generated data and scheduler should demonstrate.

They are not scheduler decisions. They are scenario constraints that should later appear in activities, availability, substitutions, decision traces, or unscheduled reasons.

Each friction must have a stable `friction_id` so validation and traces can reference it.

## Required friction coverage

Generate frictions covering:

1. planned travel with better facilities, such as hotel gym access
2. last-minute travel with limited facilities
3. provider availability mismatch with member preferences
4. lab or consultation disruption during travel
5. food prep dependency requiring chef or member prep
6. equipment or facility unavailability
7. post-travel fatigue after a location change over 3 hours
8. skipped or substituted high-load activity requiring recovery adjustment

## Friction shape

Each friction should include:

- `friction_id`
- `name`
- `description`
- `linked_resource_ids` or `affected_travel_window_ids` when applicable
- `date_range` when applicable
- `scheduler_expectation`

## Realism rules

Frictions should arise from plausible care coordination:

- A provider's calendar does not always match the member's preferred time.
- A travel destination may have a hotel gym but no trusted local physio.
- A last-minute trip may have only a hotel room and remote support.
- A lab may only be open weekday mornings.
- A food activity may require prep before consumption.
- A sauna or facility may be unavailable during maintenance.
- A high-load session after travel may need a recovery substitution.
- A travel day over 3 hours may make the member lower-readiness even when a location resource exists.

Avoid arbitrary contradictions that exist only to make the data hard.
