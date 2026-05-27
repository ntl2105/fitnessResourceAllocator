import json
import shutil
from datetime import date

import pytest

import scripts.validate_data as validate_data_script
from src.generation.flatten import flatten_activity_families, write_action_plan
from src.generation.validate import (
    build_validation_report,
    load_activities_payload,
    validate_canonical_data,
    write_validation_artifacts,
)
from src.generation.quality_report import build_activity_board_review
from src.models.activity import ActivityFamiliesDocument, ActivityPrescription
from src.models.availability import AvailabilityData
from src.models.member import MemberProfile
from src.models.resources import ResourceUniverse


def test_flatten_activity_families_returns_activity_prescriptions(load_seed):
    document = ActivityFamiliesDocument.model_validate(load_seed("activity_families.json"))

    activities = flatten_activity_families(document.activity_families)

    assert len(activities) == len(document.flattened_activities())
    assert activities[0].activity_id == document.activity_families[0].primary_activity.activity_id
    assert activities[0].activity_family_id == document.activity_families[0].activity_family_id


def test_write_action_plan_accepts_wrapper_and_writes_activities_wrapper(tmp_path, load_seed):
    source_path = tmp_path / "activity_families.json"
    output_path = tmp_path / "action_plan.json"
    source_path.write_text(json.dumps(load_seed("activity_families.json")))

    activities = write_action_plan(source_path, output_path)

    payload = json.loads(output_path.read_text())
    assert list(payload) == ["activities"]
    assert len(payload["activities"]) == len(activities)
    assert payload["activities"][0]["activity_id"] == activities[0].activity_id


def test_load_activities_payload_accepts_wrapper_and_array(load_seed):
    document = ActivityFamiliesDocument.model_validate(load_seed("activity_families.json"))
    activity_dicts = [
        activity.model_dump(mode="json") for activity in document.flattened_activities()
    ]

    wrapped = load_activities_payload({"activities": activity_dicts})
    raw = load_activities_payload(activity_dicts)

    assert [activity.activity_id for activity in wrapped] == [
        activity.activity_id for activity in raw
    ]


def test_active_goal_taxonomy_replaces_travel_continuity(load_seed):
    profile = load_seed("member_profile.json")
    action_ids = {action["goal_action_id"] for action in profile["goal_actions"]}

    assert "ga_travel_continuity_3month" not in action_ids
    assert "ga_care_team_followthrough_3month" in action_ids
    assert "ga_behavior_coaching_weekly" in action_ids


def test_active_activities_do_not_reference_travel_continuity(load_seed):
    activity_families = load_seed("activity_families.json")["activity_families"]
    action_plan = load_seed("action_plan.json")["activities"]

    family_refs = {
        goal_action_id
        for family in activity_families
        for goal_action_id in family.get("goal_action_ids", [])
    }
    activity_refs = {
        contribution.get("goal_action_id")
        for activity in action_plan
        for contribution in activity.get("goal_contributions", [])
        if contribution.get("goal_action_id")
    }

    assert "ga_travel_continuity_3month" not in family_refs
    assert "ga_travel_continuity_3month" not in activity_refs


def test_activity_board_review_reports_generation_qa_flags():
    activities = [
        _activity(
            "act_breakfast_weekday",
            "High-protein breakfast",
            activity_type="food",
            meal_slot="breakfast",
        ),
        _activity(
            "act_breakfast_weekend",
            "Weekend structured breakfast",
            activity_type="food",
            meal_slot="breakfast",
            details="Max 1x per weekend.",
            frequency={"type": "weekly", "count": 2},
        ),
        _activity(
            "act_hydration",
            "Daily hydration and electrolyte protocol",
            activity_type="medication",
            goal_contributions=[
                {
                    "weekly_goal_action_id": "wga_support",
                    "counts_toward_weekly_target": False,
                }
            ],
        ),
        _activity(
            "act_travel_strength",
            "Travel-adapted strength session",
            goal_contributions=[
                {
                    "weekly_goal_action_id": "wga_travel_adapted_sessions",
                    "counts_toward_weekly_target": True,
                }
            ],
        ),
    ]

    report = build_activity_board_review(activities)

    assert "## QA Flags" in report
    assert "breakfast has 2 primary food activities" in report
    assert "frequency count is 2, but details say max 1" in report
    assert "support/prep/protocol work but has no dependency link" in report
    assert "travel adaptation should usually be substitution logic" in report


