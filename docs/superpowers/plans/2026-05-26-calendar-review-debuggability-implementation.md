# Calendar Review Debuggability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the weekly calendar a human-reviewable debugging surface that shows selected-week filter counts, goal coverage, unscheduled work, location/travel context, providers, and cleaner activity names.

**Architecture:** Extend the existing file-backed calendar view model instead of adding a frontend framework. Enrich rows in Python from `personalized_plan.json`, `resource_universe.json`, traces, rejection summary, and availability; keep browser JavaScript focused on rendering and selected-week filtering.

**Tech Stack:** Python, FastAPI, pytest, Jinja2, vanilla JavaScript, CSS, committed JSON artifacts.

---

## File Structure

- Modify: `src/calendar_interface.py`
  - Add provider resolution, display-name normalization, goal coverage, unscheduled summaries, location bands, travel blocks, and run/week scenario count support.
- Modify: `src/app.py`
  - Load `personalized_plan.json` and `resource_universe.json` into `/api/calendar/interface`.
- Modify: `src/static/calendar.js`
  - Render review panels, selected-week filter counts, location bands, travel/unavailable rows, provider text, and cleaner labels.
- Modify: `src/static/calendar.css`
  - Style review panels, location bands, travel rows, provider metadata, and at-risk states.
- Modify: `tests/test_calendar_interface.py`
  - Unit-test the enriched view model.
- Modify: `tests/test_app.py`
  - Route/static tests for review UI hooks.
- Later modify seed/prompt files:
  - `data/runs/demo-run/00_inputs/activity_families.json`
  - `data/runs/demo-run/00_inputs/availability.json`
  - `prompts/` fragments
  - This pass should expose data issues first; regeneration can happen after the UI makes the issues obvious.

---

### Task 1: Enrich Activities With Providers And Display Names

**Files:**
- Modify: `src/calendar_interface.py`
- Modify: `src/app.py`
- Test: `tests/test_calendar_interface.py`
- Test: `tests/test_app.py`

- [ ] **Step 1: Write failing provider/display-name test**

Append to `tests/test_calendar_interface.py`:

```python
def test_activity_view_resolves_provider_and_clean_display_title():
    calendar_rows = [
        {
            "calendar_row_id": "row_task_1",
            "date": "2026-06-01",
            "start_time": "18:45",
            "end_time": "19:30",
            "title": "Remote or hotel-gym substitution: Trainer-led lower-body strength session",
            "activity_type": "fitness",
            "goal_tags": ["strength"],
            "load_level": "medium",
            "location_id": "remote",
            "mode": "remote",
            "substitution_status": "substitution",
            "trace_id": "trace_1",
        }
    ]
    personalized_plan = {
        "tasks": [
            {
                "task_id": "task_1",
                "activity_id": "act_1",
                "provider_ids": ["provider_trainer_001"],
            }
        ]
    }
    resource_universe = {
        "providers": [
            {
                "provider_id": "provider_trainer_001",
                "provider_type": "trainer",
                "display_name": "Maya Tan",
            }
        ]
    }

    view_model = build_calendar_interface(
        calendar_rows,
        {"availability_blocks": []},
        [{"trace_id": "trace_1", "rejected_candidates": [], "constraint_checks": [], "dependency_checks": []}],
        {},
        personalized_plan,
        resource_universe,
    )

    activity = view_model["weeks"][0]["activities"][0]
    assert activity["raw_title"] == "Remote or hotel-gym substitution: Trainer-led lower-body strength session"
    assert activity["display_title"] == "Trainer-led lower-body strength session"
    assert activity["provider_summary"] == "Maya Tan, trainer"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_calendar_interface.py::test_activity_view_resolves_provider_and_clean_display_title -q
```

Expected: fail because `build_calendar_interface` does not accept `personalized_plan` or `resource_universe`.

- [ ] **Step 3: Implement task/provider lookup and display-title helpers**

In `src/calendar_interface.py`, change the function signature:

```python
def build_calendar_interface(
    calendar_rows: list[dict[str, Any]],
    availability: dict[str, Any],
    traces: list[dict[str, Any]],
    rejection_summary: dict[str, Any],
    personalized_plan: dict[str, Any] | None = None,
    resource_universe: dict[str, Any] | None = None,
) -> dict[str, Any]:
```

