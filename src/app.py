from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
import re
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.calendar_interface import build_calendar_interface, display_title
from src.generation.quality_report import build_quality_report
from src.generation.pipeline_story import build_pipeline_story
from src.generation.profile_brief import build_member_profile_brief
from src.io_utils import load_json


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RUN_DIR = DATA_DIR / "runs" / "demo-run"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent / "static"
# TEMPLATES_DIR = PROJECT_ROOT / "ui_redesign" / "templates"
# STATIC_DIR = PROJECT_ROOT / "ui_redesign" / "static"

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
        "member_profile_brief.md",
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
        "activity_board_model_review.md",
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

app = FastAPI(title="Resource Allocator")
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


def _plan_tasks_by_id() -> dict[str, dict[str, Any]]:
    plan = load_json(RUN_DIR / "03_scheduling" / "personalized_plan.json")
    return {task["task_id"]: task for task in plan.get("tasks", []) if task.get("task_id")}


def _activities_by_id() -> dict[str, dict[str, Any]]:
    action_plan = _load_run_json_or_root("action_plan.json")
    return {
        activity["activity_id"]: activity
        for activity in action_plan.get("activities", [])
        if activity.get("activity_id")
    }


def _weekly_goal_actions_by_id() -> dict[str, dict[str, Any]]:
    profile = _load_run_json_or_root("member_profile.json")
    return {
        action["weekly_goal_action_id"]: action
        for action in profile.get("weekly_goal_actions", [])
        if action.get("weekly_goal_action_id")
    }


def _trace_activity_title(
    trace: dict[str, Any], rows_by_task_id: dict[str, dict[str, Any]]
) -> str:
    row = rows_by_task_id.get(trace.get("task_instance_id"))
    if row:
        return display_title(row.get("title", trace.get("activity_id", "Activity")))
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
    plan_tasks = _plan_tasks_by_id()
    activities = _activities_by_id()
    weekly_actions = _weekly_goal_actions_by_id()
    payload = deepcopy(trace)
    payload["activity_title"] = _trace_activity_title(trace, rows_by_task_id)
    activity = activities.get(trace.get("activity_id", ""), {})
    task = plan_tasks.get(trace.get("task_instance_id", ""), {})
    goal_explanation = _goal_explanation(trace, activity, rows_by_task_id, plan_tasks, activities, weekly_actions)
    payload["goal_explanation"] = goal_explanation
    payload["planning_rationale"] = _planning_rationale(activity, goal_explanation, activities)

    selected_slot = trace.get("selected_slot")
    if selected_slot:
        payload["selected_slot_summary"] = (
            "Scheduled for "
            f"{_slot_summary(selected_slot['start'], selected_slot['end'], selected_slot.get('location_id'))} "
            f"because {_selected_slot_reason(trace, activity, task, goal_explanation)}"
        )
    else:
        payload["selected_slot_summary"] = _unscheduled_summary(trace, activity, goal_explanation)
    payload["why_scheduled"] = _why_scheduled(trace, activity, task, goal_explanation)
    payload["why_not_scheduled"] = _why_not_scheduled(trace, activity, goal_explanation)

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


def _planning_rationale(
    activity: dict[str, Any],
    goal_explanation: dict[str, Any] | None,
    activities: dict[str, dict[str, Any]],
) -> list[str]:
    if not activity:
        return ["No activity metadata was found for this trace."]

    rationale = []
    family_id = activity.get("activity_family_id")
    if activity.get("is_primary") is False:
        primary = _primary_family_activity(activity, activities)
        primary_text = (
            f" It replaces primary activity {primary.get('title', primary.get('activity_id'))}."
            if primary
            else ""
        )
        rationale.append(
            "Activity role: substitution in activity family "
            f"{family_id or 'unknown'}.{primary_text}"
        )
    else:
        sibling_substitutions = _family_substitutions(activity, activities)
        substitution_text = (
            f" {len(sibling_substitutions)} substitution option(s) exist if this primary cannot be placed."
            if sibling_substitutions
            else " No substitution option is defined for this family."
        )
        rationale.append(
            "Activity role: primary activity in family "
            f"{family_id or 'unknown'}.{substitution_text}"
        )

    if goal_explanation:
        target = goal_explanation.get("target_per_week")
        target_text = f" Target: {target} per week." if target is not None else ""
        rationale.append(
            f"Goal mapping: contributes to {goal_explanation['label']}.{target_text}"
        )
    else:
        rationale.append(
            "Goal mapping: support/context activity or no counted weekly goal action."
        )

    frequency = activity.get("frequency", {})
    frequency_bits = []
    if frequency.get("type"):
        frequency_bits.append(str(frequency["type"]))
    if frequency.get("count") is not None:
        frequency_bits.append(f"count {frequency['count']}")
    if frequency.get("preferred_days"):
        frequency_bits.append(f"days {', '.join(frequency['preferred_days'])}")
    if frequency.get("preferred_time_windows"):
        frequency_bits.append(f"windows {', '.join(frequency['preferred_time_windows'])}")
    if frequency_bits:
        rationale.append("Generated cadence: " + "; ".join(frequency_bits) + ".")

    if activity.get("journey_phase_applicability"):
        rationale.append(
            "Journey fit: generated for phase(s) "
            f"{', '.join(activity['journey_phase_applicability'])}."
        )

    substitution = _substitution_explanation({}, activity)
    if substitution:
        rationale.append(f"Substitution logic: {substitution}.")

    return rationale