def _activity(
    activity_id: str,
    title: str,
    *,
    activity_type: str = "fitness",
    meal_slot: str | None = None,
    details: str | None = None,
    frequency: dict | None = None,
    goal_contributions: list[dict] | None = None,
) -> ActivityPrescription:
    payload = {
        "activity_id": activity_id,
        "priority": 1,
        "goal_tags": [],
        "goal_contributions": goal_contributions
        if goal_contributions is not None
        else [
            {
                "weekly_goal_action_id": "wga_core",
                "counts_toward_weekly_target": True,
            }
        ],
        "activity_type": activity_type,
        "title": title,
        "frequency": frequency or {"type": "weekly", "count": 1},
        "duration_minutes": 30,
        "load_level": "low",
        "details": details,
        "is_primary": True,
        "activity_family_id": f"fam_{activity_id}",
    }
    if meal_slot:
        payload["meal_slot"] = meal_slot
    return ActivityPrescription.model_validate(payload)


def test_validate_canonical_data_rejects_duplicate_activity_ids(load_seed):
    activities = load_activities_payload(
        {
            "activities": [
                activity.model_dump(mode="json")
                for activity in ActivityFamiliesDocument.model_validate(
                    load_seed("activity_families.json")
                ).flattened_activities()
            ]
        }
    )
    activities[1] = activities[1].model_copy(
        update={"activity_id": activities[0].activity_id}
    )

    with pytest.raises(ValueError, match="Duplicate activity IDs"):
        validate_canonical_data(
            member=MemberProfile.model_validate(load_seed("member_profile.json")),
            resources=ResourceUniverse.model_validate(load_seed("resource_universe.json")),
            availability=AvailabilityData.model_validate(load_seed("availability.json")),
            activities=activities,
        )


def test_validate_canonical_data_rejects_one_block_availability_coverage(load_seed):
    activities = load_activities_payload(
        {
            "activities": [
                activity.model_dump(mode="json")
                for activity in ActivityFamiliesDocument.model_validate(
                    load_seed("activity_families.json")
                ).flattened_activities()
            ]
        }
    )
    availability = AvailabilityData.model_validate(load_seed("availability.json"))
    incomplete_availability = availability.model_copy(
        update={"availability_blocks": [availability.availability_blocks[0]]}
    )

    with pytest.raises(ValueError, match="coverage"):
        validate_canonical_data(
            member=MemberProfile.model_validate(load_seed("member_profile.json")),
            resources=ResourceUniverse.model_validate(load_seed("resource_universe.json")),
            availability=incomplete_availability,
            activities=activities,
        )


def test_validation_report_requires_realistic_availability_density(load_seed):
    document = ActivityFamiliesDocument.model_validate(load_seed("activity_families.json"))
    report = build_validation_report(
        member=MemberProfile.model_validate(load_seed("member_profile.json")),
        resources=ResourceUniverse.model_validate(load_seed("resource_universe.json")),
        availability=AvailabilityData.model_validate(load_seed("availability.json")),
        activities=document.flattened_activities(),
    )

    assert 225 <= report["availability_block_count"] <= 375
    assert report["checks"]["availability_has_realistic_block_density"]["passed"]


def test_validation_report_requires_compact_equipment_availability(load_seed):
    document = ActivityFamiliesDocument.model_validate(load_seed("activity_families.json"))
    report = build_validation_report(
        member=MemberProfile.model_validate(load_seed("member_profile.json")),
        resources=ResourceUniverse.model_validate(load_seed("resource_universe.json")),
        availability=AvailabilityData.model_validate(load_seed("availability.json")),
        activities=document.flattened_activities(),
    )

    assert report["availability_resource_type_counts"]["equipment"] <= 30
    assert report["checks"]["availability_keeps_equipment_compact"]["passed"]


def test_validation_report_enforces_availability_distribution_targets(load_seed):
    document = ActivityFamiliesDocument.model_validate(load_seed("activity_families.json"))
    report = build_validation_report(
        member=MemberProfile.model_validate(load_seed("member_profile.json")),
        resources=ResourceUniverse.model_validate(load_seed("resource_universe.json")),
        availability=AvailabilityData.model_validate(load_seed("availability.json")),
        activities=document.flattened_activities(),
    )

    counts = report["availability_resource_type_counts"]
    assert 120 <= counts["provider"] <= 200
    assert 70 <= counts["member_blocked"] <= 100
    assert 10 <= counts["equipment"] <= 30
    assert 6 <= counts["location"] <= 40
    assert counts["member_travel"] + counts["travel_window"] == 6
    assert report["checks"]["availability_distribution_matches_targets"]["passed"]


