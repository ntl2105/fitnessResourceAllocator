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
from src.models.activity import ActivityFamiliesDocument
from src.models.availability import AvailabilityData
from src.models.member import MemberProfile
from src.models.resources import ResourceUniverse


def test_flatten_activity_families_returns_activity_prescriptions(load_seed):
    document = ActivityFamiliesDocument.model_validate(load_seed("activity_families.json"))

    activities = flatten_activity_families(document.activity_families)

    assert len(activities) == len(document.flattened_activities())
    assert activities[0].activity_id == "act_001"
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
