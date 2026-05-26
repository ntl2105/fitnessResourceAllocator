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
