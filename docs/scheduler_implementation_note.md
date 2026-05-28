# Scheduler Implementation Note

This note documents the current scheduler honestly for review and handoff. The generated calendar is now auditable and passes the final hard-constraint audit, but the scheduler implementation is not a clean optimizer. It is a deterministic greedy scheduler with several targeted repair passes added during review.

## Current Goal

The scheduler turns the canonical activity library into a 3-month member calendar for Marcus Tan. It must show that the Resource Allocator can:

- place required daily, weekly, monthly, and travel-window activities;
- adapt to member location, travel, WFH days, provider availability, equipment, and facility constraints;
- use same-family substitutions when the preferred activity is infeasible;
- expose enough decision trace data for a reviewer to understand why a row exists;
- produce final calendar rows that pass hard feasibility checks.

The implementation optimizes for explainability and assignment defensibility, not long-term scheduler architecture.

## Files Involved

Canonical inputs:

- `data/member_profile.json` - member goals, persona, goal actions, weekly targets, and care context.
- `data/activity_families.json` - source activity board with primary activities, substitutions, prep/dependencies, metrics, and goal contributions.
- `data/action_plan.json` - flattened scheduler-facing activity prescriptions derived from activity families.
- `data/availability_patterns.json` - compact recurring and dated availability rules.
- `data/availability.json` - expanded concrete availability blocks used by scheduling.
- `data/resource_universe.json` - providers, equipment, locations, and travel-time rules.

Scheduler and calendar code:

- `scripts/build_demo_run.py` - runs the full local data build.
- `scripts/flatten_action_plan.py` - converts activity families into `data/action_plan.json`.
- `scripts/validate_data.py` - validates canonical data before scheduling.
- `scripts/run_scheduler.py` - expands task instances and runs the scheduler.
- `src/scheduler/task_instances.py` - expands recurring activities into dated task instances and creates daily meal-coverage candidates.
- `src/scheduler/placement.py` - generates candidate slots and task ordering.
- `src/scheduler/policy.py` - evaluates member, timing, location, WFH, travel, fatigue, and overlap constraints.
- `src/scheduler/availability.py` - validates provider, equipment, and location availability.
- `src/scheduler/engine.py` - greedy scheduling loop, substitution handling, goal reporting, and repair passes.
- `src/scheduler/traces.py` - trace/handoff helpers.
- `src/calendar_view.py` - writes final calendar artifacts.
- `src/calendar_audit.py` - performs final hard-constraint audit over the produced calendar.
- `src/calendar_interface.py` - maps calendar artifacts into the UI payload.

Runtime outputs:

- `data/runs/demo-run/02_task_expansion/task_instances.json`
- `data/runs/demo-run/03_scheduling/personalized_plan.json`
- `data/runs/demo-run/03_scheduling/decision_traces.json`
- `data/runs/demo-run/03_scheduling/rejection_summary.json`
- `data/runs/demo-run/04_calendar/calendar_rows.json`
- `data/runs/demo-run/04_calendar/summary_report.md`
- `data/runs/demo-run/04_calendar/constraint_violations.json`

## Ordering Of Operations

The current pipeline is:

1. Flatten the generated activity-family board into scheduler-facing prescriptions.
2. Validate data shape, provider references, equipment references, activity counts, and modality coverage.
3. Expand activities into dated task instances.
4. Add daily meal-coverage candidates for breakfast, lunch, and dinner.
5. Group task instances by activity family occurrence so a primary and its substitutions compete for the same intended slot.
6. Run a greedy scheduling loop:
   - sort tasks by priority and cadence;
   - try the primary activity first unless planned-variety rules put a substitution first;
   - generate candidate slots from preferred days/windows and availability;
   - reject candidates that fail policy, resource, provider, or overlap checks;
   - schedule the first accepted candidate;
   - skip remaining substitutions for that same family occurrence once one activity is scheduled.
7. Apply targeted post-schedule repairs:
   - remove breakfast before fasting metabolic lab draws and add an explicit skipped-breakfast row;
   - align supplement reminders with breakfast or dinner timing and location;
   - repair weekly aerobic/strength target gaps where feasible;
   - remove same-day duplicate substantial fitness sessions;
   - prefer higher-resource travel fitness options, such as hotel gym or pool, when available.