Add helpers:

```python
def task_id_from_row(row: dict[str, Any]) -> str | None:
    row_id = row.get("calendar_row_id", "")
    return row_id.removeprefix("row_") if row_id.startswith("row_") else None


def tasks_by_id(personalized_plan: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    return {
        task["task_id"]: task
        for task in (personalized_plan or {}).get("tasks", [])
        if task.get("task_id")
    }


def providers_by_id(resource_universe: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    return {
        provider["provider_id"]: provider
        for provider in (resource_universe or {}).get("providers", [])
        if provider.get("provider_id")
    }


def provider_summary(task: dict[str, Any] | None, providers: dict[str, dict[str, Any]]) -> str | None:
    if not task:
        return None
    labels = []
    for provider_id in task.get("provider_ids", []):
        provider = providers.get(provider_id)
        if provider:
            labels.append(f"{provider.get('display_name', provider_id)}, {provider.get('provider_type', 'provider')}")
        else:
            labels.append(provider_id)
    return "; ".join(labels) if labels else None


def display_title(raw_title: str) -> str:
    prefixes = [
        "Remote or hotel-gym substitution:",
        "No-prep fallback for",
        "Fallback:",
        "Substitution:",
    ]
    title = raw_title
    for prefix in prefixes:
        if title.startswith(prefix):
            title = title[len(prefix):].strip()
    return title[:1].upper() + title[1:] if title else raw_title
```

Inside `build_calendar_interface`, create:

```python
plan_tasks = tasks_by_id(personalized_plan)
providers = providers_by_id(resource_universe)
```

Pass both into `activity_view(...)`.

In `activity_view`, add:

```python
task = plan_tasks.get(task_id_from_row(row) or "")
return {
    ...
    "title": display_title(row["title"]),
    "display_title": display_title(row["title"]),
    "raw_title": row["title"],
    "provider_summary": provider_summary(task, providers),
    ...
}
```

- [ ] **Step 4: Update app API inputs**

In `src/app.py`, update `api_calendar_interface()`:

```python
personalized_plan = load_json(RUN_DIR / "03_scheduling" / "personalized_plan.json")
resource_universe = load_json(RUN_DIR / "00_inputs" / "resource_universe.json")
return build_calendar_interface(
    calendar_rows,
    availability,
    traces,
    rejection_summary,
    personalized_plan,
    resource_universe,
)
```

- [ ] **Step 5: Run tests**

Run:

```bash
pytest tests/test_calendar_interface.py tests/test_app.py -q
```

Expected: pass.

- [ ] **Step 6: Commit**

```bash
git add src/calendar_interface.py src/app.py tests/test_calendar_interface.py tests/test_app.py
git commit -m "feat: enrich calendar activities for review"
```

---

### Task 2: Add Goal Coverage And Unscheduled Review Model

**Files:**
- Modify: `src/calendar_interface.py`
- Test: `tests/test_calendar_interface.py`

- [ ] **Step 1: Write failing goal coverage test**

Append to `tests/test_calendar_interface.py`:

```python
def test_goal_coverage_reports_week_and_full_plan_risk():
    calendar_rows = [
        {
            "calendar_row_id": "row_task_1",
            "date": "2026-06-02",
            "start_time": "07:00",
            "end_time": "07:40",
            "title": "Zone 2 bike",
            "activity_type": "fitness",
            "goal_tags": ["cardio"],
            "load_level": "medium",
            "location_id": "gym",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": "trace_1",
        }
    ]
    traces = [
        {"trace_id": "trace_1", "activity_id": "act_1", "final_status": "scheduled", "rejected_candidates": [], "constraint_checks": [], "dependency_checks": []},
        {"trace_id": "trace_2", "activity_id": "act_2", "final_status": "unscheduled", "policy_fit_summary": "No valid slot.", "rejected_candidates": [{"reasons": ["No provider available."]}], "constraint_checks": [], "dependency_checks": [], "task_instance_id": "task_2"},
    ]

    view_model = build_calendar_interface(
        calendar_rows,
        {"availability_blocks": []},
        traces,
        {"act_2": {"unscheduled_count": 1, "rejected_candidate_count": 1}},
        {"tasks": [{"task_id": "task_2", "activity_id": "act_2", "goal_tags": ["cardio"], "status": "unscheduled"}]},
        {"providers": []},
    )

    week_cardio = view_model["goal_coverage"]["week"][0]
    assert week_cardio["goal_tag"] == "cardio"
    assert week_cardio["scheduled"] == 1
    assert week_cardio["unscheduled"] == 1
    assert week_cardio["status"] == "at_risk"
    assert view_model["unscheduled_items"][0]["activity_id"] == "act_2"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_calendar_interface.py::test_goal_coverage_reports_week_and_full_plan_risk -q
```

