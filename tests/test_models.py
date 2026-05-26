from datetime import date, datetime

from src.models.activity import (
    ActivityFamiliesDocument,
    ActivityFamily,
    ActivityPrescription,
    ActivityType,
)
from src.models.availability import AvailabilityData
from src.models.member import JourneyPhase, MemberProfile
from src.models.resources import ResourceUniverse
from src.models.schedule import CalendarRow, TaskInstance
from src.models.trace import ConstraintCheck, DecisionTrace


def test_member_profile_parses_seed_with_journey_phase_timeline(load_seed):
    profile = MemberProfile.model_validate(load_seed("member_profile.json"))

    assert profile.member_id == "member_elyx_001"
    assert profile.journey_phases
    assert isinstance(profile.journey_phases[0].start_date, date)
    assert profile.journey_phases[0].phase_type == "baseline"
    assert profile.travel_windows[0].travel_window_id == "travel_hk_2026_06"


def test_resource_universe_parses_seed_and_exposes_resource_ids(load_seed):
    universe = ResourceUniverse.model_validate(load_seed("resource_universe.json"))

    assert "provider_physio_001" in universe.provider_ids()
    assert "eq_stationary_bike" in universe.equipment_ids()
    assert {"home", "office", "gym", "clinic", "lab", "remote"}.issubset(
        set(universe.location_ids())
    )


def test_activity_families_document_parses_seed_and_flattens_activities(load_seed):
    document = ActivityFamiliesDocument.model_validate(load_seed("activity_families.json"))

    assert document.activity_families
    assert len(document.activity_families) >= 1
    assert len(document.flattened_activities()) > len(document.activity_families)
    assert document.flatten_activities() == document.flattened_activities()
    assert document.activity_families[0].primary_activity.is_primary is True

    family_with_substitution = next(
        family for family in document.activity_families if family.substitution_activities
    )
    flattened_ids = family_with_substitution.flattened_activity_ids()
    assert flattened_ids[0] == family_with_substitution.primary_activity.activity_id
    assert flattened_ids[1] == family_with_substitution.substitution_activities[0].activity_id


def test_activity_prescription_allows_structured_skip_adjustment_and_dependency_metadata(load_seed):
    document = ActivityFamiliesDocument.model_validate(load_seed("activity_families.json"))
    activity = document.activity_families[0].primary_activity

    assert isinstance(activity.skip_adjustment, dict)
    assert activity.dependencies[0]["type"] == "fasting"
    assert activity.dependencies[0]["hours"] == 10


def test_availability_data_parses_seed(load_seed):
    availability = AvailabilityData.model_validate(load_seed("availability.json"))

    assert availability.planning_start_date == date(2026, 6, 1)
    assert availability.planning_months == 3
    assert availability.availability_blocks
    assert isinstance(availability.availability_blocks[0].start, datetime)


def test_activity_family_contains_primary_and_substitution():
    primary = ActivityPrescription(
        activity_id="act_001",
        priority=1,
        goal_tags=["knee_health"],
        activity_type=ActivityType.FITNESS,
        title="In-person PT strength",
        frequency={"type": "weekly", "count": 1},
        duration_minutes=45,
        load_level="medium",
        details="Knee-safe lower-body strength",
        facilitator_type="physiotherapist",
        required_provider_ids=["provider_pt_001"],
        required_equipment_ids=[],
        allowed_locations=["clinic"],
        remote_allowed=False,
        prep_required=False,
        dependencies=[],
        substitution_activity_ids=["act_002"],
        skip_adjustment={"fallback": "Use remote mobility if missed."},
        metrics_to_collect=["pain_score"],
        care_context_required=["knee limitation summary"],
        share_with_provider_types=["physiotherapist"],
        raw_clinical_data_required=False,
        journey_phase_applicability=["baseline"],
        same_day_repeat_allowed=False,
        is_primary=True,
        activity_family_id="fam_001",
    )
    substitution = primary.model_copy(
        update={
            "activity_id": "act_002",
            "title": "Remote PT mobility",
            "remote_allowed": True,
            "allowed_locations": ["remote"],
            "is_primary": False,
            "substitution_activity_ids": [],
        }
    )

    family = ActivityFamily(
        activity_family_id="fam_001",
        intent="Maintain knee-safe strength.",
        goal_tags=["knee_health"],
        primary_activity=primary,
        substitution_activities=[substitution],
        substitution_rules=[
            {
                "when": "travel_or_provider_unavailable",
                "prefer_activity_id": "act_002",
            }
        ],
        family_validation_notes=[],
    )

    assert family.flattened_activity_ids() == ["act_001", "act_002"]
    assert family.flattened_activities() == [primary, substitution]
    assert family.flatten_activities() == family.flattened_activities()