def test_validation_rejects_missing_goal_actions(load_seed):
    activities = load_activities_payload(
        {
            "activities": [
                activity.model_dump(mode="json")
                for activity in ActivityFamiliesDocument.model_validate(
                    load_seed("activity_families.json")
                ).flattened_activities()
            ]
        }
    )
    member = MemberProfile.model_validate(load_seed("member_profile.json")).model_copy(
        update={"goal_actions": [], "weekly_goal_actions": []}
    )

    with pytest.raises(ValueError, match="goal actions"):
        validate_canonical_data(
            member=member,
            resources=ResourceUniverse.model_validate(load_seed("resource_universe.json")),
            availability=AvailabilityData.model_validate(load_seed("availability.json")),
            activities=activities,
        )


def test_validation_rejects_unknown_goal_action_contribution(load_seed):
    activities = load_activities_payload(
        {
            "activities": [
                activity.model_dump(mode="json")
                for activity in ActivityFamiliesDocument.model_validate(
                    load_seed("activity_families.json")
                ).flattened_activities()
            ]
        }
    )
    activities[0] = activities[0].model_copy(
        update={
            "goal_contributions": [
                    {
                        "goal_id": "metabolic_health",
                        "goal_action_id": "ga_missing",
                    "role": "core",
                    "counts_toward_weekly_target": True,
                    "unit": "activity",
                    "value": 1,
                }
            ]
        }
    )

    with pytest.raises(ValueError, match="Missing goal actions"):
        validate_canonical_data(
            member=MemberProfile.model_validate(load_seed("member_profile.json")),
            resources=ResourceUniverse.model_validate(load_seed("resource_universe.json")),
            availability=AvailabilityData.model_validate(load_seed("availability.json")),
            activities=activities,
        )


def test_validation_report_rejects_unknown_family_goal_action(load_seed):
    document = ActivityFamiliesDocument.model_validate(load_seed("activity_families.json"))
    broken_family = document.activity_families[0].model_copy(
        update={"goal_action_ids": ["ga_missing"]}
    )
    report = build_validation_report(
        member=MemberProfile.model_validate(load_seed("member_profile.json")),
        resources=ResourceUniverse.model_validate(load_seed("resource_universe.json")),
        availability=AvailabilityData.model_validate(load_seed("availability.json")),
        activities=document.flattened_activities(),
        activity_families=[broken_family, *document.activity_families[1:]],
    )

    assert report["status"] == "fail"
    assert "Missing goal actions" in report["checks"][
        "activity_family_goal_action_references_resolve"
    ]["message"]


def test_validation_requires_family_targets_when_goal_actions_are_present(load_seed):
    document = ActivityFamiliesDocument.model_validate(load_seed("activity_families.json"))
    broken_family = document.activity_families[0].model_copy(
        update={"care_domain": "metabolic_nutrition", "family_target": None}
    )

    report = build_validation_report(
        member=MemberProfile.model_validate(load_seed("member_profile.json")),
        resources=ResourceUniverse.model_validate(load_seed("resource_universe.json")),
        availability=AvailabilityData.model_validate(load_seed("availability.json")),
        activities=document.flattened_activities(),
        activity_families=[broken_family, *document.activity_families[1:]],
    )

    assert report["status"] == "fail"
    assert "activity_family_targets_present" in report["checks"]
    assert "missing family_target" in report["checks"]["activity_family_targets_present"]["message"]