Expected: fail because goal coverage is missing.

- [ ] **Step 3: Implement goal coverage helpers**

Add to `src/calendar_interface.py`:

```python
def goal_status(scheduled: int, unscheduled: int, substitutions: int) -> str:
    if unscheduled and not scheduled:
        return "missed"
    if unscheduled or substitutions:
        return "at_risk"
    return "on_track" if scheduled else "no_activity"


def goal_coverage(
    calendar_rows: list[dict[str, Any]],
    traces: list[dict[str, Any]],
    personalized_plan: dict[str, Any] | None,
) -> dict[str, list[dict[str, Any]]]:
    plan_tasks = tasks_by_id(personalized_plan)
    unscheduled_by_goal: Counter[str] = Counter()
    for trace in traces:
        if trace.get("final_status") != "unscheduled":
            continue
        task = plan_tasks.get(trace.get("task_instance_id", ""))
        for goal in task.get("goal_tags", []) if task else []:
            unscheduled_by_goal[goal] += 1

    scheduled_by_goal: Counter[str] = Counter()
    substitutions_by_goal: Counter[str] = Counter()
    for row in calendar_rows:
        for goal in row.get("goal_tags", []):
            scheduled_by_goal[goal] += 1
            if row.get("substitution_status") == "substitution":
                substitutions_by_goal[goal] += 1

    goals = sorted(set(scheduled_by_goal) | set(unscheduled_by_goal))
    summary = [
        {
            "goal_tag": goal,
            "scheduled": scheduled_by_goal[goal],
            "unscheduled": unscheduled_by_goal[goal],
            "substitutions": substitutions_by_goal[goal],
            "status": goal_status(
                scheduled_by_goal[goal],
                unscheduled_by_goal[goal],
                substitutions_by_goal[goal],
            ),
        }
        for goal in goals
    ]
    return {"week": summary, "full_plan": summary}
```

Add to `build_calendar_interface` return:

```python
"goal_coverage": goal_coverage(calendar_rows, traces, personalized_plan),
"unscheduled_items": unscheduled_items(traces, rejection_summary, personalized_plan),
```

Add:

```python
def unscheduled_items(
    traces: list[dict[str, Any]],
    rejection_summary: dict[str, Any],
    personalized_plan: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    plan_tasks = tasks_by_id(personalized_plan)
    items = []
    for trace in traces:
        if trace.get("final_status") != "unscheduled":
            continue
        task = plan_tasks.get(trace.get("task_instance_id", ""))
        activity_id = trace.get("activity_id")
        summary = rejection_summary.get(activity_id, {})
        items.append(
            {
                "activity_id": activity_id,
                "task_instance_id": trace.get("task_instance_id"),
                "title": activity_id,
                "goal_tags": task.get("goal_tags", []) if task else [],
                "unscheduled_count": summary.get("unscheduled_count", 1),
                "rejected_candidate_count": summary.get("rejected_candidate_count", len(trace.get("rejected_candidates", []))),
                "reason_summary": trace.get("policy_fit_summary") or "No candidate slot passed policy and resource checks.",
                "trace_id": trace.get("trace_id"),
            }
        )
    return items
```

- [ ] **Step 4: Run tests**

Run:

```bash
pytest tests/test_calendar_interface.py -q
```

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add src/calendar_interface.py tests/test_calendar_interface.py
git commit -m "feat: summarize goal coverage and unscheduled work"
```

---

### Task 3: Add Location Bands And Travel Blocks

**Files:**
- Modify: `src/calendar_interface.py`
- Test: `tests/test_calendar_interface.py`

- [ ] **Step 1: Write failing location/travel test**

Append to `tests/test_calendar_interface.py`:

```python
def test_calendar_interface_exposes_location_bands_and_travel_blocks():
    availability = {
        "availability_blocks": [
            {
                "resource_type": "member_blocked",
                "start": "2026-06-01T08:30:00+08:00",
                "end": "2026-06-01T18:30:00+08:00",
                "location_id": "office",
                "notes": "Work block.",
            },
            {
                "resource_type": "member_travel",
                "start": "2026-06-03T09:30:00+08:00",
                "end": "2026-06-05T13:15:00+08:00",
                "location_id": "travel_hotel",
                "notes": "Hong Kong planned travel.",
            },
        ]
    }

    view_model = build_calendar_interface([], availability, [], {}, {"tasks": []}, {"providers": []})
    week = view_model["weeks"][0]

    assert week["location_bands"][0]["label"] == "Work block."
    assert week["location_bands"][1]["label"] == "Hong Kong planned travel."
    assert week["travel_blocks"][0]["location_id"] == "travel_hotel"
    assert week["travel_blocks"][0]["start_hour"] == 9.5
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_calendar_interface.py::test_calendar_interface_exposes_location_bands_and_travel_blocks -q
```

Expected: fail because location bands and travel blocks are missing.

- [ ] **Step 3: Implement location/travel mapping**

In `src/calendar_interface.py`, add:

```python
def context_blocks_by_week(availability: dict[str, Any]) -> dict[date, list[dict[str, Any]]]:
    by_week: dict[date, list[dict[str, Any]]] = defaultdict(list)
    for block in availability.get("availability_blocks", []):
        if block.get("resource_type") not in {"member_blocked", "member_travel"}:
            continue
        start = datetime.fromisoformat(block["start"])
        by_week[monday_start(start.date())].append(block)
    return by_week


def location_band(block: dict[str, Any], week_start: date) -> dict[str, Any]:
    start = datetime.fromisoformat(block["start"])
    end = datetime.fromisoformat(block["end"])
    return {
        "label": block.get("notes") or block.get("location_id") or "Location context",
        "location_id": block.get("location_id"),
        "resource_type": block.get("resource_type"),
        "start_day_index": max(0, (start.date() - week_start).days),
        "end_day_index": min(6, (end.date() - week_start).days),
    }


def travel_block(block: dict[str, Any], week_start: date) -> dict[str, Any]:
    start = datetime.fromisoformat(block["start"])
    end = datetime.fromisoformat(block["end"])
    return {
        "date": start.date().isoformat(),
        "day_index": (start.date() - week_start).days,
        "start_hour": round(start.hour + start.minute / 60, 2),
        "duration_hours": round((end - start).total_seconds() / 3600, 2),
        "label": block.get("notes") or "Travel",
        "location_id": block.get("location_id"),
    }
```

Use `context_blocks_by_week` when building weeks and include:

```python
"location_bands": [location_band(block, week_start) for block in context_blocks],
"travel_blocks": [
    travel_block(block, week_start)
    for block in context_blocks
    if block.get("resource_type") == "member_travel"
],
```

Make sure weeks are created from `rows_by_week`, `blocked_by_week`, and context block weeks.

- [ ] **Step 4: Run tests**

Run:

```bash
pytest tests/test_calendar_interface.py -q
```

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add src/calendar_interface.py tests/test_calendar_interface.py
git commit -m "feat: expose member location and travel context"
```

---

### Task 4: Render Review Panels And Weekly Filter Counts

**Files:**
- Modify: `src/static/calendar.js`
- Modify: `src/static/calendar.css`
- Test: `tests/test_app.py`

- [ ] **Step 1: Write failing static renderer test**

Append to `tests/test_app.py`:

