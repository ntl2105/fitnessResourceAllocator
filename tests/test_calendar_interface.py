from datetime import date

from src.calendar_interface import (
    build_calendar_interface,
    decimal_hour,
    duration_hours,
    monday_start,
)


def test_time_helpers_convert_calendar_row_times():
    assert decimal_hour("07:00") == 7.0
    assert decimal_hour("13:30") == 13.5
    assert duration_hours("07:15", "08:45") == 1.5


def test_monday_start_uses_work_week_boundary():
    assert monday_start(date(2026, 6, 1)).isoformat() == "2026-06-01"
    assert monday_start(date(2026, 6, 7)).isoformat() == "2026-06-01"


def test_build_calendar_interface_groups_rows_and_member_blocked_overlays():
    calendar_rows = [
        {
            "calendar_row_id": "row_1",
            "date": "2026-06-02",
            "start_time": "07:30",
            "end_time": "08:15",
            "title": "Remote physio",
            "activity_type": "therapy",
            "goal_tags": ["travel_continuity"],
            "load_level": "low",
            "location_id": "remote",
            "mode": "remote",
            "substitution_status": "substitution",
            "trace_id": "trace_1",
            "compact_group_key": "2026-06-02:therapy",
        }
    ]
    availability = {
        "availability_blocks": [
            {
                "resource_type": "member_blocked",
                "start": "2026-06-02T08:30:00+08:00",
                "end": "2026-06-02T18:30:00+08:00",
                "notes": "Work block.",
                "location_id": "office",
            }
        ]
    }
    traces = [
        {
            "trace_id": "trace_1",
            "final_status": "scheduled",
            "rejected_candidates": [
                {
                    "reasons": [
                        "office->gym requires 15 minutes; only 5 minutes available after Work block."
                    ]
                }
            ],
            "constraint_checks": [
                {
                    "name": "travel_time_buffer",
                    "passed": False,
                    "reason": "office->gym requires 15 minutes; only 5 minutes available.",
                }
            ],
            "dependency_checks": [],
        }
    ]

    view_model = build_calendar_interface(calendar_rows, availability, traces, {})

    assert view_model["display_hours"] == {"start": 6, "end": 22}
    assert view_model["scenario_counts"]["remote"] == 1
    assert view_model["scenario_counts"]["substitution"] == 1
    assert view_model["scenario_counts"]["travel_time_rejection"] == 1

    week = view_model["weeks"][0]
    assert week["week_id"] == "2026-W23"
    assert week["start_date"] == "2026-06-01"
    assert week["days"][1]["date"] == "2026-06-02"

    activity = week["activities"][0]
    assert activity["day_index"] == 1
    assert activity["start_hour"] == 7.5
    assert activity["duration_hours"] == 0.75
    assert set(activity["scenario_flags"]) >= {
        "remote",
        "substitution",
        "trace_rejections",
        "travel_time_rejection",
    }

    block = week["unavailable_blocks"][0]
    assert block["day_index"] == 1
    assert block["start_hour"] == 8.5
    assert block["duration_hours"] == 10.0
    assert block["label"] == "Work block."


def test_activity_view_resolves_provider_and_clean_display_title():
    calendar_rows = [
        {
            "calendar_row_id": "row_task_1",
            "date": "2026-06-01",
            "start_time": "18:45",
            "end_time": "19:30",
            "title": "Remote or hotel-gym substitution: Trainer-led lower-body strength session",
            "activity_type": "fitness",
            "goal_tags": ["strength"],
            "load_level": "medium",
            "location_id": "remote",
            "mode": "remote",
            "substitution_status": "substitution",
            "trace_id": "trace_1",
        }
    ]
    personalized_plan = {
        "tasks": [
            {
                "task_id": "task_1",
                "activity_id": "act_1",
                "provider_ids": ["provider_trainer_001"],
            }
        ]
    }
    resource_universe = {
        "providers": [
            {
                "provider_id": "provider_trainer_001",
                "provider_type": "trainer",
                "display_name": "Maya Tan",
            }
        ]
    }

    view_model = build_calendar_interface(
        calendar_rows,
        {"availability_blocks": []},
        [
            {
                "trace_id": "trace_1",
                "rejected_candidates": [],
                "constraint_checks": [],
                "dependency_checks": [],
            }
        ],
        {},
        personalized_plan,
        resource_universe,
    )

    activity = view_model["weeks"][0]["activities"][0]
    assert (
        activity["raw_title"]
        == "Remote or hotel-gym substitution: Trainer-led lower-body strength session"
    )
    assert activity["display_title"] == "Trainer-led lower-body strength session"
    assert activity["provider_summary"] == "Maya Tan, trainer"


def test_goal_coverage_reports_week_and_full_plan_risk():
    calendar_rows = [
        {
            "calendar_row_id": "row_task_1",
            "date": "2026-06-02",
            "start_time": "07:00",
            "end_time": "07:40",
            "title": "Zone 2 bike",
            "activity_type": "fitness",
            "goal_tags": ["cardio"],
            "load_level": "medium",
            "location_id": "gym",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": "trace_1",
        }
    ]
    traces = [
        {
            "trace_id": "trace_1",
            "activity_id": "act_1",
            "final_status": "scheduled",
            "rejected_candidates": [],
            "constraint_checks": [],
            "dependency_checks": [],
        },
        {
            "trace_id": "trace_2",
            "activity_id": "act_2",
            "final_status": "unscheduled",
            "policy_fit_summary": "No valid slot.",
            "rejected_candidates": [{"reasons": ["No provider available."]}],
            "constraint_checks": [],
            "dependency_checks": [],
            "task_instance_id": "task_2",
        },
    ]

    view_model = build_calendar_interface(
        calendar_rows,
        {"availability_blocks": []},
        traces,
        {"act_2": {"unscheduled_count": 1, "rejected_candidate_count": 1}},
        {
            "tasks": [
                {
                    "task_id": "task_2",
                    "activity_id": "act_2",
                    "goal_tags": ["cardio"],
                    "status": "unscheduled",
                }
            ]
        },
        {"providers": []},
    )

    week_cardio = view_model["goal_coverage"]["week"][0]
    assert week_cardio["goal_tag"] == "cardio"
    assert week_cardio["scheduled"] == 1
    assert week_cardio["unscheduled"] == 1
    assert week_cardio["status"] == "at_risk"
    assert view_model["unscheduled_items"][0]["activity_id"] == "act_2"
