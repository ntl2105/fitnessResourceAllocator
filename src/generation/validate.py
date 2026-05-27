import shutil
from collections import Counter
from pathlib import Path
from typing import Any

from src.generation.quality_report import (
    build_activity_board_review,
    build_quality_report,
)
from src.io_utils import copy_inputs, load_json, save_json
from src.models.activity import ActivityFamily, ActivityPrescription, ActivityType
from src.models.availability import AvailabilityData
from src.models.member import MemberProfile
from src.models.resources import ResourceUniverse


CARE_DOMAINS = {
    "metabolic nutrition",
    "metabolic_nutrition",
    "cardiorespiratory fitness",
    "cardiorespiratory_fitness",
    "strength, mobility, and pain resilience",
    "strength_mobility_pain",
    "recovery, sleep, and stress regulation",
    "recovery_sleep_stress",
    "clinical review and measurement",
    "clinical_review_measurement",
}

REMOVED_GOAL_ACTION_IDS = {"ga_travel_continuity_3month"}
REQUIRED_GOAL_ACTION_IDS = {
    "ga_care_team_followthrough_3month",
    "ga_behavior_coaching_weekly",
}


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


def _model_value(model: Any, key: str, default: Any = None) -> Any:
    value = getattr(model, key, default)
    if value is not default:
        return value
    extra = getattr(model, "model_extra", None) or {}
    if isinstance(extra, dict):
        return extra.get(key, default)
    return default


def _goal_action_ids_for_member(member: MemberProfile) -> set[str]:
    legacy_ids = {action.weekly_goal_action_id for action in member.weekly_goal_actions}
    period_aware_ids = {action.goal_action_id for action in member.goal_actions}
    return legacy_ids | period_aware_ids


def _contribution_action_id(contribution: dict[str, Any]) -> str | None:
    return contribution.get("goal_action_id") or contribution.get("weekly_goal_action_id")


