# Calendar Interface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the flat row table at `/calendar` with a Figma-style weekly review calendar populated from the existing scheduler artifacts.

**Architecture:** Add a Python calendar-interface view model that groups rows into Monday-first weeks, maps availability into unavailable overlays, and derives scenario flags from traces. Render that view model with static CSS and browser JavaScript in the existing FastAPI/Jinja app; do not add React, Vite, or a frontend build step.

**Tech Stack:** Python, FastAPI, Jinja2, pytest, vanilla JavaScript, CSS, committed JSON artifacts.

---

## File Structure

- `src/calendar_interface.py`
  - Builds the reviewer-facing calendar view model from `calendar_rows`, `availability`, `decision_traces`, and `rejection_summary`.
- `tests/test_calendar_interface.py`
  - Unit tests for week grouping, time conversion, unavailable overlays, scenario flags, and trace-derived flags.
- `src/app.py`
  - Adds `GET /api/calendar/interface`.
- `tests/test_app.py`
  - Adds route smoke tests for the new API and calendar static bootstrap.
- `src/templates/calendar.html`
  - Replaces the flat table with static containers for the weekly grid, scenario chips, and trace drawer.
- `src/static/calendar.css`
  - Figma-style weekly grid, activity blocks, badges, drawer, and controls.
- `src/static/calendar.js`
  - Fetches `/api/calendar/interface`, renders weeks, filters scenario chips, and loads trace drawer details.

---

### Task 1: Calendar Interface View Model

**Files:**
- Create: `src/calendar_interface.py`
- Create: `tests/test_calendar_interface.py`

- [ ] **Step 1: Write failing tests for view-model helpers**

Create `tests/test_calendar_interface.py`:

```python
from datetime import date

from src.calendar_interface import (
    build_calendar_interface,
    decimal_hour,
    duration_hours,
    monday_start,
)


def test_time_helpers_convert_calendar_row_times():
    assert decimal_hour("07:00") == 7.0
    assert decimal_hour("13:30") == 13.5
    assert duration_hours("07:15", "08:45") == 1.5


def test_monday_start_uses_work_week_boundary():
    assert monday_start(date(2026, 6, 1)).isoformat() == "2026-06-01"
    assert monday_start(date(2026, 6, 7)).isoformat() == "2026-06-01"
```

- [ ] **Step 2: Run helper tests and verify failure**

Run:

```bash
pytest tests/test_calendar_interface.py -q
```

Expected: fail because `src.calendar_interface` does not exist.

- [ ] **Step 3: Implement helper functions**

Create `src/calendar_interface.py`:

```python
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from typing import Any


WEEK_DAYS = 7
DISPLAY_START_HOUR = 6
DISPLAY_END_HOUR = 22


def decimal_hour(value: str) -> float:
    hour_text, minute_text = value.split(":", maxsplit=1)
    return int(hour_text) + int(minute_text) / 60


def duration_hours(start_time: str, end_time: str) -> float:
    return round(decimal_hour(end_time) - decimal_hour(start_time), 2)


def monday_start(value: date) -> date:
    return value - timedelta(days=value.weekday())
```

- [ ] **Step 4: Run helper tests and verify pass**

Run:

```bash
pytest tests/test_calendar_interface.py -q
```

Expected: 2 passed.

- [ ] **Step 5: Add tests for weeks, unavailable blocks, and scenario flags**

Append to `tests/test_calendar_interface.py`:

