# Seed Data Instructions

Generate five JSON files for a Resource Allocator demo:

1. `member_profile.json`
2. `resource_universe.json`
3. `known_frictions.json`
4. `activity_families.json`
5. `availability.json`

The dataset must cover June 1, 2026 through August 31, 2026.

Use `prompts/inputs/original_persona.md` as the source persona for `member_profile.json`.

Hard requirements:

- One member profile with a `journey_phases` timeline.
- Member goals include weekly and 3-month target definitions for calendar coverage.
- Member profile includes `goal_actions` that define concrete weekly and 3-month denominators.
- Resource universe includes providers, equipment, locations, travel windows, and minimal travel-state rules.
- Include at least one trainer, physiotherapist, dietitian, physician, phlebotomist/lab, and chef/cook.
- Include planned monthly travel and one last-minute travel window.
- Activity families flatten to at least 100 scheduler-facing activities.
- At least 60 flattened activities are primary activities.
- Each family has one primary activity and realistic substitutions where needed.
- Every activity has exactly one activity type: `fitness`, `food`, `medication`, `therapy`, `consultation`.
- Activities include conservative goal contribution metadata so goal coverage is interpretable.
- Activity families include `goal_action_ids` and only reference valid goal actions.
- Low-complexity support habits, supplements, and reminders should not inflate goal progress.
- Food activities include real breakfast, lunch, and dinner prescriptions where nutrition is part of the journey; supplement protocols do not count as meals.
- Include food prep dependencies and chef/member prep cases.
- Do not model detailed travel or commute time for this version.
- Travel over 3 hours should create arrival-day or next-day fatigue logic that can drive lower-load substitutions or recovery emphasis.
- Include the 8 demo scenarios from the design spec.
- Use consistent IDs across all files.
