# Seed Data Instructions

Generate five JSON files for a Resource Allocator demo:

1. `member_profile.json`
2. `resource_universe.json`
3. `known_frictions.json`
4. `activity_families.json`
5. `availability.json`

The dataset must cover June 1, 2026 through August 31, 2026.

Hard requirements:

- One member profile with a `journey_phases` timeline.
- Resource universe includes providers, equipment, locations, travel windows, and travel time rules.
- Include at least one trainer, physiotherapist, dietitian, physician, phlebotomist/lab, and chef/cook.
- Include planned monthly travel and one last-minute travel window.
- Activity families flatten to at least 100 scheduler-facing activities.
- At least 60 flattened activities are primary activities.
- Each family has one primary activity and realistic substitutions where needed.
- Every activity has exactly one activity type: `fitness`, `food`, `medication`, `therapy`, `consultation`.
- Include food prep dependencies and chef/member prep cases.
- Include the 8 demo scenarios from the design spec.
- Use consistent IDs across all files.