```python
def test_build_calendar_interface_groups_rows_and_member_blocked_overlays():
    calendar_rows = [
        {
            "calendar_row_id": "row_1",
            "date": "2026-06-02",
            "start_time": "07:30",
            "end_time": "08:15",
            "title": "Remote physio",
            "activity_type": "therapy",
            "goal_tags": ["travel_continuity"],
            "load_level": "low",
            "location_id": "remote",
            "mode": "remote",
            "substitution_status": "substitution",
            "trace_id": "trace_1",
            "compact_group_key": "2026-06-02:therapy",
        }
    ]
    availability = {
        "availability_blocks": [
            {
                "resource_type": "member_blocked",
                "start": "2026-06-02T08:30:00+08:00",
                "end": "2026-06-02T18:30:00+08:00",
                "notes": "Work block.",
                "location_id": "office",
            }
        ]
    }
    traces = [
        {
            "trace_id": "trace_1",
            "final_status": "scheduled",
            "rejected_candidates": [{"reasons": ["office->gym requires 15 minutes; only 5 minutes available after Work block."]}],
            "constraint_checks": [
                {"name": "travel_time_buffer", "passed": False, "reason": "office->gym requires 15 minutes; only 5 minutes available."}
            ],
            "dependency_checks": [],
        }
    ]

    view_model = build_calendar_interface(calendar_rows, availability, traces, {})

    assert view_model["display_hours"] == {"start": 6, "end": 22}
    assert view_model["scenario_counts"]["remote"] == 1
    assert view_model["scenario_counts"]["substitution"] == 1
    assert view_model["scenario_counts"]["travel_time_rejection"] == 1

    week = view_model["weeks"][0]
    assert week["week_id"] == "2026-W23"
    assert week["start_date"] == "2026-06-01"
    assert week["days"][1]["date"] == "2026-06-02"

    activity = week["activities"][0]
    assert activity["day_index"] == 1
    assert activity["start_hour"] == 7.5
    assert activity["duration_hours"] == 0.75
    assert set(activity["scenario_flags"]) >= {"remote", "substitution", "trace_rejections", "travel_time_rejection"}

    block = week["unavailable_blocks"][0]
    assert block["day_index"] == 1
    assert block["start_hour"] == 8.5
    assert block["duration_hours"] == 10.0
    assert block["label"] == "Work block."
```

- [ ] **Step 6: Run tests and verify failure**

Run:

```bash
pytest tests/test_calendar_interface.py -q
```

Expected: fail because `build_calendar_interface` is not implemented.

- [ ] **Step 7: Implement view-model builder**

Replace `src/calendar_interface.py` with:

```python
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from typing import Any


WEEK_DAYS = 7
DISPLAY_START_HOUR = 6
DISPLAY_END_HOUR = 22
SCENARIOS = [
    "remote",
    "travel_adaptation",
    "substitution",
    "high_load",
    "trace_rejections",
    "travel_time_rejection",
    "blocked_time_rejection",
    "dependency",
]


def decimal_hour(value: str) -> float:
    hour_text, minute_text = value.split(":", maxsplit=1)
    return int(hour_text) + int(minute_text) / 60


def duration_hours(start_time: str, end_time: str) -> float:
    return round(decimal_hour(end_time) - decimal_hour(start_time), 2)


def monday_start(value: date) -> date:
    return value - timedelta(days=value.weekday())


def build_calendar_interface(
    calendar_rows: list[dict[str, Any]],
    availability: dict[str, Any],
    traces: list[dict[str, Any]],
    rejection_summary: dict[str, Any],
) -> dict[str, Any]:
    traces_by_id = {trace["trace_id"]: trace for trace in traces}
    travel_windows = member_travel_windows(availability)
    rows_by_week: dict[date, list[dict[str, Any]]] = defaultdict(list)
    for row in calendar_rows:
        row_date = date.fromisoformat(row["date"])
        rows_by_week[monday_start(row_date)].append(row)

    blocked_by_week: dict[date, list[dict[str, Any]]] = defaultdict(list)
    for block in availability.get("availability_blocks", []):
        if block.get("resource_type") != "member_blocked":
            continue
        block_start = datetime.fromisoformat(block["start"])
        blocked_by_week[monday_start(block_start.date())].append(block)

    scenario_counts: Counter[str] = Counter()
    weeks = []
    for week_start in sorted(set(rows_by_week) | set(blocked_by_week)):
        activities = [
            activity_view(row, week_start, traces_by_id.get(row.get("trace_id")), travel_windows)
            for row in sorted(
                rows_by_week.get(week_start, []),
                key=lambda item: (item["date"], item["start_time"], item["title"]),
            )
        ]
        for activity in activities:
            scenario_counts.update(activity["scenario_flags"])

        weeks.append(
            {
                "week_id": iso_week_id(week_start),
                "start_date": week_start.isoformat(),
                "end_date": (week_start + timedelta(days=6)).isoformat(),
                "label": week_label(week_start),
                "days": week_days(week_start),
                "activities": activities,
                "unavailable_blocks": [
                    unavailable_view(block, week_start)
                    for block in sorted(
                        blocked_by_week.get(week_start, []),
                        key=lambda item: item["start"],
                    )
                ],
            }
        )

    return {
        "display_hours": {"start": DISPLAY_START_HOUR, "end": DISPLAY_END_HOUR},
        "scenarios": SCENARIOS,
        "scenario_counts": {scenario: scenario_counts.get(scenario, 0) for scenario in SCENARIOS},
        "weeks": weeks,
        "rejection_summary": rejection_summary,
    }


def activity_view(
    row: dict[str, Any],
    week_start: date,
    trace: dict[str, Any] | None,
    travel_windows: list[tuple[date, date]],
) -> dict[str, Any]:
    row_date = date.fromisoformat(row["date"])
    flags = scenario_flags(row, trace, travel_windows)
    badges = badges_for(row, flags)
    return {
        "id": row["calendar_row_id"],
        "title": row["title"],
        "date": row["date"],
        "day_index": (row_date - week_start).days,
        "start_hour": decimal_hour(row["start_time"]),
        "duration_hours": duration_hours(row["start_time"], row["end_time"]),
        "start_time": row["start_time"],
        "end_time": row["end_time"],
        "activity_type": row["activity_type"],
        "goal_tags": row.get("goal_tags", []),
        "load_level": row["load_level"],
        "location_id": row.get("location_id"),
        "mode": row["mode"],
        "substitution_status": row["substitution_status"],
        "trace_id": row.get("trace_id"),
        "badges": badges,
        "scenario_flags": flags,
    }


def unavailable_view(block: dict[str, Any], week_start: date) -> dict[str, Any]:
    start = datetime.fromisoformat(block["start"])
    end = datetime.fromisoformat(block["end"])
    return {
        "date": start.date().isoformat(),
        "day_index": (start.date() - week_start).days,
        "start_hour": round(start.hour + start.minute / 60, 2),
        "duration_hours": round((end - start).total_seconds() / 3600, 2),
        "label": block.get("notes") or block.get("resource_id") or "Unavailable",
        "location_id": block.get("location_id"),
    }


def scenario_flags(
    row: dict[str, Any],
    trace: dict[str, Any] | None,
    travel_windows: list[tuple[date, date]],
) -> list[str]:
    flags: set[str] = set()
    row_date = date.fromisoformat(row["date"])
    if row.get("mode") == "remote":
        flags.add("remote")
    if row.get("location_id") == "travel_hotel" or (
        row.get("mode") == "remote" and any(start <= row_date <= end for start, end in travel_windows)
    ):
        flags.add("travel_adaptation")
    if row.get("substitution_status") == "substitution":
        flags.add("substitution")
    if row.get("load_level") == "high":
        flags.add("high_load")
    if trace:
        if trace.get("rejected_candidates"):
            flags.add("trace_rejections")
        checks = trace.get("constraint_checks", [])
        if any(check.get("name") == "travel_time_buffer" and check.get("passed") is False for check in checks):
            flags.add("travel_time_rejection")
        reason_text = " ".join(
            reason
            for candidate in trace.get("rejected_candidates", [])
            for reason in candidate.get("reasons", [])
        ).lower()
        if "member blocked" in reason_text:
            flags.add("blocked_time_rejection")
        dependency_checks = trace.get("dependency_checks", [])
        if any(check.get("name") != "dependencies_acknowledged" for check in dependency_checks if isinstance(check, dict)):
            flags.add("dependency")
    return sorted(flags)


def badges_for(row: dict[str, Any], flags: list[str]) -> list[str]:
    badges = []
    if "remote" in flags:
        badges.append("remote")
    if row.get("location_id") == "travel_hotel":
        badges.append("travel hotel")
    if "substitution" in flags:
        badges.append("substitution")
    if "high_load" in flags:
        badges.append("high load")
    if "dependency" in flags:
        badges.append("dependency")
    if "trace_rejections" in flags:
        badges.append("rejections")
    return badges


def member_travel_windows(availability: dict[str, Any]) -> list[tuple[date, date]]:
    windows = []
    for block in availability.get("availability_blocks", []):
        if block.get("resource_type") != "member_travel":
            continue
        windows.append(
            (
                datetime.fromisoformat(block["start"]).date(),
                datetime.fromisoformat(block["end"]).date(),
            )
        )
    return windows


def week_days(week_start: date) -> list[dict[str, str]]:
    return [
        {
            "date": (week_start + timedelta(days=offset)).isoformat(),
            "label": (week_start + timedelta(days=offset)).strftime("%a %b %-d"),
        }
        for offset in range(WEEK_DAYS)
    ]


def week_label(week_start: date) -> str:
    return f"{week_start.strftime('%b %-d')} - {(week_start + timedelta(days=6)).strftime('%b %-d, %Y')}"


def iso_week_id(week_start: date) -> str:
    iso = week_start.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"
```

