from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.io_utils import load_json


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RUN_DIR = DATA_DIR / "runs" / "demo-run"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

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


@app.get("/api/traces/{trace_id}")
def api_trace(trace_id: str) -> dict[str, Any]:
    return _load_trace(trace_id)


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
