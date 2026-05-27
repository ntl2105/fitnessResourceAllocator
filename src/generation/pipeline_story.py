from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
from typing import Any

from src.io_utils import load_json


StageCard = dict[str, Any]


def _load_optional_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return load_json(path)


def _plural(count: int, singular: str, plural: str | None = None) -> str:
    label = singular if count == 1 else plural or f"{singular}s"
    return f"{count} {label}"


def _goal_action_summary(member: dict[str, Any]) -> list[str]:
    actions = member.get("goal_actions", []) or member.get("weekly_goal_actions", [])
    summaries = []
    for action in actions:
        target_payload = action.get("target") or {}
        target = target_payload.get("units", action.get("target_per_week"))
        period = target_payload.get("period", "week")
        role = action.get("role", "goal action")
        label = action.get("label") or action.get("goal_action_id") or action.get("weekly_goal_action_id")
        if target is None:
            summaries.append(f"{label}: {role}")
        else:
            summaries.append(f"{label}: {target}/{period}, {role}")
    return summaries


def _primary_goal_names(member: dict[str, Any], limit: int = 3) -> list[str]:
    goals = sorted(
        member.get("goals", []),
        key=lambda goal: goal.get("priority", 999),
    )
    return [goal.get("name") or goal.get("goal_id", "Unnamed goal") for goal in goals[:limit]]


def _physical_constraint_names(member: dict[str, Any]) -> list[str]:
    constraints = member.get("constraints", {})
    return [
        constraint.get("name", "physical constraint")
        for constraint in constraints.get("physical", [])
    ]


def _provider_role_counts(resources: dict[str, Any]) -> Counter[str]:
    return Counter(
        provider.get("provider_type", "unknown")
        for provider in resources.get("providers", [])
    )


def _availability_counts(availability: dict[str, Any]) -> Counter[str]:
    return Counter(
        block.get("resource_type", "unknown")
        for block in availability.get("availability_blocks", [])
    )


def _batch_rank(path: Path) -> tuple[str, int, str]:
    stem = path.stem
    batch_match = re.match(r"^(batch_\d+)", stem)
    batch_key = batch_match.group(1) if batch_match else stem

    rank = 10
    if "_regenerated_" in stem:
        regenerated_match = re.search(r"_regenerated_(\d+)_", stem)
        rank = 30 + int(regenerated_match.group(1)) if regenerated_match else 30
    if stem.endswith("_candidate"):
        rank += 2
    if stem.endswith("_repaired"):
        rank += 5
    return batch_key, rank, stem


def _selected_stage5_batch_paths(data_dir: Path) -> list[Path]:
    batch_dir = data_dir / "generated" / "stage05_activity_families" / "batches"
    if not batch_dir.is_dir():
        return []

    selected: dict[str, tuple[int, str, Path]] = {}
    for path in sorted(batch_dir.glob("*.json")):
        batch_key, rank, stem = _batch_rank(path)
        current = selected.get(batch_key)
        if current is None or (rank, stem) > (current[0], current[1]):
            selected[batch_key] = (rank, stem, path)
    return [entry[2] for entry in sorted(selected.values(), key=lambda entry: entry[2].name)]


def _load_stage5_families(data_dir: Path) -> tuple[list[dict[str, Any]], list[str]]:
    families: list[dict[str, Any]] = []
    source_files = []
    for path in _selected_stage5_batch_paths(data_dir):
        payload = _load_optional_json(path, {})
        batch_families = payload.get("activity_families", [])
        if isinstance(batch_families, list):
            families.extend(batch_families)
            source_files.append("data/generated/stage05_activity_families/batches")
    source_files = sorted(set(source_files))
    return families, source_files


