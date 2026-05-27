# Batch Instructions

Activities should be generated in small coherent batches of activity families.

Each batch should contain the exact number of activity families requested by
the batch scope.

Each family should contain:

- exactly one primary activity
- zero to three substitution activities when realistic
- substitution rules when substitutions exist

## Batch coherence

Each batch should focus on a care stream, not a date range.

Good batch themes:

- cardiovascular fitness and mobility
- strength and knee-safe training
- nutrition and metabolic health
- medication and supplement adherence
- sleep and recovery therapy
- PT, trainer, physician, and dietitian consultations
- lab testing and physician follow-up
- travel adaptations inside the relevant care stream
- adherence adaptations inside the relevant care stream

Chronology belongs to the scheduler, not the batch.

## Cross-batch requirements

Across all generated batches, the final flattened `action_plan.json` must contain:

- at least 100 scheduler-facing activity prescriptions
- exactly 50 primary activity families
- substitutions counted separately and linked to families
- all five activity types represented

Do not inflate counts with low-value duplicate substitutions.

## ID rules

Use stable, non-overlapping IDs.

Examples:

- `fam_strength_001`
- `act_strength_001_primary`
- `act_strength_001_remote_travel`

If a batch index or ID prefix is provided, use it exactly.

## Avoid duplicates

Before generating a batch, use the provided existing activity summaries to avoid duplicating the same prescription.

Similar activities are allowed only when they serve distinct purposes, phases, frequencies, providers, or constraints.
