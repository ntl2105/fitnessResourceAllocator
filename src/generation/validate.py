import shutil
from pathlib import Path
from typing import Any

from src.generation.quality_report import (
    build_activity_board_review,
    build_quality_report,
)
from src.io_utils import copy_inputs, load_json, save_json
from src.models.activity import ActivityPrescription, ActivityType
from src.models.availability import AvailabilityData
from src.models.member import MemberProfile
from src.models.resources import ResourceUniverse


def load_activities_payload(payload: Any) -> list[ActivityPrescription]:
    if isinstance(payload, dict):
        if "activities" not in payload:
            raise ValueError("Activity payload wrapper must contain an 'activities' key.")
        payload = payload["activities"]
    if not isinstance(payload, list):
        raise ValueError("Activity payload must be an array or an object wrapper.")
    return [ActivityPrescription.model_validate(item) for item in payload]


def _check(passed: bool, message: str) -> dict[str, Any]:
    return {"passed": passed, "message": message}


def _duplicate_ids(activity_ids: list[str]) -> list[str]:
    seen = set()
    duplicates = []
    for activity_id in activity_ids:
        if activity_id in seen and activity_id not in duplicates:
            duplicates.append(activity_id)
        seen.add(activity_id)
    return duplicates


def _add_months(start_date, month_count: int):
    month_index = start_date.month - 1 + month_count
    year = start_date.year + month_index // 12
    month = month_index % 12 + 1
    return start_date.replace(day=1, year=year, month=month)


def _month_keys_between(start_date, end_date):
    keys = []
    current = start_date.replace(day=1)
    while current < end_date:
        keys.append((current.year, current.month))
        current = _add_months(current, 1)
    return keys


def _availability_coverage(availability: AvailabilityData) -> dict[str, Any]:
    coverage_start = availability.planning_start_date
    coverage_end = _add_months(coverage_start, availability.planning_months)
    expected_months = _month_keys_between(coverage_start, coverage_end)
    covered_months = set()

    for block in availability.availability_blocks:
        block_start = block.start.date()
        block_end = block.end.date()
        if block.end.time() != block.start.time() or block_end == block_start:
            block_end = max(block_end, block_start)
        if block_end < coverage_start or block_start >= coverage_end:
            continue
        intersect_start = max(block_start, coverage_start)
        intersect_end = min(block_end, coverage_end)
        for month_key in _month_keys_between(intersect_start, intersect_end):
            covered_months.add(month_key)
        covered_months.add((intersect_start.year, intersect_start.month))

    missing_months = [month for month in expected_months if month not in covered_months]
    final_month = expected_months[-1] if expected_months else None
    return {
        "coverage_start": coverage_start.isoformat(),
        "coverage_end_exclusive": coverage_end.isoformat(),
        "expected_months": [f"{year:04d}-{month:02d}" for year, month in expected_months],
        "covered_months": [
            f"{year:04d}-{month:02d}" for year, month in sorted(covered_months)
        ],
        "missing_months": [f"{year:04d}-{month:02d}" for year, month in missing_months],
        "final_month_covered": final_month in covered_months if final_month else False,
        "passed": not missing_months and bool(expected_months),
    }