def test_task_instance_defines_required_contract_fields():
    expected_fields = {
        "task_instance_id",
        "activity_id",
        "activity_family_id",
        "is_substitution",
        "target_date",
        "target_week",
        "duration_minutes",
        "priority",
        "goal_tags",
        "required_resources",
        "dependencies",
        "status",
    }
    assert expected_fields.issubset(TaskInstance.model_fields)

    task = TaskInstance(
        task_instance_id="task_001",
        activity_id="act_001",
        activity_family_id="fam_001",
        is_substitution=False,
        target_date=date(2026, 6, 4),
        target_week="2026-W23",
        duration_minutes=45,
        priority=1,
        goal_tags=["metabolic_health"],
        required_resources={
            "provider_ids": ["provider_lab_001"],
            "equipment_ids": ["eq_lab_draw_station"],
            "location_ids": ["lab"],
        },
        dependencies=[{"type": "fasting", "hours": 10}],
        status="pending",
    )

    assert task.task_instance_id == "task_001"
    assert task.required_resources["provider_ids"] == ["provider_lab_001"]


def test_decision_trace_and_calendar_row_match_required_contracts():
    assert {
        "name",
        "passed",
        "reason",
    }.issubset(ConstraintCheck.model_fields)
    assert {
        "trace_id",
        "task_instance_id",
        "activity_id",
        "final_status",
        "selected_slot",
        "policy_fit_summary",
        "resource_fit_summary",
        "constraint_checks",
        "rejected_candidates",
        "substitution_reason",
        "dependency_checks",
        "provider_handoff_summary",
        "skip_adjustment_applied",
        "source_artifact_paths",
    }.issubset(DecisionTrace.model_fields)
    assert {
        "calendar_row_id",
        "date",
        "start_time",
        "end_time",
        "title",
        "activity_type",
        "goal_tags",
        "load_level",
        "location_id",
        "mode",
        "substitution_status",
        "trace_id",
        "compact_group_key",
    }.issubset(CalendarRow.model_fields)

    trace = DecisionTrace(
        task_instance_id="task_001",
        activity_id="act_001",
        final_status="scheduled",
        selected_slot={
            "start": "2026-06-04T07:30:00+08:00",
            "end": "2026-06-04T08:15:00+08:00",
            "location_id": "lab",
        },
        policy_fit_summary="Target date and fasting window fit.",
        resource_fit_summary="Lab provider and draw station available.",
        constraint_checks=[
            ConstraintCheck(
                name="fasting_window",
                passed=True,
                reason="Scheduled after 10-hour fast.",
            )
        ],
        rejected_candidates=[
            {
                "start": "2026-06-05T07:30:00+08:00",
                "reason": "outside target preference",
            }
        ],
        substitution_reason=None,
        dependency_checks=[{"dependency": "fasting", "passed": True}],
        provider_handoff_summary="Share lab order with provider_lab_001.",
        skip_adjustment_applied=None,
        source_artifact_paths=["data/activity_families.json"],
    )
    row = CalendarRow(
        calendar_row_id="row_001",
        date=date(2026, 6, 4),
        start_time="07:30",
        end_time="08:15",
        title="Baseline fasting metabolic lab panel",
        activity_type=ActivityType.CONSULTATION,
        goal_tags=["metabolic_health"],
        load_level="low",
        location_id="lab",
        mode="in_person",
        substitution_status="primary",
        trace_id=trace.trace_id,
        compact_group_key="2026-06-04:consultation",
    )

    assert trace.final_status == "scheduled"
    assert trace.constraint_checks[0].passed is True
    assert row.trace_id == trace.trace_id