def _activity_family_activities(
    families: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    activities = []
    for family in families:
        primary = family.get("primary_activity")
        if isinstance(primary, dict):
            activities.append(primary)
        substitutions = family.get("substitution_activities", [])
        if isinstance(substitutions, list):
            activities.extend(
                substitution
                for substitution in substitutions
                if isinstance(substitution, dict)
            )
    return activities


def _stage_card(
    stage_id: str,
    title: str,
    status: str,
    generated: list[str],
    meaning_for_member: list[str],
    validation_focus: list[str],
    source_files: list[str],
) -> StageCard:
    return {
        "stage_id": stage_id,
        "title": title,
        "status": status,
        "generated": generated,
        "meaning_for_member": meaning_for_member,
        "validation_focus": validation_focus,
        "source_files": source_files,
    }


def _member_stage(member: dict[str, Any]) -> StageCard:
    member_name = member.get("name", "the member")
    goal_names = _primary_goal_names(member)
    constraints = _physical_constraint_names(member)
    goal_actions = _goal_action_summary(member)
    travel_windows = member.get("travel_windows", [])
    phases = member.get("journey_phases", [])
    exercise = member.get("preferences", {}).get("exercise_timing", {})
    preferred_times = ", ".join(exercise.get("preferred", [])) or "not specified"

    meaning = [
        f"{member_name} is the source of truth for every later generated artifact.",
        (
            f"The pipeline should protect {member_name}'s stated goals: "
            f"{', '.join(goal_names)}."
        ),
        (
            f"His exercise preference is {preferred_times}, so provider and facility "
            "availability should create real scheduling tradeoffs instead of perfect fit."
        ),
    ]
    if constraints:
        meaning.append(
            f"Physical constraints such as {', '.join(constraints)} should influence load, "
            "substitutions, and recovery decisions."
        )

    return _stage_card(
        "01_member_profile",
        "Member Profile",
        "ready",
        [
            f"Member: {member_name} ({member.get('member_id')})",
            _plural(len(member.get("goals", [])), "goal"),
            _plural(len(goal_actions), "goal action"),
            _plural(len(phases), "journey phase"),
            _plural(len(travel_windows), "travel window"),
            *goal_actions[:5],
        ],
        meaning,
        [
            "Do the goals justify all later activity modalities?",
            "Are weekly goal targets explicit enough for scheduler-facing math?",
            "Do travel, work, and physical constraints create realistic scheduling pressure?",
        ],
        ["data/member_profile.json"],
    )


def _resources_stage(member: dict[str, Any], resources: dict[str, Any]) -> StageCard:
    member_name = member.get("name", "the member")
    provider_counts = _provider_role_counts(resources)
    provider_summary = ", ".join(
        f"{role}: {count}" for role, count in sorted(provider_counts.items())
    )
    travel_compatible_providers = sum(
        1 for provider in resources.get("providers", []) if provider.get("travel_compatible")
    )

    return _stage_card(
        "02_resource_universe",
        "Resource Universe",
        "ready" if resources else "missing",
        [
            _plural(len(resources.get("providers", [])), "provider"),
            _plural(len(resources.get("equipment", [])), "equipment item"),
            _plural(len(resources.get("locations", [])), "location"),
            _plural(len(resources.get("travel_windows", [])), "travel window"),
            f"Provider coverage: {provider_summary or 'none'}",
            f"Travel-compatible providers: {travel_compatible_providers}",
        ],
        [
            (
                f"This stage defines what exists for {member_name}: providers, locations, "
                "equipment, travel windows, and travel-time rules."
            ),
            (
                "Later stages must reference only these concrete IDs, so this is the "
                "resource boundary for validation and scheduling."
            ),
            (
                "Resource existence is not availability; it only says what could be used "
                "if the calendar later allows it."
            ),
        ],
        [
            "Does provider coverage include trainer, physiotherapist, dietitian, physician, lab, and chef roles?",
            "Do activity and availability references use only resource IDs from this universe?",
            "Do travel-compatible resources match Marcus's planned and last-minute travel context?",
        ],
        ["data/resource_universe.json"],
    )


def _frictions_stage(member: dict[str, Any], frictions_payload: dict[str, Any]) -> StageCard:
    member_name = member.get("name", "Marcus")
    frictions = frictions_payload.get("frictions", [])
    friction_names = [friction.get("name", friction.get("friction_id")) for friction in frictions]

    return _stage_card(
        "03_known_frictions",
        "Known Frictions",
        "ready" if frictions else "missing",
        [
            _plural(len(frictions), "known friction"),
            *friction_names[:8],
        ],
        [
            (
                f"These frictions intentionally make {member_name}'s plan imperfect in "
                "realistic ways."
            ),
            (
                "They are scenario constraints, not scheduler decisions: they should later "
                "show up as substitutions, reschedules, rejected slots, or unscheduled reasons."
            ),
            (
                "The point is to validate adaptation: planned travel should look different "
                "from last-minute travel, and provider/equipment conflicts should be explainable."
            ),
        ],
        [
            "Does every required friction category have a stable ID?",
            "Can each friction be traced to resources, travel windows, activities, or scheduler decisions?",
            "Are conflicts plausible rather than arbitrary contradictions?",
        ],
        ["data/known_frictions.json"],
    )


def _availability_stage(member: dict[str, Any], availability: dict[str, Any]) -> StageCard:
    member_name = member.get("name", "Marcus")
    counts = _availability_counts(availability)
    block_count = len(availability.get("availability_blocks", []))
    provider_count = counts.get("provider", 0)
    blocked_count = counts.get("member_blocked", 0)
    travel_count = counts.get("member_travel", 0) + counts.get("travel_window", 0)

    return _stage_card(
        "04_availability",
        "Availability",
        "ready" if block_count else "missing",
        [
            f"Planning horizon: {availability.get('planning_start_date')} for {availability.get('planning_months')} months",
            _plural(block_count, "availability block"),
            f"Provider blocks: {provider_count}",
            f"Member blocked windows: {blocked_count}",
            f"Travel context blocks: {travel_count}",
            *[
                f"{resource_type}: {count}"
                for resource_type, count in sorted(counts.items())
            ],
        ],
        [
            (
                f"{member_name}'s preferences are now tested against independent member, "
                "provider, equipment, facility, and travel calendars."
            ),
            (
                "This is where the pipeline stops assuming resources are usable just because "
                "they exist."
            ),
            (
                "The scheduler should now have to adapt around blocked work time, constrained "
                "lab windows, limited chef prep, travel overrides, and provider mismatches."
            ),
        ],
        [
            "Does availability cover the full three-month planning horizon?",
            "Are provider calendars limited rather than magically aligned with Marcus's preferences?",
            "Do travel windows override ordinary home, gym, clinic, and lab assumptions?",
        ],
        ["data/availability.json"],
    )


def _activity_stage(member: dict[str, Any], data_dir: Path) -> StageCard:
    member_name = member.get("name", "Marcus")
    families, source_files = _load_stage5_families(data_dir)
    activities = _activity_family_activities(families)
    primary_count = sum(1 for activity in activities if activity.get("is_primary"))
    substitution_count = len(activities) - primary_count
    modality_counts = Counter(activity.get("activity_type", "unknown") for activity in activities)
    goal_action_ids = sorted(
        {
            contribution.get("goal_action_id") or contribution.get("weekly_goal_action_id")
            for activity in activities
            for contribution in activity.get("goal_contributions", [])
            if contribution.get("goal_action_id") or contribution.get("weekly_goal_action_id")
        }
    )
    status = "ready" if len(families) == 50 and len(activities) >= 100 else "in_progress"

    return _stage_card(
        "05_activity_families",
        "Activity Families",
        status,
        [
            _plural(len(families), "activity family", "activity families"),
            _plural(len(activities), "scheduler-facing activity draft"),
            f"Primary activities: {primary_count}",
            f"Substitution activities: {substitution_count}",
            *[
                f"{modality}: {count}"
                for modality, count in sorted(modality_counts.items())
            ],
            f"Goal action IDs referenced: {', '.join(goal_action_ids) or 'none yet'}",
        ],
        [
            (
                f"This is where {member_name}'s goals become prescriptions with frequency, "
                "duration, load, required resources, substitutions, and goal contributions."
            ),
            (
                "A family preserves intent: the primary activity and substitutions should serve "
                "the same goal even when travel, availability, or equipment changes."
            ),
            (
                "Until this stage reaches 50 families and at least 100 scheduler-facing "
                "activities, the final calendar should be treated as not ready."
            ),
        ],
        [
            "Does every counting activity contribution resolve to one of Marcus's goal actions?",
            "Can primary frequencies plausibly satisfy weekly and 3-month targets without support-only over-counting?",
            "Do substitutions reduce a real constraint while preserving the original intent?",
        ],
        source_files or ["data/generated/stage05_activity_families/batches"],
    )


def _validation_stage(data_dir: Path, activity_stage: StageCard) -> StageCard:
    report_path = data_dir / "runs" / "demo-run" / "01_validation" / "validation_report.json"
    model_review_path = (
        data_dir / "runs" / "demo-run" / "01_validation" / "activity_board_model_review.md"
    )
    model_review_metadata_path = (
        data_dir / "generated" / "stage06_activity_board_review" / "metadata_001_review.json"
    )
    model_review_raw_path = (
        data_dir / "generated" / "stage06_activity_board_review" / "raw_response_001_review.md"
    )
    report = _load_optional_json(report_path, {})
    model_review_metadata = _load_optional_json(model_review_metadata_path, {})
    report_status = report.get("status", "not run")
    model_review_exists = model_review_path.is_file()
    status = "pending" if activity_stage["status"] != "ready" else report_status
    errors = report.get("errors", [])
    generated = [
        f"Deterministic validation status: {report_status}",
        f"Activity count in latest report: {report.get('activity_count', 'not available')}",
        f"Primary count in latest report: {report.get('primary_activity_count', 'not available')}",
        f"Validation errors: {len(errors)}",
        f"Model board review: {'available' if model_review_exists else 'not available'}",
    ]
    if model_review_metadata:
        generated.extend(
            [
                f"Model reviewer: {model_review_metadata.get('model', 'unknown')}",
                f"Review attempt: {model_review_metadata.get('attempt', 'unknown')}",
            ]
        )
    generated.extend(errors[:5])

    return _stage_card(
        "06_validation",
        "Validation",
        status,
        generated,
        [
            "Validation is the consistency gate before scheduling should be trusted.",
            (
                "While Stage 5 is still in progress, validation failures are expected and "
                "should be read as repair guidance, not as a final product failure."
            ),
            (
                "Once the activity board is complete, this stage should prove that Marcus's "
                "goals, resources, availability, and activity references resolve end to end."
            ),
            (
                "The model board review adds a qualitative audit of priority, goal coverage, "
                "journey phase fit, dependencies, substitutions, known frictions, and care handoff logic."
            ),
        ],
        [
            "Do all provider, equipment, location, activity, and goal action references resolve?",
            "Do activity counts, primary counts, modalities, and availability density satisfy the assignment?",
            "Does the board-level review flag any unrealistic or contradictory care logic?",
            "Do the raw model response and copied report match the metadata for audit traceability?",
        ],
        [
            str(path.relative_to(data_dir.parent))
            for path in [
                report_path,
                model_review_path,
                model_review_raw_path,
                model_review_metadata_path,
            ]
            if path.is_file()
        ],
    )


def _scheduling_stage(data_dir: Path, activity_stage: StageCard) -> StageCard:
    run_dir = data_dir / "runs" / "demo-run"
    plan = _load_optional_json(run_dir / "03_scheduling" / "personalized_plan.json", {})
    rejection_summary = _load_optional_json(
        run_dir / "03_scheduling" / "rejection_summary.json",
        {},
    )
    calendar_rows = _load_optional_json(run_dir / "04_calendar" / "calendar_rows.json", [])
    scheduled_count = len(plan.get("tasks", []))
    calendar_count = len(calendar_rows) if isinstance(calendar_rows, list) else 0
    status = "pending" if activity_stage["status"] != "ready" else "ready"

    return _stage_card(
        "07_scheduling_and_calendar",
        "Scheduling And Calendar",
        status,
        [
            f"Scheduled tasks in latest run: {scheduled_count}",
            f"Calendar rows in latest run: {calendar_count}",
            f"Rejection categories: {len(rejection_summary) if isinstance(rejection_summary, dict) else 0}",
        ],
        [
            (
                "Scheduling is where prescriptions meet actual availability, conflicts, "
                "travel context, and travel-time rules."
            ),
            (
                "The final calendar should explain what Marcus received, what was substituted, "
                "and what could not be placed."
            ),
            (
                "This stage should only be treated as current after the Marcus activity board "
                "has passed validation and regenerated the run artifacts."
            ),
        ],
        [
            "Do scheduled instances preserve priority order while respecting constraints?",
            "Are substitutions and unscheduled tasks explained with decision traces?",
            "Does final weekly coverage show progress against Marcus's goal targets?",
        ],
        [
            "data/runs/demo-run/03_scheduling/personalized_plan.json",
            "data/runs/demo-run/04_calendar/calendar_rows.json",
        ],
    )


def build_pipeline_story(data_dir: str | Path) -> dict[str, Any]:
    base = Path(data_dir)
    member = _load_optional_json(base / "member_profile.json", {})
    resources = _load_optional_json(base / "resource_universe.json", {})
    frictions = _load_optional_json(base / "known_frictions.json", {})
    availability = _load_optional_json(base / "availability.json", {})

    stages = [
        _member_stage(member),
        _resources_stage(member, resources),
        _frictions_stage(member, frictions),
        _availability_stage(member, availability),
    ]
    activity_stage = _activity_stage(member, base)
    stages.append(activity_stage)
    stages.append(_validation_stage(base, activity_stage))
    stages.append(_scheduling_stage(base, activity_stage))

    return {
        "member_name": member.get("name", "Unknown Member"),
        "member_id": member.get("member_id"),
        "status": "in_progress"
        if any(stage["status"] in {"in_progress", "pending", "missing"} for stage in stages)
        else "ready",
        "stages": stages,
    }