def build_validation_report(
    member: MemberProfile,
    resources: ResourceUniverse,
    availability: AvailabilityData,
    activities: list[ActivityPrescription],
) -> dict[str, Any]:
    activity_ids = [activity.activity_id for activity in activities]
    duplicate_ids = _duplicate_ids(activity_ids)
    activity_id_set = set(activity_ids)
    provider_ids = set(resources.provider_ids())
    equipment_ids = set(resources.equipment_ids())
    location_ids = set(resources.location_ids())

    missing_provider_refs = sorted(
        {
            provider_id
            for activity in activities
            for provider_id in activity.required_provider_ids
            if provider_id not in provider_ids
        }
    )
    missing_equipment_refs = sorted(
        {
            equipment_id
            for activity in activities
            for equipment_id in activity.required_equipment_ids
            if equipment_id not in equipment_ids
        }
    )
    missing_location_refs = sorted(
        {
            location_id
            for activity in activities
            for location_id in activity.allowed_locations
            if location_id not in location_ids
        }
    )
    missing_substitution_refs = sorted(
        {
            substitution_id
            for activity in activities
            for substitution_id in activity.substitution_activity_ids
            if substitution_id not in activity_id_set
        }
    )
    modalities_present = sorted({activity.activity_type.value for activity in activities})
    expected_modalities = {modality.value for modality in ActivityType}
    primary_activity_count = sum(1 for activity in activities if activity.is_primary)
    availability_coverage = _availability_coverage(availability)

    checks = {
        "at_least_100_activities": _check(
            len(activities) >= 100,
            f"Found {len(activities)} activities.",
        ),
        "at_least_60_primary_activities": _check(
            primary_activity_count >= 60,
            f"Found {primary_activity_count} primary activities.",
        ),
        "unique_activity_ids": _check(
            not duplicate_ids,
            "No duplicate IDs found."
            if not duplicate_ids
            else f"Duplicate activity IDs: {', '.join(duplicate_ids)}",
        ),
        "all_modalities_present": _check(
            expected_modalities.issubset(set(modalities_present)),
            f"Present modalities: {', '.join(modalities_present)}.",
        ),
        "provider_references_resolve": _check(
            not missing_provider_refs,
            "All provider references resolve."
            if not missing_provider_refs
            else f"Missing providers: {', '.join(missing_provider_refs)}",
        ),
        "equipment_references_resolve": _check(
            not missing_equipment_refs,
            "All equipment references resolve."
            if not missing_equipment_refs
            else f"Missing equipment: {', '.join(missing_equipment_refs)}",
        ),
        "location_references_resolve": _check(
            not missing_location_refs,
            "All location references resolve."
            if not missing_location_refs
            else f"Missing locations: {', '.join(missing_location_refs)}",
        ),
        "substitution_references_resolve": _check(
            not missing_substitution_refs,
            "All substitution references resolve."
            if not missing_substitution_refs
            else f"Missing substitutions: {', '.join(missing_substitution_refs)}",
        ),
        "member_has_journey_phases": _check(
            bool(member.journey_phases),
            f"Found {len(member.journey_phases)} journey phases.",
        ),
        "availability_has_3_months": _check(
            availability.planning_months == 3,
            f"Planning months: {availability.planning_months}.",
        ),
        "availability_has_blocks": _check(
            bool(availability.availability_blocks),
            f"Found {len(availability.availability_blocks)} availability blocks.",
        ),
        "availability_covers_planning_months": _check(
            availability_coverage["passed"],
            "Availability coverage spans expected months "
            f"{', '.join(availability_coverage['expected_months'])}."
            if availability_coverage["passed"]
            else "Availability coverage missing months: "
            f"{', '.join(availability_coverage['missing_months'])}.",
        ),
    }

    errors = [check["message"] for check in checks.values() if not check["passed"]]
    return {
        "status": "pass" if all(check["passed"] for check in checks.values()) else "fail",
        "errors": errors,
        "activity_count": len(activities),
        "primary_activity_count": primary_activity_count,
        "modalities_present": modalities_present,
        "availability_coverage": availability_coverage,
        "checks": checks,
    }


def validate_canonical_data(
    member: MemberProfile,
    resources: ResourceUniverse,
    availability: AvailabilityData,
    activities: list[ActivityPrescription],
) -> dict[str, Any]:
    report = build_validation_report(member, resources, availability, activities)
    if report["errors"]:
        raise ValueError("; ".join(report["errors"]))
    return report


def load_canonical_data(data_dir: str | Path) -> tuple[
    MemberProfile,
    ResourceUniverse,
    AvailabilityData,
    list[ActivityPrescription],
]:
    base = Path(data_dir)
    return (
        MemberProfile.model_validate(load_json(base / "member_profile.json")),
        ResourceUniverse.model_validate(load_json(base / "resource_universe.json")),
        AvailabilityData.model_validate(load_json(base / "availability.json")),
        load_activities_payload(load_json(base / "action_plan.json")),
    )


def write_validation_artifacts(data_dir: str | Path, run_id: str = "demo-run") -> dict[str, Any]:
    base = Path(data_dir)
    run_dir = base / "runs" / run_id
    inputs_dir = run_dir / "00_inputs"
    validation_dir = run_dir / "01_validation"

    input_paths = [
        base / "member_profile.json",
        base / "resource_universe.json",
        base / "known_frictions.json",
        base / "activity_families.json",
        base / "availability.json",
        base / "action_plan.json",
    ]
    member, resources, availability, activities = load_canonical_data(base)
    report = build_validation_report(member, resources, availability, activities)

    validation_dir.mkdir(parents=True, exist_ok=True)
    save_json(validation_dir / "validation_report.json", report)
    if report["status"] != "pass":
        if inputs_dir.exists():
            shutil.rmtree(inputs_dir)
        for artifact_name in [
            "synthetic_data_quality_report.md",
            "activity_board_review.md",
        ]:
            artifact_path = validation_dir / artifact_name
            if artifact_path.exists():
                artifact_path.unlink()
        return report

    copy_inputs(input_paths, inputs_dir)
    stale_quality_report = validation_dir / "synthetic_data_quality_report.md"
    if stale_quality_report.exists():
        stale_quality_report.unlink()
    (inputs_dir / "synthetic_data_quality_report.md").write_text(
        build_quality_report(report),
        encoding="utf-8",
    )
    (validation_dir / "activity_board_review.md").write_text(
        build_activity_board_review(activities),
        encoding="utf-8",
    )
    return report