def _counting_contribution_action_ids(activity: ActivityPrescription) -> set[str]:
    return {
        action_id
        for contribution in activity.goal_contributions
        if (action_id := _contribution_action_id(contribution))
        and contribution.get("counts_toward_weekly_target") is not False
        and contribution.get("value", 1) != 0
    }


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
    activity_families: list[ActivityFamily] | None = None,
) -> dict[str, Any]:
    activity_ids = [activity.activity_id for activity in activities]
    duplicate_ids = _duplicate_ids(activity_ids)
    activity_id_set = set(activity_ids)
    provider_ids = set(resources.provider_ids())
    equipment_ids = set(resources.equipment_ids())
    location_ids = set(resources.location_ids())
    weekly_goal_action_ids = _goal_action_ids_for_member(member)
    removed_goal_action_refs = sorted(weekly_goal_action_ids & REMOVED_GOAL_ACTION_IDS)
    missing_required_goal_actions = sorted(REQUIRED_GOAL_ACTION_IDS - weekly_goal_action_ids)

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
    missing_activity_weekly_goal_refs = sorted(
        {
            _contribution_action_id(contribution)
            for activity in activities
            for contribution in activity.goal_contributions
            if _contribution_action_id(contribution)
            and _contribution_action_id(contribution) not in weekly_goal_action_ids
        }
    )
    missing_family_weekly_goal_refs = sorted(
        {
            goal_action_id
            for family in activity_families or []
            for goal_action_id in [
                *getattr(family, "goal_action_ids", []),
                *getattr(family, "satisfies_weekly_goal_action_ids", []),
            ]
            if goal_action_id not in weekly_goal_action_ids
        }
    )
    active_removed_activity_refs = sorted(
        {
            _contribution_action_id(contribution)
            for activity in activities
            for contribution in activity.goal_contributions
            if _contribution_action_id(contribution) in REMOVED_GOAL_ACTION_IDS
        }
    )
    active_removed_family_refs = sorted(
        {
            goal_action_id
            for family in activity_families or []
            for goal_action_id in [
                *getattr(family, "goal_action_ids", []),
                *getattr(family, "satisfies_weekly_goal_action_ids", []),
            ]
            if goal_action_id in REMOVED_GOAL_ACTION_IDS
        }
    )
    enforce_family_targets = any(
        _model_value(family, "care_domain") or _model_value(family, "family_target")
        for family in activity_families or []
    )
    family_target_errors: list[str] = []
    substitution_alignment_errors: list[str] = []
    if enforce_family_targets:
        for family in activity_families or []:
            family_id = family.activity_family_id
            care_domain = _model_value(family, "care_domain")
            family_target = _model_value(family, "family_target")
            if not care_domain:
                family_target_errors.append(f"{family_id} missing care_domain")
            elif str(care_domain) not in CARE_DOMAINS:
                family_target_errors.append(
                    f"{family_id} has invalid care_domain {care_domain}"
                )
            if not isinstance(family_target, dict):
                family_target_errors.append(f"{family_id} missing family_target")
                continue
            target_action_id = (
                family_target.get("goal_action_id")
                or family_target.get("weekly_goal_action_id")
            )
            if not target_action_id:
                family_target_errors.append(f"{family_id} family_target missing goal_action_id")
                continue
            if target_action_id not in weekly_goal_action_ids:
                family_target_errors.append(
                    f"{family_id} family_target references unknown goal action {target_action_id}"
                )
            if family_target.get("period") not in {"weekly", "3_month"}:
                family_target_errors.append(
                    f"{family_id} family_target period must be weekly or 3_month"
                )
            if family_target.get("target_units") is None and family_target.get("units") is None:
                family_target_errors.append(f"{family_id} family_target missing target_units")
            if family_target.get("substitutions_count") is not False:
                for substitution in family.substitution_activities:
                    action_ids = _counting_contribution_action_ids(substitution)
                    if action_ids and target_action_id not in action_ids:
                        substitution_alignment_errors.append(
                            f"{substitution.activity_id} counts toward "
                            f"{', '.join(sorted(action_ids))}, expected {target_action_id}"
                        )
    modalities_present = sorted({activity.activity_type.value for activity in activities})
    expected_modalities = {modality.value for modality in ActivityType}
    primary_activity_count = sum(1 for activity in activities if activity.is_primary)
    activity_family_count = len(activity_families or [])
    availability_coverage = _availability_coverage(availability)
    availability_resource_type_counts = Counter(
        block.resource_type for block in availability.availability_blocks
    )
    travel_context_count = (
        availability_resource_type_counts["member_travel"]
        + availability_resource_type_counts["travel_window"]
    )
    availability_distribution_passed = (
        120 <= availability_resource_type_counts["provider"] <= 200
        and 70 <= availability_resource_type_counts["member_blocked"] <= 100
        and 10 <= availability_resource_type_counts["equipment"] <= 30
        and 6 <= availability_resource_type_counts["location"] <= 40
        and travel_context_count == 6
    )

    checks = {
        "at_least_100_activities": _check(
            len(activities) >= 100,
            f"Found {len(activities)} activities.",
        ),
        "exactly_50_activity_families": _check(
            activity_family_count == 50 if activity_families is not None else True,
            f"Found {activity_family_count} activity families."
            if activity_families is not None
            else "Activity family document not provided.",
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
        "member_has_goal_actions": _check(
            bool(member.goal_actions) or bool(member.weekly_goal_actions),
            f"Found {len(member.goal_actions)} goal actions."
            if member.goal_actions
            else f"Found {len(member.weekly_goal_actions)} legacy weekly goal actions."
            if member.weekly_goal_actions
            else "Member profile must include goal actions.",
        ),
        "goal_taxonomy_replaces_travel_continuity": _check(
            not removed_goal_action_refs and not missing_required_goal_actions,
            "Travel-continuity action removed and replacement goal actions are present."
            if not removed_goal_action_refs and not missing_required_goal_actions
            else "Goal taxonomy mismatch: "
            f"removed refs={', '.join(removed_goal_action_refs) or 'none'}; "
            f"missing required={', '.join(missing_required_goal_actions) or 'none'}",
        ),
        "active_data_omits_removed_goal_actions": _check(
            not active_removed_activity_refs and not active_removed_family_refs,
            "Active activities and families omit removed goal actions."
            if not active_removed_activity_refs and not active_removed_family_refs
            else "Removed goal action referenced by active data: "
            f"activities={', '.join(active_removed_activity_refs) or 'none'}; "
            f"families={', '.join(active_removed_family_refs) or 'none'}",
        ),
        "activity_goal_action_references_resolve": _check(
            not missing_activity_weekly_goal_refs,
            "All activity goal action references resolve."
            if not missing_activity_weekly_goal_refs
            else "Missing goal actions: "
            f"{', '.join(missing_activity_weekly_goal_refs)}",
        ),
        "activity_family_goal_action_references_resolve": _check(
            not missing_family_weekly_goal_refs,
            "All activity family goal action references resolve."
            if not missing_family_weekly_goal_refs
            else "Missing goal actions: "
            f"{', '.join(missing_family_weekly_goal_refs)}",
        ),
        "activity_family_targets_present": _check(
            not family_target_errors,
            "Activity family targets are complete."
            if not family_target_errors
            else "; ".join(family_target_errors),
        ),
        "substitution_target_alignment": _check(
            not substitution_alignment_errors,
            "Substitutions preserve family-level counted targets."
            if not substitution_alignment_errors
            else "; ".join(substitution_alignment_errors),
        ),
        "availability_has_3_months": _check(
            availability.planning_months == 3,
            f"Planning months: {availability.planning_months}.",
        ),
        "availability_has_blocks": _check(
            bool(availability.availability_blocks),
            f"Found {len(availability.availability_blocks)} availability blocks.",
        ),
        "availability_has_realistic_block_density": _check(
            225 <= len(availability.availability_blocks) <= 375,
            f"Availability coverage found {len(availability.availability_blocks)} blocks; "
            "expected 225-375 concrete scheduler-facing blocks for a "
            "3-month demo.",
        ),
        "availability_keeps_equipment_compact": _check(
            availability_resource_type_counts["equipment"] <= 30,
            f"Found {availability_resource_type_counts['equipment']} equipment blocks; "
            "expected 30 or fewer so equipment does not dominate the audit data.",
        ),
        "availability_distribution_matches_targets": _check(
            availability_distribution_passed,
            "Availability resource-type counts match target ranges."
            if availability_distribution_passed
            else "Expected provider 120-200, member_blocked 70-100, "
            "equipment 10-30, location 6-40, and member_travel + "
            f"travel_window = 6. Found {dict(availability_resource_type_counts)}.",
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
        "activity_family_count": activity_family_count,
        "modalities_present": modalities_present,
        "availability_block_count": len(availability.availability_blocks),
        "availability_resource_type_counts": dict(availability_resource_type_counts),
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
    availability_patterns_path = base / "availability_patterns.json"
    if availability_patterns_path.exists():
        input_paths.insert(3, availability_patterns_path)
    member, resources, availability, activities = load_canonical_data(base)
    activity_families_payload = load_json(base / "activity_families.json")
    activity_families = []
    if isinstance(activity_families_payload, dict):
        activity_families = [
            ActivityFamily.model_validate(family)
            for family in activity_families_payload.get("activity_families", [])
        ]
    report = build_validation_report(
        member,
        resources,
        availability,
        activities,
        activity_families=activity_families,
    )

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
