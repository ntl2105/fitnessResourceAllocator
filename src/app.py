from copy import deepcopy
from datetime import datetime
from pathlib import Path
import re
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.calendar_interface import build_calendar_interface
from src.io_utils import load_json


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RUN_DIR = DATA_DIR / "runs" / "demo-run"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent / "static"

KNOWN_STAGES = [
    "00_inputs",
    "01_validation",
    "02_task_expansion",
    "03_scheduling",
    "04_calendar",
]

STAGE_FILES = {
    "00_inputs": [
        "member_profile.json",
        "action_plan.json",
        "availability.json",
        "activity_families.json",
        "resource_universe.json",
        "known_frictions.json",
        "synthetic_data_quality_report.md",
    ],
    "01_validation": [
        "validation_report.json",
        "activity_board_review.md",
    ],
    "02_task_expansion": [
        "task_instances.json",
        "expansion_report.md",
    ],
    "03_scheduling": [
        "personalized_plan.json",
        "decision_traces.json",
        "rejection_summary.json",
    ],
    "04_calendar": [
        "calendar_rows.json",
        "summary_report.md",
    ],
}

app = FastAPI(title="Elyx Resource Allocator")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _data_path(filename: str) -> Path:
    return DATA_DIR / filename


def _run_path(stage_id: str, filename: str) -> Path:
    if stage_id not in KNOWN_STAGES:
        raise HTTPException(status_code=404, detail="Unknown run stage")

    stage_dir = (RUN_DIR / stage_id).resolve()
    candidate = (stage_dir / filename).resolve()
    try:
        candidate.relative_to(stage_dir)
        candidate.relative_to(RUN_DIR.resolve())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="File not found") from exc

    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return candidate


def _load_trace(trace_id: str) -> dict[str, Any]:
    traces = load_json(RUN_DIR / "03_scheduling" / "decision_traces.json")
    for trace in traces:
        if trace.get("trace_id") == trace_id:
            return trace
    raise HTTPException(status_code=404, detail="Trace not found")


def _task_id_from_calendar_row(row: dict[str, Any]) -> str | None:
    row_id = row.get("calendar_row_id", "")
    if row_id.startswith("row_"):
        return row_id.removeprefix("row_")
    return None


def _calendar_rows_by_task_id() -> dict[str, dict[str, Any]]:
    rows = load_json(RUN_DIR / "04_calendar" / "calendar_rows.json")
    return {
        task_id: row
        for row in rows
        if (task_id := _task_id_from_calendar_row(row)) is not None
    }


def _trace_activity_title(
    trace: dict[str, Any], rows_by_task_id: dict[str, dict[str, Any]]
) -> str:
    row = rows_by_task_id.get(trace.get("task_instance_id"))
    if row:
        return row.get("title", trace.get("activity_id", "Activity"))
    return trace.get("activity_id", "Activity")


def _slot_summary(start: str, end: str, location_id: str | None) -> str:
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)
    day = f"{start_dt.strftime('%a %b')} {start_dt.day}"
    time_range = f"{start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}"
    location = location_id or "unspecified location"
    return f"{day}, {time_range} at {location}"


def _human_reasons(
    reasons: list[str], rows_by_task_id: dict[str, dict[str, Any]]
) -> list[str]:
    resolved = []
    has_overlap_resolution = False
    for reason in reasons:
        overlap = re.fullmatch(r"Overlaps ([^.]+)\.", reason)
        if overlap:
            task_id = overlap.group(1)
            row = rows_by_task_id.get(task_id)
            if row:
                resolved.append(
                    "Rejected because it overlaps "
                    f"{row['title']}, {row['start_time']}-{row['end_time']} "
                    f"at {row.get('location_id') or row.get('mode')}."
                )
                has_overlap_resolution = True
            else:
                resolved.append(f"Rejected because it overlaps {task_id}.")
            continue

        nearby = re.fullmatch(r"Nearby task at incompatible location ([^.]+)\.", reason)
        if nearby and has_overlap_resolution:
            continue
        if nearby:
            resolved.append(
                "Rejected because another nearby scheduled activity is at "
                f"{nearby.group(1)}, and this candidate needs a different location."
            )
            continue

        resolved.append(reason)
    return resolved