```python
def test_calendar_renderer_has_review_debugging_sections():
    js_response = client.get("/static/calendar.js")
    css_response = client.get("/static/calendar.css")

    assert js_response.status_code == 200
    assert css_response.status_code == 200
    assert "renderGoalCoverage" in js_response.text
    assert "renderUnscheduledItems" in js_response.text
    assert "renderLocationBands" in js_response.text
    assert "weekScenarioCounts" in js_response.text
    assert "provider_summary" in js_response.text
    assert ".goal-panel" in css_response.text
    assert ".location-band" in css_response.text
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_app.py::test_calendar_renderer_has_review_debugging_sections -q
```

Expected: fail because renderer functions/classes are missing.

- [ ] **Step 3: Add selected-week scenario counts**

In `src/static/calendar.js`, add:

```javascript
function weekScenarioCounts(week) {
  const counts = {};
  for (const scenario of state.model.scenarios) counts[scenario] = 0;
  for (const activity of week.activities) {
    for (const flag of activity.scenario_flags || []) {
      counts[flag] = (counts[flag] || 0) + 1;
    }
  }
  return counts;
}
```

Update `renderScenarioChips()` to read:

```javascript
const week = state.model.weeks[state.weekIndex];
const counts = week ? weekScenarioCounts(week) : {};
```

and use `counts[scenario] || 0` for chip labels.

- [ ] **Step 4: Render review panels**

In `src/static/calendar.js`, add:

```javascript
function renderGoalCoverage() {
  const goals = state.model.goal_coverage?.week || [];
  if (!goals.length) return "";
  return `
    <section class="goal-panel">
      <h2>Goal Coverage</h2>
      <div class="goal-grid">
        ${goals.map((goal) => `
          <div class="goal-card status-${escapeHtml(goal.status)}">
            <strong>${escapeHtml(goal.goal_tag.replaceAll("_", " "))}</strong>
            <span>${goal.scheduled} scheduled · ${goal.unscheduled} unscheduled · ${goal.substitutions || 0} substitutions</span>
          </div>
        `).join("")}
      </div>
    </section>
  `;
}

function renderUnscheduledItems() {
  const items = state.model.unscheduled_items || [];
  if (!items.length) return "";
  return `
    <section class="risk-panel">
      <h2>Unscheduled / At Risk</h2>
      ${items.slice(0, 8).map((item) => `
        <div class="risk-item">
          <strong>${escapeHtml(item.title || item.activity_id)}</strong>
          <span>${escapeHtml((item.goal_tags || []).join(", "))}</span>
          <span>${escapeHtml(item.reason_summary || "No candidate slot passed.")}</span>
        </div>
      `).join("")}
    </section>
  `;
}

function renderLocationBands(week) {
  const bands = week.location_bands || [];
  if (!bands.length) return "";
  return `
    <div class="location-bands">
      ${bands.map((band) => `
        <div class="location-band" style="grid-column: ${band.start_day_index + 1} / ${band.end_day_index + 2}">
          ${escapeHtml(band.label)}
        </div>
      `).join("")}
    </div>
  `;
}
```

At the top of `render()`, before the agenda grid, render:

```javascript
grid.innerHTML = `
  ${renderGoalCoverage()}
  ${renderUnscheduledItems()}
  ${renderLocationBands(week)}
  <p class="filter-help">Counts reflect the selected week. Filtering only affects visible activities in this week.</p>
  <div class="agenda-grid">
    ${week.days.map((day, dayIndex) => renderAgendaDay(week, day, dayIndex)).join("")}
  </div>
`;
```

In `renderActivity`, add provider metadata:

```javascript
${activity.provider_summary ? `<div class="activity-provider">${escapeHtml(activity.provider_summary)}</div>` : ""}
```

- [ ] **Step 5: Add CSS**

In `src/static/calendar.css`, add:

```css
.filter-help { color: var(--muted); font-size: 13px; margin: 0 0 12px; }
.goal-panel, .risk-panel { padding: 14px; border-bottom: 1px solid var(--line); background: #fff; }
.goal-panel h2, .risk-panel h2 { margin: 0 0 10px; font-size: 16px; }
.goal-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 8px; }
.goal-card, .risk-item { display: grid; gap: 3px; border: 1px solid var(--line); border-radius: 6px; padding: 8px; background: #f8fafc; font-size: 12px; }
.status-on_track { border-left: 4px solid #059669; }
.status-at_risk { border-left: 4px solid #d97706; }
.status-missed { border-left: 4px solid #dc2626; }
.location-bands { display: grid; grid-template-columns: repeat(7, minmax(160px, 1fr)); gap: 4px; padding: 8px 10px; border-bottom: 1px solid var(--line); background: #f8fafc; }
.location-band { border: 1px solid #cbd5e1; background: #e0f2fe; color: #075985; border-radius: 6px; padding: 5px 8px; font-size: 12px; font-weight: 700; overflow-wrap: anywhere; }
.activity-provider { margin-top: 4px; font-size: 11px; opacity: .92; }
```

- [ ] **Step 6: Run tests**

Run:

```bash
pytest tests/test_app.py -q
```

Expected: pass.

- [ ] **Step 7: Commit**

```bash
git add src/static/calendar.js src/static/calendar.css tests/test_app.py
git commit -m "feat: render calendar review panels"
```

---

### Task 5: Add Data Quality Warnings For Food, Travel Times, And Raw Titles

**Files:**
- Modify: `src/calendar_interface.py`
- Modify: `src/static/calendar.js`
- Modify: `src/static/calendar.css`
- Test: `tests/test_calendar_interface.py`
- Test: `tests/test_app.py`

- [ ] **Step 1: Write failing data warning test**

Append to `tests/test_calendar_interface.py`:

```python
def test_calendar_interface_reports_data_generation_warnings():
    rows = [
        {
            "calendar_row_id": "row_task_1",
            "date": "2026-06-01",
            "start_time": "08:00",
            "end_time": "08:10",
            "title": "Morning supplement protocol",
            "activity_type": "food",
            "goal_tags": ["nutrition"],
            "load_level": "low",
            "location_id": "home",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": "trace_1",
        },
        {
            "calendar_row_id": "row_task_2",
            "date": "2026-06-01",
            "start_time": "12:00",
            "end_time": "12:30",
            "title": "No-prep fallback for high-protein prepared breakfast",
            "activity_type": "food",
            "goal_tags": ["nutrition"],
            "load_level": "low",
            "location_id": "home",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": "trace_2",
        },
    ]

    view_model = build_calendar_interface(
        rows,
        {"availability_blocks": [{"resource_type": "member_travel", "start": "2026-06-03T00:00:00+08:00", "end": "2026-06-04T23:59:00+08:00", "location_id": "travel_hotel", "notes": "Travel window."}]},
        [],
        {},
        {"tasks": []},
        {"providers": []},
    )

    warnings = " ".join(view_model["data_quality_warnings"])
    assert "Food plan has supplement/protocol rows but no explicit breakfast/lunch/dinner coverage" in warnings
    assert "Raw activity titles still contain fallback/substitution wording" in warnings
    assert "Travel windows should include exact travel leg times" in warnings
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_calendar_interface.py::test_calendar_interface_reports_data_generation_warnings -q
```

Expected: fail because data warnings are missing.

- [ ] **Step 3: Implement warnings**

Add to `src/calendar_interface.py`:

```python
def data_quality_warnings(
    calendar_rows: list[dict[str, Any]], availability: dict[str, Any]
) -> list[str]:
    warnings = []
    food_titles = [
        row.get("title", "").lower()
        for row in calendar_rows
        if row.get("activity_type") == "food"
    ]
    has_meal = any(
        meal in title
        for title in food_titles
        for meal in ["breakfast", "lunch", "dinner"]
    )
    has_protocol_food = any("supplement" in title or "protocol" in title for title in food_titles)
    if has_protocol_food and not has_meal:
        warnings.append(
            "Food plan has supplement/protocol rows but no explicit breakfast/lunch/dinner coverage."
        )

    raw_title_text = " ".join(row.get("title", "") for row in calendar_rows).lower()
    if "fallback" in raw_title_text or "substitution:" in raw_title_text:
        warnings.append("Raw activity titles still contain fallback/substitution wording.")

    for block in availability.get("availability_blocks", []):
        if block.get("resource_type") != "member_travel":
            continue
        start = datetime.fromisoformat(block["start"])
        end = datetime.fromisoformat(block["end"])
        if start.hour == 0 and start.minute == 0 and end.hour in {23, 0}:
            warnings.append("Travel windows should include exact travel leg times.")
            break
    return warnings
```

