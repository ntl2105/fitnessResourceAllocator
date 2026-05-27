# Member Profile Brief Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate and display a human-readable client profile brief from `member_profile.json`.

**Architecture:** Add a deterministic Markdown renderer that maps the profile JSON to a reviewer-friendly brief without inventing content. Wire the renderer into the demo-run build pipeline and expose the generated Markdown through the existing FastAPI app and audit file endpoint.

**Tech Stack:** Python, FastAPI, Jinja2 templates, pytest.

---

### Task 1: Renderer Test And Implementation

**Files:**
- Create: `tests/test_profile_brief.py`
- Create: `src/generation/profile_brief.py`

- [ ] Write a failing test that loads `data/member_profile.json`, renders Markdown, and asserts the brief includes the member name, narrative summary, goal priorities, constraints, baseline metrics, journey phases, travel windows, and scheduling implications.
- [ ] Run `pytest tests/test_profile_brief.py -q` and verify it fails because `src.generation.profile_brief` does not exist.
- [ ] Implement `build_member_profile_brief(profile: dict) -> str` and `write_member_profile_brief(profile_path, output_path) -> str`.
- [ ] Run `pytest tests/test_profile_brief.py -q` and verify it passes.

### Task 2: Pipeline And App Surface

**Files:**
- Modify: `scripts/build_demo_run.py`
- Modify: `src/app.py`
- Create: `src/templates/profile.html`
- Modify: `src/templates/calendar.html`
- Modify: `src/templates/summary.html`
- Modify: `src/templates/audit.html`
- Modify: `tests/test_app.py`

- [ ] Extend `tests/test_app.py` so `/profile` returns the brief, nav includes Profile, Audit lists `member_profile_brief.md`, and `/api/runs/latest/files/00_inputs/member_profile_brief.md` returns Markdown content.
- [ ] Run the focused app tests and verify they fail because the route/file are not wired yet.
- [ ] Update `scripts/build_demo_run.py` to write `data/runs/demo-run/00_inputs/member_profile_brief.md`.
- [ ] Add `member_profile_brief.md` to `STAGE_FILES["00_inputs"]`.
- [ ] Add the `/profile` route and `profile.html` template.
- [ ] Add Profile to the shared nav links in the existing templates.
- [ ] Regenerate the run with `python scripts/build_demo_run.py`.
- [ ] Run focused tests and the full test suite.