def _enriched_trace(trace: dict[str, Any]) -> dict[str, Any]:
    rows_by_task_id = _calendar_rows_by_task_id()
    payload = deepcopy(trace)
    payload["activity_title"] = _trace_activity_title(trace, rows_by_task_id)

    selected_slot = trace.get("selected_slot")
    if selected_slot:
        payload["selected_slot_summary"] = (
            "Scheduled for "
            f"{_slot_summary(selected_slot['start'], selected_slot['end'], selected_slot.get('location_id'))} "
            "because all selected-slot policy and resource checks passed."
        )
    else:
        payload["selected_slot_summary"] = "No selected slot."

    payload["rejected_candidate_summaries"] = [
        {
            "slot_summary": _slot_summary(
                candidate["start"], candidate["end"], candidate.get("location_id")
            ),
            "human_reasons": _human_reasons(candidate.get("reasons", []), rows_by_task_id),
            "raw_reasons": candidate.get("reasons", []),
        }
        for candidate in trace.get("rejected_candidates", [])
    ]
    return payload


def _read_text(stage_id: str, filename: str) -> str:
    return _run_path(stage_id, filename).read_text(encoding="utf-8")


@app.get("/", include_in_schema=False)
def index() -> RedirectResponse:
    return RedirectResponse(url="/calendar")


@app.get("/api/member")
def api_member() -> Any:
    return load_json(_data_path("member_profile.json"))


@app.get("/api/action-plan")
def api_action_plan() -> Any:
    return load_json(_data_path("action_plan.json"))


@app.get("/api/availability")
def api_availability() -> Any:
    return load_json(_data_path("availability.json"))


@app.get("/api/plan")
def api_plan() -> Any:
    return load_json(RUN_DIR / "03_scheduling" / "personalized_plan.json")


@app.get("/api/calendar/interface")
def api_calendar_interface() -> Any:
    calendar_rows = load_json(RUN_DIR / "04_calendar" / "calendar_rows.json")
    availability = load_json(RUN_DIR / "00_inputs" / "availability.json")
    traces = load_json(RUN_DIR / "03_scheduling" / "decision_traces.json")
    rejection_summary = load_json(RUN_DIR / "03_scheduling" / "rejection_summary.json")
    return build_calendar_interface(
        calendar_rows,
        availability,
        traces,
        rejection_summary,
    )


@app.get("/api/traces/{trace_id}")
def api_trace(trace_id: str) -> dict[str, Any]:
    return _enriched_trace(_load_trace(trace_id))


@app.get("/calendar")
def calendar(request: Request):
    rows = load_json(RUN_DIR / "04_calendar" / "calendar_rows.json")
    return templates.TemplateResponse(
        request,
        "calendar.html",
        {"request": request, "rows": rows, "row_count": len(rows)},
    )


@app.get("/summary")
def summary(request: Request):
    rows = load_json(RUN_DIR / "04_calendar" / "calendar_rows.json")
    quality_report = _read_text("00_inputs", "synthetic_data_quality_report.md")
    calendar_summary = _read_text("04_calendar", "summary_report.md")
    return templates.TemplateResponse(
        request,
        "summary.html",
        {
            "request": request,
            "quality_report": quality_report,
            "calendar_summary": calendar_summary,
            "row_count": len(rows),
        },
    )


@app.get("/audit")
def audit(request: Request):
    stages = [
        {
            "stage_id": stage_id,
            "files": [
                {"name": filename, "url": f"/api/runs/latest/files/{stage_id}/{filename}"}
                for filename in STAGE_FILES[stage_id]
            ],
        }
        for stage_id in KNOWN_STAGES
    ]
    return templates.TemplateResponse(
        request,
        "audit.html",
        {"request": request, "stages": stages},
    )


@app.get("/api/runs/latest/files/{stage_id}/{filename:path}")
def api_run_file(stage_id: str, filename: str) -> JSONResponse:
    path = _run_path(stage_id, filename)
    if path.suffix == ".json":
        return JSONResponse(content=load_json(path))
    if path.suffix in {".md", ".txt"}:
        return JSONResponse(content={"content": path.read_text(encoding="utf-8")})
    raise HTTPException(status_code=404, detail="Unsupported file type")