Add to `build_calendar_interface` return:

```python
"data_quality_warnings": data_quality_warnings(calendar_rows, availability),
```

- [ ] **Step 4: Render warnings in UI**

In `src/static/calendar.js`, add:

```javascript
function renderDataQualityWarnings() {
  const warnings = state.model.data_quality_warnings || [];
  if (!warnings.length) return "";
  return `
    <section class="warning-panel">
      <h2>Data Review Warnings</h2>
      <ul>${warnings.map((warning) => `<li>${escapeHtml(warning)}</li>`).join("")}</ul>
    </section>
  `;
}
```

Include `${renderDataQualityWarnings()}` above the goal coverage panel.

In `src/static/calendar.css`, add:

```css
.warning-panel { padding: 14px; border-bottom: 1px solid var(--line); background: #fffbeb; color: #78350f; }
.warning-panel h2 { margin: 0 0 8px; font-size: 16px; }
.warning-panel ul { margin: 0; padding-left: 18px; }
```

- [ ] **Step 5: Add static hook test**

Append to `tests/test_app.py`:

```python
def test_calendar_renderer_exposes_data_quality_warnings():
    js_response = client.get("/static/calendar.js")
    css_response = client.get("/static/calendar.css")

    assert "renderDataQualityWarnings" in js_response.text
    assert "data_quality_warnings" in js_response.text
    assert ".warning-panel" in css_response.text
```

- [ ] **Step 6: Run tests**

Run:

```bash
pytest tests/test_calendar_interface.py tests/test_app.py -q
```

Expected: pass.

- [ ] **Step 7: Commit**

```bash
git add src/calendar_interface.py src/static/calendar.js src/static/calendar.css tests/test_calendar_interface.py tests/test_app.py
git commit -m "feat: surface calendar data quality warnings"
```

---

### Task 6: Verify Full Calendar Review Flow

**Files:**
- No new files unless verification reveals defects.

- [ ] **Step 1: Run full test suite**

Run:

```bash
pytest
```

Expected: all tests pass.

- [ ] **Step 2: Restart local server**

Run:

```bash
uvicorn src.app:app --host 127.0.0.1 --port 8000
```

Expected: server starts at `http://127.0.0.1:8000`.

- [ ] **Step 3: Verify API shape**

Run:

```bash
curl -s http://127.0.0.1:8000/api/calendar/interface
```

Expected response includes:

```json
{
  "goal_coverage": {},
  "unscheduled_items": [],
  "data_quality_warnings": [],
  "weeks": [
    {
      "location_bands": [],
      "travel_blocks": []
    }
  ]
}
```

- [ ] **Step 4: Manual browser review**

Open:

```text
http://127.0.0.1:8000/calendar
```

Verify:

- Filter chip numbers change when switching weeks.
- Helper text says counts reflect the selected week.
- Goal coverage panel is visible.
- Unscheduled/at-risk panel is visible when unscheduled traces exist.
- Location bands appear under day headers.
- Travel blocks appear as unavailable context when exact travel blocks exist.
- Provider names appear on provider-led activity cards.
- Awkward raw titles are cleaned on cards but raw titles remain inspectable in trace/audit files.

- [ ] **Step 5: Commit verification fixes if any**

If changes were required:

```bash
git add src tests
git commit -m "fix: polish calendar review flow"
```

If no changes were required, do not create an empty commit.

---

## Self-Review

- Spec coverage: Covers weekly filter counts, goal coverage, unscheduled work, provider display, location bands, travel blocks, data warnings, and display-name cleanup.
- Placeholder scan: No placeholder markers.
- Type consistency: The plan consistently uses `personalized_plan`, `resource_universe`, `goal_coverage`, `unscheduled_items`, `location_bands`, `travel_blocks`, `provider_summary`, and `data_quality_warnings`.
- Scope note: This plan improves the app and surfaces data-generation defects. It does not regenerate activity data. A separate data-generation pass should revise `activity_families.json`, `availability.json`, and prompts after these warnings make gaps visible.
