# Calendar Interface Design

## Goal

Replace the current flat calendar table with a reviewer-first weekly calendar interface that makes the allocator output human-verifiable while preserving the existing file-backed audit trail.

## Problem

The current `calendar_rows.json` artifact is correct but too row-oriented for human review. A reviewer has to scan hundreds of rows and open raw trace JSON manually to understand travel adaptations, substitutions, unavailable time, travel buffers, and rejected candidates.

The first visual pass surfaced a second problem: the calendar can show scheduled rows, but it does not yet explain whether the schedule is good. A reviewer needs to see goal coverage, unscheduled work, provider ownership, member location, travel blocks, and human-readable activity names directly in the calendar.

## Chosen Approach

Port the useful parts of the Figma weekly calendar into the existing FastAPI/Jinja app using plain HTML, CSS, and browser JavaScript. Do not add Vite, React, or a frontend build step for this assignment slice.

The Figma export is a good visual reference because its `WeeklyCalendar.tsx` component is a simple week grid:

- seven day columns
- hourly vertical positioning
- colored activity blocks
- gray unavailable overlays
- week navigation
- goal/progress area

The implementation should reproduce that behavior in the current app and populate it from committed JSON artifacts.

## Data Flow

The app already writes these canonical artifacts:

- `data/runs/demo-run/04_calendar/calendar_rows.json`
- `data/runs/demo-run/03_scheduling/decision_traces.json`
- `data/runs/demo-run/03_scheduling/rejection_summary.json`
- `data/runs/demo-run/00_inputs/availability.json`

Add a Python view-model layer that converts these artifacts into a browser-friendly structure:

```text
calendar_rows + personalized_plan + availability + traces + rejection_summary + resource_universe
  -> calendar interface view model
  -> /api/calendar/interface
  -> static browser renderer
```

This keeps the browser code simple and makes the hard mapping logic testable in Python.

## Interface Requirements

The `/calendar` page should show:

- A weekly grid with previous/next week navigation.
- Day columns and time rows covering the normal scheduling window.
- Activity blocks positioned by `start_time` and `end_time`.
- Unavailable overlays from `member_blocked` availability blocks.
- Domain colors for the five modalities: consultation, fitness, food, medication, therapy.
- Badges for remote, travel hotel, substitution, high load, dependency, and trace rejection.
- Review filter chips for travel adaptations, substitutions, travel-time rejections, blocked-time rejections, remote sessions, high-load activities, and dependencies.
- Review filter chip counts are scoped to the selected week, not the full three-month run. The UI must say: "Counts reflect the selected week. Filtering only affects visible activities in this week."
- A goal coverage panel that shows selected-week and full-plan progress by goal tag.
- An at-risk/unscheduled panel that shows activities that did not find placement, grouped by goal and activity.
- Location bands under the day headers showing where the member is located or unavailable, such as Singapore, office, planned travel, last-minute travel, and in transit.
- Travel blocks for exact travel times when available. Travel is a member constraint and should appear as blocked time in the calendar, not only as metadata.
- Provider or specialist information on activity cards when a provider is assigned or required.
- Display names for activity cards that are cleaner than raw scheduler names. Raw names remain in JSON and trace artifacts.
- A click-driven trace drawer showing policy fit, resource fit, provider handoff summary, failed checks, rejected candidate examples, and source artifacts.

The UI is read-only. It must not mutate the scheduler output.

## View Model

`src/calendar_interface.py` should expose a function that returns:

```python
{
  "weeks": [
    {
      "week_id": "2026-W23",
      "start_date": "2026-06-01",
      "end_date": "2026-06-07",
      "days": [
        {"date": "2026-06-01", "label": "Mon Jun 1"}
      ],
      "activities": [
        {
          "id": "row_task_act_...",
          "title": "...",
          "date": "2026-06-01",
          "day_index": 0,
          "start_hour": 7.0,
          "duration_hours": 0.75,
          "activity_type": "fitness",
          "location_id": "gym",
          "mode": "in_person",
          "load_level": "medium",
          "substitution_status": "primary",
          "trace_id": "trace_task_...",
          "badges": ["trace_rejections"],
          "scenario_flags": ["blocked_time_rejection"]
        }
      ],
      "unavailable_blocks": [
        {
          "date": "2026-06-01",
          "day_index": 0,
          "start_hour": 8.5,
          "duration_hours": 10.0,
          "label": "Work block."
        }
      ]
    }
  ],
  "run_scenario_counts": {
    "travel_adaptation": 108,
    "substitution": 129
  },
  "goal_coverage": {
    "week": [
      {"goal_tag": "metabolic_health", "scheduled": 6, "unscheduled": 1, "status": "at_risk"}
    ],
    "full_plan": [
      {"goal_tag": "metabolic_health", "scheduled": 54, "unscheduled": 4, "status": "on_track"}
    ]
  },
  "unscheduled_items": [
    {
      "activity_id": "act_019",
      "title": "Zone 2 stationary bike session",
      "goal_tags": ["cardio", "metabolic_health"],
      "unscheduled_count": 1,
      "rejected_candidate_count": 14,
      "reason_summary": "No candidate slot passed policy and resource checks."
    }
  ],
  "rejection_summary": {...}
}
```

