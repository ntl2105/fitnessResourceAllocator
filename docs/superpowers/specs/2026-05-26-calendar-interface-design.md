# Calendar Interface Design

## Goal

Replace the current flat calendar table with a reviewer-first weekly calendar interface that makes the allocator output human-verifiable while preserving the existing file-backed audit trail.

## Problem

The current `calendar_rows.json` artifact is correct but too row-oriented for human review. A reviewer has to scan hundreds of rows and open raw trace JSON manually to understand travel adaptations, substitutions, unavailable time, travel buffers, and rejected candidates.

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
calendar_rows + availability + traces + rejection_summary
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
- Scenario chips for travel adaptations, substitutions, travel-time rejections, blocked-time rejections, remote sessions, high-load activities, and unscheduled summary.
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
  "scenario_counts": {
    "travel_adaptation": 108,
    "substitution": 129
  },
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