def _primary_family_activity(
    activity: dict[str, Any],
    activities: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    family_id = activity.get("activity_family_id")
    if not family_id:
        return None
    explicit_primary_id = activity.get("substitution_for_activity_id")
    if explicit_primary_id and explicit_primary_id in activities:
        return activities[explicit_primary_id]
    for candidate in activities.values():
        if candidate.get("activity_family_id") == family_id and candidate.get("is_primary"):
            return candidate
    return None


def _family_substitutions(
    activity: dict[str, Any],
    activities: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    family_id = activity.get("activity_family_id")
    if not family_id:
        return []
    return [
        candidate
        for candidate in activities.values()
        if candidate.get("activity_family_id") == family_id
        and candidate.get("is_primary") is False
    ]


def _goal_explanation(
    trace: dict[str, Any],
    activity: dict[str, Any],
    rows_by_task_id: dict[str, dict[str, Any]],
    plan_tasks: dict[str, dict[str, Any]],
    activities: dict[str, dict[str, Any]],
    weekly_actions: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    selected_slot = trace.get("selected_slot")
    contributions = [
        contribution
        for contribution in _effective_goal_contributions(activity, activities)
        if _contribution_action_id(contribution)
        and contribution.get("counts_toward_weekly_target") is not False
    ]
    if not contributions:
        return None
    contribution = contributions[0]
    action_id = _contribution_action_id(contribution)
    action = weekly_actions.get(action_id, {})
    target = action.get("target_per_week")
    week_count = None
    if selected_slot:
        selected_date = datetime.fromisoformat(selected_slot["start"]).date()
        week_start = selected_date - timedelta(days=selected_date.weekday())
        week_end = week_start + timedelta(days=7)
        week_count = 0
        for task_id, row in rows_by_task_id.items():
            row_date = datetime.fromisoformat(row["date"]).date()
            if not (week_start <= row_date < week_end):
                continue
            scheduled_task = plan_tasks.get(task_id, {})
            scheduled_activity = activities.get(scheduled_task.get("activity_id", ""), {})
            if any(
                item.get("weekly_goal_action_id") == action_id
                and item.get("counts_toward_weekly_target") is not False
                for item in scheduled_activity.get("goal_contributions", [])
            ):
                week_count += 1
    return {
        "weekly_goal_action_id": action_id,
        "label": action.get("label", action_id),
        "target_per_week": target,
        "week_count": week_count,
        "role": contribution.get("role"),
        "notes": contribution.get("notes"),
    }


def _contribution_action_id(contribution: dict[str, Any]) -> str | None:
    return contribution.get("weekly_goal_action_id") or contribution.get("goal_action_id")


def _effective_goal_contributions(
    activity: dict[str, Any],
    activities: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    contributions = activity.get("goal_contributions", [])
    if contributions:
        return contributions
    if activity.get("is_primary") is False:
        primary = _primary_family_activity(activity, activities)
        if primary:
            return primary.get("goal_contributions", [])
    return []


def _selected_slot_reason(
    trace: dict[str, Any],
    activity: dict[str, Any],
    task: dict[str, Any],
    goal_explanation: dict[str, Any] | None,
) -> str:
    reasons = []
    if goal_explanation:
        count = goal_explanation.get("week_count")
        target = goal_explanation.get("target_per_week")
        if count is not None and target:
            reasons.append(
                f"it supports {goal_explanation['label']} with weekly coverage at {count} of {target}"
            )
        else:
            reasons.append(f"it supports {goal_explanation['label']}")
    substitution = _substitution_explanation(trace, activity)
    if substitution:
        reasons.append(substitution)
    if activity.get("frequency", {}).get("preferred_time_windows"):
        reasons.append("the time is inside the activity's preferred window")
    if task.get("provider_ids"):
        reasons.append("the required provider was available")
    if task.get("equipment_ids"):
        reasons.append("the required equipment was available")
    facilitator = str(activity.get("facilitator_type") or "").lower()
    if not task.get("provider_ids") and facilitator in {"self", "member"}:
        reasons.append(f"{facilitator}-led; no provider required")
    location = (trace.get("selected_slot") or {}).get("location_id")
    if location:
        reasons.append(f"{_display_token(location)} was an allowed location")
    return ", ".join(reasons) + "."


def _display_token(value: Any) -> str:
    return str(value).replace("_", " ")


def _why_scheduled(
    trace: dict[str, Any],
    activity: dict[str, Any],
    task: dict[str, Any],
    goal_explanation: dict[str, Any] | None,
) -> list[str]:
    if trace.get("final_status") != "scheduled":
        return []
    reasons = []
    if goal_explanation:
        count = goal_explanation.get("week_count")
        target = goal_explanation.get("target_per_week")
        if count is not None and target:
            reasons.append(
                f"Goal fit: supports {goal_explanation['label']}; related scheduled coverage is {count} of {target} this week."
            )
        else:
            reasons.append(f"Goal fit: supports {goal_explanation['label']}.")
    else:
        reasons.append("Goal fit: support activity or no counted weekly goal contribution.")
    substitution = _substitution_explanation(trace, activity)
    if substitution:
        reasons.append(f"Adaptation fit: {substitution}.")
    if activity.get("frequency", {}).get("preferred_time_windows"):
        reasons.append(
            "Time fit: selected slot is within the generated preferred time window."
        )
    selected_slot = trace.get("selected_slot") or {}
    if selected_slot.get("location_id"):
        reasons.append(f"Location fit: {selected_slot['location_id']} is allowed for this activity.")
    if task.get("provider_ids"):
        reasons.append(f"Provider fit: {', '.join(task['provider_ids'])} covered the slot.")
    if task.get("equipment_ids"):
        reasons.append(f"Equipment fit: {', '.join(task['equipment_ids'])} covered the slot.")
    if trace.get("rejected_candidates"):
        reasons.append(
            f"Earlier attempts: {len(trace['rejected_candidates'])} candidate slots were rejected before this one."
        )
    return reasons


def _substitution_explanation(trace: dict[str, Any], activity: dict[str, Any]) -> str | None:
    stored_reason = trace.get("substitution_reason")
    if stored_reason:
        return str(stored_reason).rstrip(".")
    if activity.get("is_primary") is not False:
        return None

    codes = activity.get("substitution_reason_codes") or []
    if isinstance(codes, str):
        codes = [codes]
    readable_codes = [
        str(code).replace("_", " ")
        for code in codes
        if str(code).strip()
    ]
    notes = activity.get("substitution_notes") or activity.get("substitution_reason")
    primary_id = activity.get("substitution_for_activity_id")

    parts = []
    if primary_id:
        parts.append(f"replaces {primary_id}")
    if readable_codes:
        parts.append(f"reason: {', '.join(readable_codes)}")
    if notes:
        parts.append(str(notes))
    if parts:
        return "; ".join(parts)
    return "substitution in the same activity family"


def _unscheduled_summary(
    trace: dict[str, Any],
    activity: dict[str, Any],
    goal_explanation: dict[str, Any] | None,
) -> str:
    if trace.get("final_status") == "skipped":
        return trace.get("policy_fit_summary") or "Skipped because the primary option was already scheduled."
    reasons = [
        reason
        for candidate in trace.get("rejected_candidates", [])
        for reason in candidate.get("reasons", [])
    ]
    if not reasons:
        return "No selected slot."
    goal_text = (
        f" for {goal_explanation['label']}" if goal_explanation else ""
    )
    return f"Could not schedule{goal_text} because {reasons[0]}"


def _why_not_scheduled(
    trace: dict[str, Any],
    activity: dict[str, Any],
    goal_explanation: dict[str, Any] | None,
) -> list[str]:
    if trace.get("final_status") == "scheduled":
        return []
    reasons = []
    if goal_explanation:
        reasons.append(f"Goal affected: {goal_explanation['label']}.")
    if trace.get("policy_fit_summary"):
        reasons.append(trace["policy_fit_summary"])
    first_rejections = [
        reason
        for candidate in trace.get("rejected_candidates", [])[:3]
        for reason in candidate.get("reasons", [])[:2]
    ]
    reasons.extend(first_rejections)
    return reasons


def _read_text(stage_id: str, filename: str) -> str:
    return _run_path(stage_id, filename).read_text(encoding="utf-8")


def _load_run_json_or_root(filename: str) -> Any:
    run_file = RUN_DIR / "00_inputs" / filename
    if run_file.is_file():
        return load_json(run_file)
    return load_json(_data_path(filename))


def _profile_brief_text() -> str:
    brief_path = RUN_DIR / "00_inputs" / "member_profile_brief.md"
    if brief_path.is_file():
        return brief_path.read_text(encoding="utf-8")
    return build_member_profile_brief(_load_run_json_or_root("member_profile.json"))


def _quality_report_text() -> str:
    quality_path = RUN_DIR / "00_inputs" / "synthetic_data_quality_report.md"
    if quality_path.is_file():
        return quality_path.read_text(encoding="utf-8")
    validation_path = RUN_DIR / "01_validation" / "validation_report.json"
    if validation_path.is_file():
        return build_quality_report(load_json(validation_path))
    return "# Synthetic Data Quality Report\n\nStatus: not available\n"


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


@app.get("/api/pipeline/story")
def api_pipeline_story() -> Any:
    return build_pipeline_story(DATA_DIR)


@app.get("/api/plan")
def api_plan() -> Any:
    return load_json(RUN_DIR / "03_scheduling" / "personalized_plan.json")


@app.get("/api/calendar/interface")
def api_calendar_interface() -> Any:
    calendar_rows = load_json(RUN_DIR / "04_calendar" / "calendar_rows.json")
    availability = _load_run_json_or_root("availability.json")
    traces = load_json(RUN_DIR / "03_scheduling" / "decision_traces.json")
    rejection_summary = load_json(RUN_DIR / "03_scheduling" / "rejection_summary.json")
    personalized_plan = load_json(RUN_DIR / "03_scheduling" / "personalized_plan.json")
    resource_universe = _load_run_json_or_root("resource_universe.json")
    action_plan = _load_run_json_or_root("action_plan.json")
    member_profile = _load_run_json_or_root("member_profile.json")
    constraint_audit = load_json(RUN_DIR / "04_calendar" / "constraint_violations.json")
    interface = build_calendar_interface(
        calendar_rows,
        availability,
        traces,
        rejection_summary,
        personalized_plan,
        resource_universe,
        action_plan,
        member_profile,
    )
    interface["constraint_audit"] = constraint_audit
    return interface


@app.get("/api/traces/{trace_id}")
def api_trace(trace_id: str) -> dict[str, Any]:
    return _enriched_trace(_load_trace(trace_id))


@app.get("/calendar")
def calendar(request: Request):
    rows = load_json(RUN_DIR / "04_calendar" / "calendar_rows.json")
    profile_brief = _profile_brief_text()
    return templates.TemplateResponse(
        request,
        "calendar.html",
        {
            "request": request,
            "rows": rows,
            "row_count": len(rows),
            "profile_brief": profile_brief,
        },
    )


@app.get("/summary")
def summary(request: Request):
    rows = load_json(RUN_DIR / "04_calendar" / "calendar_rows.json")
    quality_report = _quality_report_text()
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


@app.get("/profile")
def profile(request: Request):
    profile_brief = _profile_brief_text()
    member = _load_run_json_or_root("member_profile.json")
    return templates.TemplateResponse(
        request,
        "profile.html",
        {
            "request": request,
            "profile_brief": profile_brief,
            "member_name": member.get("name", "Member"),
        },
    )


@app.get("/pipeline")
def pipeline(request: Request):
    story = build_pipeline_story(DATA_DIR)
    return templates.TemplateResponse(
        request,
        "pipeline.html",
        {
            "request": request,
            "story": story,
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
    if stage_id == "00_inputs" and filename == "member_profile_brief.md":
        return JSONResponse(content={"content": _profile_brief_text()})
    if stage_id == "00_inputs" and filename == "synthetic_data_quality_report.md":
        return JSONResponse(content={"content": _quality_report_text()})
    if stage_id == "00_inputs":
        root_candidate = _data_path(filename)
        if not (RUN_DIR / stage_id / filename).is_file() and root_candidate.is_file():
            if root_candidate.suffix == ".json":
                return JSONResponse(content=load_json(root_candidate))
            if root_candidate.suffix in {".md", ".txt"}:
                return JSONResponse(
                    content={"content": root_candidate.read_text(encoding="utf-8")}
                )

    path = _run_path(stage_id, filename)
    if path.suffix == ".json":
        return JSONResponse(content=load_json(path))
    if path.suffix in {".md", ".txt"}:
        return JSONResponse(content={"content": path.read_text(encoding="utf-8")})
    raise HTTPException(status_code=404, detail="Unsupported file type")