Weeks should start on Monday because the generated planning horizon begins on Monday and this is more natural for work/travel review. The Figma component starts on Sunday, but the implementation should use Monday-first weeks.

## Scenario Flags

Each activity can have zero or more scenario flags:

- `remote`: `mode == "remote"`
- `travel_adaptation`: `location_id == "travel_hotel"` or a remote row during a member travel window
- `substitution`: `substitution_status == "substitution"`
- `high_load`: `load_level == "high"`
- `trace_rejections`: selected trace has rejected candidates
- `travel_time_rejection`: trace contains a failed `travel_time_buffer` check
- `blocked_time_rejection`: trace or rejected candidates mention member blocked time
- `dependency`: trace has dependency checks beyond `dependencies_acknowledged`

Scenario chips filter/highlight activities using these flags.

The counts shown in the chip labels must be computed from the currently selected week in the browser. Run-level counts can remain in the API for summary panels, but they should not be used as weekly filter labels.

## Goal Coverage

Goal coverage is computed from scheduled calendar rows and unscheduled traces:

- Scheduled counts come from `calendar_rows[*].goal_tags`.
- Unscheduled counts come from traces whose `final_status == "unscheduled"`.
- Rejected candidate counts come from trace `rejected_candidates`.
- A goal is `missed` in a selected week if it has unscheduled work and no scheduled work.
- A goal is `at_risk` if it has scheduled work but also unscheduled work or substitutions.
- A goal is `on_track` if it has scheduled work and no unscheduled work in that scope.

This is intentionally a coverage indicator, not a clinical outcome engine.

## Location And Travel Display

The calendar should show member location context separately from activities:

- `member_blocked` blocks appear under day headers as member context, such as office time or fixed personal commitments.
- `member_travel` blocks appear as location bands spanning all affected days.
- Travel blocks with exact start/end times should also appear in the day agenda as unavailable rows.
- If the seed data only has all-day travel windows, the UI can show a travel band, but the data-generation requirements must be updated to require exact travel legs.

## Providers And Specialist Display

Provider display should resolve from scheduler output and `resource_universe.json`:

- Use scheduled task `provider_ids` from `personalized_plan.json`.
- Resolve provider display names and provider types from `resource_universe.json`.
- Show compact provider text on each activity card, such as `Maya Tan, trainer`.
- If no provider is assigned but the activity has a facilitator type, show the facilitator type only.

## Activity Display Names

Calendar cards should use human display names. The raw activity title stays available in the trace drawer and audit files.

Display-name rules:

- Remove leading delivery/substitution prefixes such as `Remote or hotel-gym substitution:`.
- Remove awkward fallback/prep prefixes when they obscure the actual activity.
- Keep important distinctions as badges or metadata, such as `remote`, `hotel gym`, `fallback`, `chef prep`, or `substitution`.
- Preserve clinical meaning: do not rename activities so broadly that a reviewer cannot tell what was scheduled.

Food activities need stricter generation rules. The activity board should include breakfast, lunch, and dinner activities where food consumption is part of the plan. Supplements and medication protocols do not count as meals. Chef/member prep should be separate prerequisite work only when prep actually has to occur.

## Trace Drawer

Clicking an activity opens a drawer without leaving the page. The drawer should fetch `/api/traces/{trace_id}` and show:

- title/time/location metadata from the activity block
- `policy_fit_summary`
- `resource_fit_summary`
- `provider_handoff_summary`
- failed `constraint_checks`
- first few `rejected_candidates`
- `dependency_checks`
- `source_artifact_paths`

The raw trace endpoint remains available for detailed audit.

## Out Of Scope

- Drag/drop scheduling.
- Editing activities.
- A React/Vite frontend build.
- Full month view.
- Mobile-perfect calendar interactions.
- Replacing the audit page.

## Testing

Tests should cover:

- week grouping and Monday-first day indexes
- time conversion from `HH:MM` to decimal hours
- unavailable block mapping from `member_blocked`
- scenario flagging
- trace linking and trace-derived flags
- `/api/calendar/interface` shape
- `/calendar` includes the static renderer bootstrap

Manual verification should include opening `/calendar`, switching weeks, applying at least one scenario chip, and opening a trace drawer.

The reviewer should also verify that the first week answers these questions without opening raw JSON:

- Which goals are on track, at risk, or missed?
- Which activities failed to schedule?
- Where is the member each day?
- Which travel periods block activity scheduling?
- Which provider or specialist owns each provider-led activity?
- Which activity names still look like raw prompt artifacts rather than human calendar entries?