- [ ] **Step 8: Run view-model tests**

Run:

```bash
pytest tests/test_calendar_interface.py -q
```

Expected: all tests pass.

- [ ] **Step 9: Commit**

Run:

```bash
git add src/calendar_interface.py tests/test_calendar_interface.py
git commit -m "feat: build calendar interface view model"
```

---

### Task 2: Calendar Interface API

**Files:**
- Modify: `src/app.py`
- Modify: `tests/test_app.py`

- [ ] **Step 1: Add failing API route test**

Append to `tests/test_app.py`:

```python
def test_calendar_interface_api_returns_weeks_and_scenarios():
    response = client.get("/api/calendar/interface")

    assert response.status_code == 200
    payload = response.json()
    assert payload["weeks"]
    assert "remote" in payload["scenario_counts"]
    assert "substitution" in payload["scenario_counts"]
    assert payload["display_hours"] == {"start": 6, "end": 22}
    first_week = payload["weeks"][0]
    assert len(first_week["days"]) == 7
    assert "activities" in first_week
    assert "unavailable_blocks" in first_week
```

- [ ] **Step 2: Run route test and verify failure**

Run:

```bash
pytest tests/test_app.py::test_calendar_interface_api_returns_weeks_and_scenarios -q
```

Expected: fail with 404.

- [ ] **Step 3: Implement route**

Modify `src/app.py` imports:

```python
from src.calendar_interface import build_calendar_interface
```

Add route after `api_plan`:

```python
@app.get("/api/calendar/interface")
def api_calendar_interface() -> Any:
    calendar_rows = load_json(RUN_DIR / "04_calendar" / "calendar_rows.json")
    availability = load_json(RUN_DIR / "00_inputs" / "availability.json")
    traces = load_json(RUN_DIR / "03_scheduling" / "decision_traces.json")
    rejection_summary = load_json(RUN_DIR / "03_scheduling" / "rejection_summary.json")
    return build_calendar_interface(calendar_rows, availability, traces, rejection_summary)
```

- [ ] **Step 4: Run app tests**

Run:

```bash
pytest tests/test_app.py -q
```

Expected: all app tests pass.

- [ ] **Step 5: Commit**

Run:

```bash
git add src/app.py tests/test_app.py
git commit -m "feat: expose calendar interface api"
```

---

### Task 3: Static Calendar Renderer