8. Rebuild goal reports and weekly validation summaries.
9. Build final calendar rows and UI payloads.
10. Run the final hard-constraint audit and write `constraint_violations.json`.

## Hard Constraints Currently Audited

The final audit checks the generated calendar after all scheduling and repair work:

- member blocked windows, including Sunday family/meal-planning blocks;
- exact travel-window location validity, so `travel_hotel` rows only happen during active travel;
- WFH office ban for full WFH dates;
- arrival-fatigue load restrictions;
- provider availability at the selected time and location, including remote support;
- same-day location transition buffers from `data/resource_universe.json`.

The current generated demo run reports:

```text
status: pass
violation_count: 0
```

## Goal And Recap Validation

The scheduler reports weekly and 3-month performance through the goal report and recap UI. Current tracked targets include:

- structured meals capped as countable goal units rather than counting every meal row;
- member-assembled meal cap;
- estimated chef-prep session cap;
- aerobic sessions per week;
- strength sessions per week;
- recovery actions per week;
- consultation/provider-review goals across the full 3-month horizon.

These checks are not the same thing as hard feasibility. They answer, "Did the calendar meet the intended care plan?" The final constraint audit answers, "Can this person/provider/location actually support the scheduled row?"

## Known Design Debt

The scheduler is currently too patched. The main design issues are:

- It starts from flattened task instances, which makes weekly planning harder to reason about.
- Some policy is in pre-placement checks, some in activity ranking, and some in post-schedule repairs.
- Meal coverage, supplement anchoring, fasting labs, weekly fitness repair, and travel quality ranking are specialized code paths rather than a unified constraint model.
- Provider availability is now validated, but preferred activity windows and provider windows are still not modeled as a clean intersection-first planning problem.
- Substitution status and trace explanations are defensible, but they were added after the fact and are more verbose than the underlying algorithm deserves.
- The implementation can pass the current assignment data, but it would be difficult to extend safely for many members, changing goals, or real-time rescheduling.

## Why It Was Not Fully Rewritten

Near submission, the safer path was to make the produced calendar valid and auditable instead of replacing the scheduler. A full rewrite would risk breaking the UI, trace outputs, generated data, and Vercel runtime artifacts.

The current implementation is acceptable for a one-time synthetic assignment because:

- inputs and outputs are committed and reproducible;
- decision traces expose accepted and rejected choices;
- recap shows goal performance;
- final audit reports zero hard violations;
- tests pass against the current data and code path.

It should not be presented as a production-grade scheduler.

## Cleaner First-Principles Rewrite

The next scheduler should be week-first instead of flattened-task-first:

1. For each week, derive the member's exact availability, location state, travel state, WFH dates, fatigue restrictions, and blocked windows.
2. Build the required weekly demand list:
   - daily meals and medications;
   - due labs and consults;
   - aerobic, strength, recovery, and behavior-coaching targets;
   - travel-specific and phase-specific requirements.
3. Place fixed anchors first:
   - travel;
   - fasting labs and prep;
   - meals;
   - medications;
   - immovable provider appointments.
4. For each remaining activity need, compute feasible slots as an intersection of:
   - member free time;
   - activity preferred windows;
   - provider availability;
   - location availability;
   - equipment availability;
   - travel-time buffers;
   - load/fatigue restrictions.
5. Rank feasible options by plan quality:
   - primary before substitution;
   - better-equipped locations before lower-resource substitutions;
   - in-person provider support before remote/self-directed when clinically useful;
   - avoid stacking fitness and avoid overloading travel days.
6. Schedule one accepted option per activity need.
7. If a goal is not met, run a transparent repair loop that creates explicit repair rows with reason codes.
8. Validate the week before moving to the next week.
9. Emit calendar rows, goal summaries, rejected candidates, and constraint violations from the same planner state.

That design would make the scheduler easier to inspect and would remove many of the current patch-style repairs.

## Submission Read

For the assignment, the important claim is not that the scheduler is elegant. The claim is that the project demonstrates an auditable Resource Allocator:

- the activity board has realistic activities, providers, prep, substitutions, skip handling, and metrics;
- the generated calendar adapts to travel, WFH, fasting labs, provider availability, and equipment;
- the UI exposes activity details, calendar decisions, recap performance, and hard-constraint audit results;
- the final generated run is reproducible from committed data.

The scheduler internals should be treated as a prototype implementation with clear next-step refactor guidance.
