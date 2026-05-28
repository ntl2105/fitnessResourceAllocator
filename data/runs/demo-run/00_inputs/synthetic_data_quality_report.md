# Synthetic Data Quality Report

Status: pass
Activities: 101
Primary activities: 50
Availability blocks: 343
Modalities: consultation, fitness, food, medication, therapy

## Availability Block Counts
- equipment: 10
- location: 9
- member_blocked: 99
- member_location: 2
- member_travel: 3
- provider: 216
- scheduling_rule: 1
- travel_window: 3

## Validation Checks
- PASS: at_least_100_activities - Found 101 activities.
- PASS: exactly_50_activity_families - Found 50 activity families.
- PASS: unique_activity_ids - No duplicate IDs found.
- PASS: all_modalities_present - Present modalities: consultation, fitness, food, medication, therapy.
- PASS: provider_references_resolve - All provider references resolve.
- PASS: equipment_references_resolve - All equipment references resolve.
- PASS: location_references_resolve - All location references resolve.
- PASS: substitution_references_resolve - All substitution references resolve.
- PASS: member_has_journey_phases - Found 7 journey phases.
- PASS: member_has_goal_actions - Found 8 goal actions.
- PASS: goal_taxonomy_replaces_travel_continuity - Travel-continuity action removed and replacement goal actions are present.
- PASS: active_data_omits_removed_goal_actions - Active activities and families omit removed goal actions.
- PASS: activity_goal_action_references_resolve - All activity goal action references resolve.
- PASS: activity_family_goal_action_references_resolve - All activity family goal action references resolve.
- PASS: activity_family_targets_present - Activity family targets are complete.
- PASS: substitution_target_alignment - Substitutions preserve family-level counted targets.
- PASS: availability_has_3_months - Planning months: 3.
- PASS: availability_has_blocks - Found 343 availability blocks.
- PASS: availability_has_realistic_block_density - Availability coverage found 343 blocks; expected 225-375 concrete scheduler-facing blocks for a 3-month demo.
- PASS: availability_keeps_equipment_compact - Found 10 equipment blocks; expected 30 or fewer so equipment does not dominate the audit data.
- PASS: availability_distribution_matches_targets - Availability resource-type counts match target ranges.
- PASS: availability_covers_planning_months - Availability coverage spans expected months 2026-06, 2026-07, 2026-08.