**Files:**
- Create: `src/static/calendar.css`
- Create: `src/static/calendar.js`
- Modify: `src/app.py`
- Modify: `src/templates/calendar.html`
- Modify: `tests/test_app.py`

- [ ] **Step 1: Mount static files**

Modify `src/app.py` imports:

```python
from fastapi.staticfiles import StaticFiles
```

Add constants near `TEMPLATES_DIR`:

```python
STATIC_DIR = Path(__file__).resolve().parent / "static"
```

After `templates = ...`, add:

```python
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
```

- [ ] **Step 2: Add failing template smoke test**

Append to `tests/test_app.py`:

```python
def test_calendar_page_bootstraps_weekly_interface_assets():
    response = client.get("/calendar")

    assert response.status_code == 200
    assert 'id="calendar-root"' in response.text
    assert "/static/calendar.css" in response.text
    assert "/static/calendar.js" in response.text
    assert "/api/calendar/interface" in response.text
```

- [ ] **Step 3: Replace calendar template**

Replace `src/templates/calendar.html` with:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Elyx Weekly Calendar</title>
  <link rel="stylesheet" href="/static/calendar.css">
</head>
<body>
  <header class="app-header">
    <div>
      <h1>Elyx Weekly Calendar</h1>
      <p>{{ row_count }} scheduled rows from the latest run</p>
    </div>
    <nav>
      <a href="/calendar">Calendar</a>
      <a href="/summary">Summary</a>
      <a href="/audit">Audit</a>
    </nav>
  </header>

  <main id="calendar-root" data-source="/api/calendar/interface">
    <section class="toolbar">
      <button type="button" id="previous-week">Previous Week</button>
      <div>
        <div class="eyebrow">Selected Week</div>
        <h2 id="week-label">Loading...</h2>
      </div>
      <button type="button" id="next-week">Next Week</button>
    </section>

    <section class="scenario-panel">
      <div class="eyebrow">Review Scenarios</div>
      <div id="scenario-chips" class="chips"></div>
    </section>

    <section class="calendar-shell">
      <div id="calendar-grid" class="calendar-grid" aria-live="polite"></div>
    </section>
  </main>

  <aside id="trace-drawer" class="trace-drawer" aria-hidden="true">
    <div class="drawer-header">
      <div>
        <div class="eyebrow">Decision Trace</div>
        <h2 id="drawer-title">Select an activity</h2>
      </div>
      <button type="button" id="close-drawer">Close</button>
    </div>
    <div id="drawer-content" class="drawer-content"></div>
  </aside>

  <script src="/static/calendar.js" defer></script>
</body>
</html>
```

- [ ] **Step 4: Add CSS**

Create `src/static/calendar.css`:

```css
:root {
  --hour-height: 64px;
  --line: #d9e2ec;
  --text: #1f2933;
  --muted: #52606d;
  --bg: #f7f8fa;
  --panel: #ffffff;
  --consultation: #2563eb;
  --fitness: #059669;
  --food: #d97706;
  --medication: #7c3aed;
  --therapy: #db2777;
}

