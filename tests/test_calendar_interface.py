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


def test_provider_summary_suppresses_travel_pool_wording_on_cards():
    calendar_rows = [
        {
            "calendar_row_id": "row_task_1",
            "date": "2026-06-01",
            "start_time": "06:30",
            "end_time": "07:15",
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
                "provider_ids": ["provider_trainer_remote_001"],
            }
        ]
    }
    resource_universe = {
        "providers": [
            {
                "provider_id": "provider_trainer_remote_001",
                "provider_type": "trainer",
                "display_name": "Remote travel trainer pool",
            }
        ]
    }

    view_model = build_calendar_interface(
        calendar_rows,
        {"availability_blocks": []},
        [],
        {},
        personalized_plan,
        resource_universe,
    )

    activity = view_model["weeks"][0]["activities"][0]
    assert activity["provider_summary"] == "Remote trainer pool, trainer"


def test_display_title_removes_remote_fallback_prefix():
    calendar_rows = [
        {
            "calendar_row_id": "row_task_1",
            "date": "2026-06-01",
            "start_time": "08:00",
            "end_time": "08:30",
            "title": "Remote fallback: Baseline movement and knee assessment",
            "activity_type": "consultation",
            "goal_tags": ["knee_health"],
            "load_level": "low",
            "location_id": "remote",
            "mode": "remote",
            "substitution_status": "substitution",
            "trace_id": "trace_1",
        }
    ]

    view_model = build_calendar_interface(
        calendar_rows,
        {"availability_blocks": []},
        [],
        {},
    )

    assert (
        view_model["weeks"][0]["activities"][0]["display_title"]
        == "Baseline movement and knee assessment"
    )


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


def test_weeks_carry_week_scoped_goal_coverage_and_unscheduled_items():
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
        },
        {
            "calendar_row_id": "row_task_2",
            "date": "2026-06-09",
            "start_time": "07:00",
            "end_time": "07:30",
            "title": "Mobility",
            "activity_type": "therapy",
            "goal_tags": ["mobility"],
            "load_level": "low",
            "location_id": "home",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": "trace_2",
        },
    ]
    traces = [
        {
            "trace_id": "trace_3",
            "activity_id": "act_3",
            "final_status": "unscheduled",
            "policy_fit_summary": "No candidate satisfied all policy checks.",
            "rejected_candidates": [
                {
                    "reasons": [
                        "No availability block covers physical location clinic for candidate slot."
                    ]
                }
            ],
            "constraint_checks": [],
            "dependency_checks": [],
            "task_instance_id": "task_3",
        }
    ]
    personalized_plan = {
        "tasks": [
            {
                "task_id": "task_3",
                "activity_id": "act_3",
                "goal_tags": ["cardio"],
                "status": "unscheduled",
                "target_date": "2026-06-05",
                "title": "Cardiology consult",
            }
        ]
    }

    view_model = build_calendar_interface(
        calendar_rows,
        {"availability_blocks": []},
        traces,
        {"act_3": {"unscheduled_count": 1, "rejected_candidate_count": 1}},
        personalized_plan,
        {"providers": []},
    )

    first_week = view_model["weeks"][0]
    second_week = view_model["weeks"][1]

    assert first_week["goal_coverage"] == [
        {
            "goal_tag": "cardio",
            "scheduled": 1,
            "unscheduled": 1,
            "substitutions": 0,
            "status": "at_risk",
        }
    ]
    assert first_week["unscheduled_items"][0]["title"] == "Cardiology consult"
    assert first_week["unscheduled_items"][0]["reason_summary"] == (
        "No clinic availability for this candidate slot."
    )
    assert second_week["goal_coverage"] == [
        {
            "goal_tag": "mobility",
            "scheduled": 1,
            "unscheduled": 0,
            "substitutions": 0,
            "status": "on_track",
        }
    ]
    assert second_week["unscheduled_items"] == []


