# Resource Allocator

Synthetic resource-allocation demo for an Elyx-style healthspan member journey. The project turns member goals, providers, locations, availability, and activity families into a 3-month scheduled calendar with decision traces.

## What It Does

- Builds an activity board from generated activity families.
- Expands activities into dated task instances.
- Schedules meals, medications, fitness, recovery, labs, and consultations against member/provider/equipment/location availability.
- Applies policy checks for travel, WFH days, meal coverage, substitutions, workout timing, provider spacing, transition buffers, and weekly goal validation.
- Runs a final hard-constraint audit for member blocks, exact travel windows, WFH office bans, provider/location fit, arrival fatigue, and location transitions.
- Serves a local UI with profile, activity board, calendar, recap, goal validation, constraint audit, and decision traces.

## Project Layout

- `data/` - canonical input data used by the demo.
- `src/` - FastAPI app, scheduler, generation helpers, models, templates, and static UI.
- `scripts/` - commands for flattening, validating, regenerating, and scheduling the demo run.
- `tests/` - unit and scenario tests.
- `prompts/` - prompt/source material used to generate the synthetic dataset.
- `docs/` - implementation notes, specs, and plans.

Generated activity-family batches are intentionally ignored:

- `data/generated/`

The deployable demo data under `data/runs/demo-run/` should be committed because the Vercel app is read-only and serves those JSON/Markdown artifacts at runtime.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Rebuild The Demo Run

```bash
python scripts/build_demo_run.py
```

The staged generation process is documented in [docs/assignment_dataset_generation.md](docs/assignment_dataset_generation.md).
Scheduler behavior and known design debt are documented in [docs/scheduler_implementation_note.md](docs/scheduler_implementation_note.md).

This runs:

1. `scripts/flatten_action_plan.py`
2. `scripts/validate_data.py`
3. `scripts/run_scheduler.py`
4. `src/calendar_view.py`

Outputs are written under `data/runs/demo-run/`.

The final calendar stage includes:

- `calendar_rows.json` - scheduled calendar rows used by the app.
- `decision_traces.json` - acceptance/rejection trace data behind calendar explanations.
- `constraint_violations.json` - final hard-constraint audit consumed by the recap page.

## Run Locally

```bash
python -m uvicorn src.app:app --host 127.0.0.1 --port 8000
```

Open:

- Calendar: `http://127.0.0.1:8000/calendar`
- Profile: `http://127.0.0.1:8000/profile`
- Summary: `http://127.0.0.1:8000/summary`

## Deploy To Vercel

The deployed app needs the committed `data/` directory, including `data/runs/demo-run/`.

Before deploying:

```bash
python scripts/build_demo_run.py
pytest -q
```

Then deploy:

```bash
vercel deploy
```

For production:

```bash
vercel deploy --prod
```

The `.vercelignore` file excludes local/dev-only material such as tests, docs, prompts, source assignment files, and generated intermediate batches while keeping runtime `data/` artifacts.

## Test

```bash
pytest -q
```

Current expected result after the latest scheduler updates:

```text
163 passed
```

## Key Scheduler Policies

- Every day gets breakfast, lunch, and dinner unless explicitly skipped for a valid reason such as fasted metabolic testing.
- Member location follows office/home/travel state. WFH days hard-ban office rows, and travel hotel rows apply only inside exact travel windows.
- Medium/high-load fitness must end by `20:30` unless explicitly allowed.
- Fitness cannot stack multiple substantial sessions on the same day.
- Arrival-fatigue windows allow only low-load recovery, mobility, or breathing work unless explicitly overridden.
- Provider-facilitated rows must match provider availability, location, and remote/in-person mode.
- Location transitions require realistic buffers between consecutive rows.
- Travel substitutions prefer higher-resource options when available, such as Tokyo hotel-gym strength before in-room bands/bodyweight.
- Weekly validation reports structured meals, member-assembled meal cap, estimated chef prep sessions, aerobic sessions, strength sessions, and recovery actions.

## Final Calendar Audit

`src/calendar_view.py` writes `data/runs/demo-run/04_calendar/constraint_violations.json` during the demo build. The current generated demo run has:

- Status: `pass`
- Violations: `0`

## Notes

The scheduler is intentionally explainable rather than fully optimized. The decision traces show why each selected slot was accepted and why earlier candidates were rejected.