* { box-sizing: border-box; }
body { margin: 0; font-family: Arial, sans-serif; color: var(--text); background: var(--bg); }
.app-header { display: flex; justify-content: space-between; gap: 24px; align-items: center; padding: 18px 28px; background: #14213d; color: white; }
.app-header h1 { margin: 0; font-size: 26px; }
.app-header p { margin: 4px 0 0; color: #cbd5e1; }
nav { display: flex; gap: 16px; }
nav a { color: white; font-weight: 700; text-decoration: none; }
main { padding: 20px 28px 36px; }
.toolbar, .scenario-panel { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 16px; padding: 16px; background: var(--panel); border: 1px solid var(--line); }
button { border: 1px solid #cbd5e1; background: white; padding: 8px 12px; border-radius: 6px; cursor: pointer; }
button:hover { background: #f1f5f9; }
.eyebrow { color: var(--muted); font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: .04em; }
#week-label { margin: 2px 0 0; font-size: 20px; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { border-radius: 999px; }
.chip.active { background: #14213d; color: white; border-color: #14213d; }
.calendar-shell { overflow-x: auto; background: var(--panel); border: 1px solid var(--line); }
.calendar-grid { min-width: 980px; }
.calendar-header, .calendar-body { display: grid; grid-template-columns: 68px repeat(7, minmax(120px, 1fr)); }
.calendar-header > div { padding: 10px; border-bottom: 1px solid var(--line); border-left: 1px solid var(--line); background: #edf2f7; font-weight: 700; text-align: center; }
.time-column { border-right: 1px solid var(--line); }
.time-cell { height: var(--hour-height); border-bottom: 1px solid var(--line); text-align: right; padding: 4px 8px; color: var(--muted); font-size: 12px; }
.day-column { position: relative; border-left: 1px solid var(--line); min-height: calc(var(--hour-height) * 16); }
.hour-line { height: var(--hour-height); border-bottom: 1px solid var(--line); }
.unavailable { position: absolute; left: 0; right: 0; background: rgba(148, 163, 184, .35); border-top: 1px solid rgba(100, 116, 139, .35); border-bottom: 1px solid rgba(100, 116, 139, .35); font-size: 11px; color: #334155; padding: 3px 5px; overflow: hidden; }
.activity { position: absolute; left: 4px; right: 4px; color: white; border-radius: 6px; padding: 6px; overflow: hidden; border: 1px solid rgba(255,255,255,.4); box-shadow: 0 1px 3px rgba(15, 23, 42, .25); text-align: left; }
.activity.hidden { display: none; }
.activity-title { font-size: 12px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.activity-meta { margin-top: 3px; font-size: 11px; opacity: .9; }
.badges { display: flex; flex-wrap: wrap; gap: 3px; margin-top: 4px; }
.badge { background: rgba(255,255,255,.22); border-radius: 999px; padding: 1px 5px; font-size: 10px; }
.type-consultation { background: var(--consultation); }
.type-fitness { background: var(--fitness); }
.type-food { background: var(--food); }
.type-medication { background: var(--medication); }
.type-therapy { background: var(--therapy); }
.trace-drawer { position: fixed; top: 0; right: 0; width: min(520px, 100vw); height: 100vh; background: white; border-left: 1px solid var(--line); box-shadow: -8px 0 24px rgba(15, 23, 42, .18); transform: translateX(100%); transition: transform .18s ease; z-index: 20; display: flex; flex-direction: column; }
.trace-drawer.open { transform: translateX(0); }
.drawer-header { padding: 18px; border-bottom: 1px solid var(--line); display: flex; justify-content: space-between; gap: 12px; }
.drawer-header h2 { margin: 2px 0 0; font-size: 18px; }
.drawer-content { padding: 18px; overflow: auto; }
.drawer-content h3 { margin: 18px 0 6px; }
.drawer-content pre { white-space: pre-wrap; background: #f8fafc; border: 1px solid var(--line); padding: 10px; }
```

- [ ] **Step 5: Add JavaScript renderer**

Create `src/static/calendar.js`:

```javascript
const state = {
  model: null,
  weekIndex: 0,
  activeScenario: null,
};

const root = document.getElementById("calendar-root");
const grid = document.getElementById("calendar-grid");
const weekLabel = document.getElementById("week-label");
const chips = document.getElementById("scenario-chips");
const drawer = document.getElementById("trace-drawer");
const drawerTitle = document.getElementById("drawer-title");
const drawerContent = document.getElementById("drawer-content");

function topFor(hour) {
  return (hour - state.model.display_hours.start) * 64;
}

function heightFor(duration) {
  return Math.max(duration * 64, 24);
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  }[char]));
}

function renderScenarioChips() {
  chips.innerHTML = "";
  for (const scenario of state.model.scenarios) {
    const count = state.model.scenario_counts[scenario] || 0;
    const button = document.createElement("button");
    button.type = "button";
    button.className = `chip ${state.activeScenario === scenario ? "active" : ""}`;
    button.textContent = `${scenario.replaceAll("_", " ")} (${count})`;
    button.onclick = () => {
      state.activeScenario = state.activeScenario === scenario ? null : scenario;
      render();
    };
    chips.appendChild(button);
  }
}

function render() {
  const week = state.model.weeks[state.weekIndex];
  weekLabel.textContent = week ? week.label : "No scheduled weeks";
  renderScenarioChips();
  if (!week) {
    grid.innerHTML = "";
    return;
  }

  const hours = [];
  for (let hour = state.model.display_hours.start; hour < state.model.display_hours.end; hour += 1) {
    hours.push(hour);
  }

  grid.innerHTML = `
    <div class="calendar-header">
      <div></div>
      ${week.days.map((day) => `<div>${escapeHtml(day.label)}</div>`).join("")}
    </div>
    <div class="calendar-body">
      <div class="time-column">
        ${hours.map((hour) => `<div class="time-cell">${formatHour(hour)}</div>`).join("")}
      </div>
      ${week.days.map((day, dayIndex) => renderDayColumn(week, dayIndex, hours)).join("")}
    </div>
  `;
}

function renderDayColumn(week, dayIndex, hours) {
  const unavailable = week.unavailable_blocks
    .filter((block) => block.day_index === dayIndex)
    .map((block) => `<div class="unavailable" style="top:${topFor(block.start_hour)}px;height:${heightFor(block.duration_hours)}px">${escapeHtml(block.label)}</div>`)
    .join("");

  const activities = week.activities
    .filter((activity) => activity.day_index === dayIndex)
    .map(renderActivity)
    .join("");

  return `
    <div class="day-column">
      ${hours.map(() => '<div class="hour-line"></div>').join("")}
      ${unavailable}
      ${activities}
    </div>
  `;
}

function renderActivity(activity) {
  const hidden = state.activeScenario && !activity.scenario_flags.includes(state.activeScenario);
  const badges = activity.badges.map((badge) => `<span class="badge">${escapeHtml(badge)}</span>`).join("");
  return `
    <button
      type="button"
      class="activity type-${escapeHtml(activity.activity_type)} ${hidden ? "hidden" : ""}"
      style="top:${topFor(activity.start_hour)}px;height:${heightFor(activity.duration_hours)}px"
      data-trace-id="${escapeHtml(activity.trace_id)}"
      data-title="${escapeHtml(activity.title)}"
    >
      <div class="activity-title">${escapeHtml(activity.title)}</div>
      <div class="activity-meta">${escapeHtml(activity.start_time)}-${escapeHtml(activity.end_time)} · ${escapeHtml(activity.location_id || activity.mode)}</div>
      <div class="badges">${badges}</div>
    </button>
  `;
}

function formatHour(hour) {
  if (hour === 12) return "12pm";
  if (hour > 12) return `${hour - 12}pm`;
  return `${hour}am`;
}

async function openTrace(traceId, title) {
  if (!traceId) return;
  drawer.classList.add("open");
  drawer.setAttribute("aria-hidden", "false");
  drawerTitle.textContent = title || traceId;
  drawerContent.innerHTML = "<p>Loading trace...</p>";
  const response = await fetch(`/api/traces/${traceId}`);
  const trace = await response.json();
  const failedChecks = (trace.constraint_checks || []).filter((check) => check.passed === false);
  drawerContent.innerHTML = `
    <p><strong>Status:</strong> ${escapeHtml(trace.final_status)}</p>
    <p><strong>Policy:</strong> ${escapeHtml(trace.policy_fit_summary)}</p>
    <p><strong>Resources:</strong> ${escapeHtml(trace.resource_fit_summary)}</p>
    <p><strong>Handoff:</strong> ${escapeHtml(trace.provider_handoff_summary || "None")}</p>
    <h3>Failed Checks</h3>
    ${failedChecks.length ? `<ul>${failedChecks.map((check) => `<li><strong>${escapeHtml(check.name)}:</strong> ${escapeHtml(check.reason)}</li>`).join("")}</ul>` : "<p>No failed checks on selected slot.</p>"}
    <h3>Rejected Candidates</h3>
    <pre>${escapeHtml(JSON.stringify((trace.rejected_candidates || []).slice(0, 5), null, 2))}</pre>
    <h3>Source Artifacts</h3>
    <ul>${(trace.source_artifact_paths || []).map((path) => `<li>${escapeHtml(path)}</li>`).join("")}</ul>
  `;
}

document.getElementById("previous-week").onclick = () => {
  state.weekIndex = Math.max(0, state.weekIndex - 1);
  render();
};

document.getElementById("next-week").onclick = () => {
  state.weekIndex = Math.min(state.model.weeks.length - 1, state.weekIndex + 1);
  render();
};

document.getElementById("close-drawer").onclick = () => {
  drawer.classList.remove("open");
  drawer.setAttribute("aria-hidden", "true");
};

grid.addEventListener("click", (event) => {
  const activity = event.target.closest(".activity");
  if (!activity) return;
  openTrace(activity.dataset.traceId, activity.dataset.title);
});

fetch(root.dataset.source)
  .then((response) => response.json())
  .then((model) => {
    state.model = model;
    render();
  })
  .catch((error) => {
    grid.innerHTML = `<p>Failed to load calendar interface: ${escapeHtml(error.message)}</p>`;
  });
```

- [ ] **Step 6: Run app tests**

Run:

```bash
pytest tests/test_app.py -q
```

Expected: all app tests pass.

- [ ] **Step 7: Commit**

Run:

```bash
git add src/app.py src/templates/calendar.html src/static/calendar.css src/static/calendar.js tests/test_app.py
git commit -m "feat: render weekly calendar interface"
```

---

### Task 4: Verification And Polish

**Files:**
- Modify only files from Tasks 1-3 if verification finds issues.

- [ ] **Step 1: Run full tests**

Run:

```bash
pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Start local app**

Run:

```bash
python -m uvicorn src.app:app --host 127.0.0.1 --port 8000
```

Expected: app starts at `http://127.0.0.1:8000`.

- [ ] **Step 3: Verify routes**

Open or fetch:

```text
http://127.0.0.1:8000/calendar
http://127.0.0.1:8000/api/calendar/interface
http://127.0.0.1:8000/api/traces/trace_task_act_001_20260604_001
```

Expected:

- `/calendar` shows the weekly grid.
- Scenario chips are visible.
- Previous/next buttons switch weeks.
- Activity click opens a trace drawer.
- `/api/calendar/interface` returns weeks and scenario counts.

- [ ] **Step 4: Browser visual verification**

Use the browser to inspect `/calendar` at desktop width. Check:

- no large overlap between header, toolbar, scenario chips, and grid
- activity blocks are visible inside day columns
- unavailable blocks are gray overlays
- drawer opens and is readable
- long activity names truncate inside blocks

- [ ] **Step 5: Commit any polish fixes**

If fixes were needed:

```bash
git add src/calendar_interface.py src/app.py src/templates/calendar.html src/static/calendar.css src/static/calendar.js tests
git commit -m "fix: polish weekly calendar interface"
```

If no fixes were needed, do not create an empty commit.

---

## Self-Review

- Spec coverage: The plan implements the Figma-style weekly grid, row-to-activity mapping, unavailable overlays, scenario chips, and trace drawer.
- Scope: No React/Vite build is introduced. The implementation stays inside the current FastAPI app.
- Testability: Mapping logic is in Python and covered by unit tests. Browser JavaScript is intentionally thin and verified through route smoke tests plus manual/browser verification.
- Known tradeoff: Browser rendering is not unit-tested with a JavaScript test runner. That is acceptable for this MVP because the complex logic is in `src/calendar_interface.py`.