def test_validation_rejects_substitution_that_does_not_count_toward_family_target(load_seed):
    document = ActivityFamiliesDocument.model_validate(load_seed("activity_families.json"))
    family = document.activity_families[0]
    primary = family.primary_activity.model_copy(
        update={
            "goal_contributions": [
                {
                    "goal_action_id": "ga_structured_meals_weekly",
                    "counts_toward_weekly_target": True,
                    "value": 1,
                }
            ]
        }
    )
    substitution = family.substitution_activities[0].model_copy(
        update={
            "goal_contributions": [
                {
                    "goal_action_id": "ga_unrelated_001",
                    "counts_toward_weekly_target": True,
                    "value": 1,
                }
            ]
        }
    )
    broken_family = family.model_copy(
        update={
            "care_domain": "metabolic_nutrition",
            "family_target": {
                "goal_action_id": "ga_structured_meals_weekly",
                "period": "weekly",
                "target_units": 14,
                "unit_label": "meals",
                "substitutions_count": True,
                "support_counts": False,
            },
            "primary_activity": primary,
            "substitution_activities": [substitution],
        }
    )
    member_payload = load_seed("member_profile.json")
    member_payload["goal_actions"] = [
        {
            "goal_action_id": "ga_structured_meals_weekly",
            "goal_id": "goal_metabolic_health",
            "label": "Complete structured metabolic meals",
            "role": "core",
            "target": {"period": "weekly", "units": 14, "unit_label": "meals"},
        }
    ]

    report = build_validation_report(
        member=MemberProfile.model_validate(member_payload),
        resources=ResourceUniverse.model_validate(load_seed("resource_universe.json")),
        availability=AvailabilityData.model_validate(load_seed("availability.json")),
        activities=broken_family.flattened_activities(),
        activity_families=[broken_family],
    )

    assert report["status"] == "fail"
    assert "substitution_target_alignment" in report["checks"]
    assert "ga_unrelated_001" in report["checks"]["substitution_target_alignment"]["message"]


def test_availability_coverage_handles_end_of_month_planning_start(load_seed):
    activities = load_activities_payload(
        {
            "activities": [
                activity.model_dump(mode="json")
                for activity in ActivityFamiliesDocument.model_validate(
                    load_seed("activity_families.json")
                ).flattened_activities()
            ]
        }
    )
    availability = AvailabilityData.model_validate(load_seed("availability.json"))
    end_of_month_availability = availability.model_copy(
        update={"planning_start_date": date(2026, 1, 31)}
    )

    report = build_validation_report(
        member=MemberProfile.model_validate(load_seed("member_profile.json")),
        resources=ResourceUniverse.model_validate(load_seed("resource_universe.json")),
        availability=end_of_month_availability,
        activities=activities,
    )

    assert report["availability_coverage"]["expected_months"] == [
        "2026-01",
        "2026-02",
        "2026-03",
    ]


def test_failed_validation_writes_report_without_validated_input_snapshot(
    tmp_path, data_dir, load_seed
):
    for filename in [
        "member_profile.json",
        "resource_universe.json",
        "known_frictions.json",
        "activity_families.json",
        "action_plan.json",
    ]:
        shutil.copy2(data_dir / filename, tmp_path / filename)

    availability_payload = load_seed("availability.json")
    availability_payload["availability_blocks"] = [
        availability_payload["availability_blocks"][0]
    ]
    (tmp_path / "availability.json").write_text(json.dumps(availability_payload))

    report = write_validation_artifacts(tmp_path, run_id="failed-run")

    run_dir = tmp_path / "runs" / "failed-run"
    assert report["status"] == "fail"
    assert (run_dir / "01_validation" / "validation_report.json").exists()
    assert "errors" in json.loads(
        (run_dir / "01_validation" / "validation_report.json").read_text()
    )
    assert not (run_dir / "00_inputs").exists()
    assert not (run_dir / "01_validation" / "synthetic_data_quality_report.md").exists()


def test_successful_validation_writes_quality_report_under_inputs(
    tmp_path, data_dir
):
    for filename in [
        "member_profile.json",
        "resource_universe.json",
        "known_frictions.json",
        "activity_families.json",
        "availability.json",
        "action_plan.json",
    ]:
        shutil.copy2(data_dir / filename, tmp_path / filename)

    report = write_validation_artifacts(tmp_path, run_id="successful-run")

    run_dir = tmp_path / "runs" / "successful-run"
    assert report["status"] == "pass"
    assert (run_dir / "00_inputs" / "synthetic_data_quality_report.md").exists()
    assert not (run_dir / "01_validation" / "synthetic_data_quality_report.md").exists()
    assert (run_dir / "01_validation" / "validation_report.json").exists()
    assert (run_dir / "01_validation" / "activity_board_review.md").exists()


def test_validate_data_script_returns_nonzero_for_failed_validation(monkeypatch):
    monkeypatch.setattr(
        validate_data_script,
        "write_validation_artifacts",
        lambda data_dir: {
            "status": "fail",
            "activity_count": 1,
            "primary_activity_count": 0,
        },
    )

    assert validate_data_script.main() == 1


def test_validate_data_script_returns_zero_for_successful_validation(monkeypatch):
    monkeypatch.setattr(
        validate_data_script,
        "write_validation_artifacts",
        lambda data_dir: {
            "status": "pass",
            "activity_count": 102,
            "primary_activity_count": 87,
        },
    )

    assert validate_data_script.main() == 0