def test_unscheduled_items_resolve_titles_and_goals_from_action_plan():
    traces = [
        {
            "trace_id": "trace_1",
            "activity_id": "act_002",
            "final_status": "unscheduled",
            "policy_fit_summary": "No candidate satisfied all policy checks.",
            "rejected_candidates": [
                {
                    "start": "2026-06-05T07:00:00+08:00",
                    "reasons": [
                        "No availability block covers physical location clinic for candidate slot."
                    ],
                }
            ],
            "constraint_checks": [],
            "dependency_checks": [],
            "task_instance_id": "task_act_002_20260605_001",
        }
    ]
    action_plan = {
        "activities": [
            {
                "activity_id": "act_002",
                "title": "Baseline movement and knee assessment",
                "goal_tags": ["knee_health", "strength"],
                "frequency": {"target_date": "2026-06-05"},
            }
        ]
    }

    view_model = build_calendar_interface(
        [],
        {"availability_blocks": []},
        traces,
        {"act_002": {"unscheduled_count": 1, "rejected_candidate_count": 7}},
        {"tasks": []},
        {"providers": []},
        action_plan,
    )

    item = view_model["weeks"][0]["unscheduled_items"][0]
    assert item["title"] == "Baseline movement and knee assessment"
    assert item["goal_tags"] == ["knee_health", "strength"]
    assert item["reason_summary"] == "No clinic availability for this candidate slot."


def test_calendar_interface_exposes_location_bands_and_travel_blocks():
    availability = {
        "availability_blocks": [
            {
                "resource_type": "member_blocked",
                "start": "2026-06-01T08:30:00+08:00",
                "end": "2026-06-01T18:30:00+08:00",
                "location_id": "office",
                "notes": "Work block.",
            },
            {
                "resource_type": "member_travel",
                "start": "2026-06-03T09:30:00+08:00",
                "end": "2026-06-05T13:15:00+08:00",
                "location_id": "travel_hotel",
                "notes": "Hong Kong planned travel.",
            },
        ]
    }

    view_model = build_calendar_interface(
        [], availability, [], {}, {"tasks": []}, {"providers": []}
    )
    week = view_model["weeks"][0]

    assert week["location_bands"][0]["label"] == "Hong Kong planned travel."
    assert len(week["location_bands"]) == 1
    assert week["travel_blocks"][0]["location_id"] == "travel_hotel"
    assert week["travel_blocks"][0]["start_hour"] == 9.5


def test_calendar_interface_reports_data_generation_warnings():
    rows = [
        {
            "calendar_row_id": "row_task_1",
            "date": "2026-06-01",
            "start_time": "08:00",
            "end_time": "08:10",
            "title": "Morning supplement protocol",
            "activity_type": "food",
            "goal_tags": ["nutrition"],
            "load_level": "low",
            "location_id": "home",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": "trace_1",
        },
        {
            "calendar_row_id": "row_task_2",
            "date": "2026-06-01",
            "start_time": "12:00",
            "end_time": "12:30",
            "title": "No-prep fallback for high-protein prepared breakfast",
            "activity_type": "food",
            "goal_tags": ["nutrition"],
            "load_level": "low",
            "location_id": "home",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": "trace_2",
        },
    ]

    view_model = build_calendar_interface(
        rows,
        {
            "availability_blocks": [
                {
                    "resource_type": "member_travel",
                    "start": "2026-06-03T00:00:00+08:00",
                    "end": "2026-06-04T23:59:00+08:00",
                    "location_id": "travel_hotel",
                    "notes": "Travel window.",
                }
            ]
        },
        [],
        {},
        {"tasks": []},
        {"providers": []},
    )

    warnings = " ".join(view_model["data_quality_warnings"])
    assert (
        "Food plan has supplement/protocol rows but no explicit breakfast/lunch/dinner coverage"
        in warnings
    )
    assert "Raw activity titles still contain fallback/substitution wording" in warnings
    assert "Travel windows should include exact travel leg times" in warnings
