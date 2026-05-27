from datetime import date

from src.calendar_interface import (
    build_calendar_interface,
    decimal_hour,
    duration_hours,
    monday_start,
    normalized_goal_actions,
    recap_action_rows,
)


def test_time_helpers_convert_calendar_row_times():
    assert decimal_hour("07:00") == 7.0
    assert decimal_hour("13:30") == 13.5
    assert duration_hours("07:15", "08:45") == 1.5


def test_monday_start_uses_work_week_boundary():
    assert monday_start(date(2026, 6, 1)).isoformat() == "2026-06-01"
    assert monday_start(date(2026, 6, 7)).isoformat() == "2026-06-01"


def test_normalized_goal_actions_accepts_legacy_and_period_aware_shapes():
    profile = {
        "weekly_goal_actions": [
            {
                "weekly_goal_action_id": "wga_cardio_sessions_001",
                "goal_id": "goal_cardio",
                "label": "Complete aerobic conditioning",
                "role": "core",
                "target_per_week": 2,
                "support_only": False,
            }
        ],
        "goal_actions": [
            {
                "goal_action_id": "ga_clinical_review_001",
                "goal_id": "goal_clinical",
                "label": "Complete clinical review package",
                "role": "measurement",
                "target": {
                    "period": "3_month",
                    "units": 1,
                    "unit_label": "package",
                },
                "support_only": False,
            }
        ],
    }

    actions = normalized_goal_actions(profile)

    assert actions[0]["goal_action_id"] == "ga_clinical_review_001"
    assert actions[0]["period"] == "3_month"
    assert actions[0]["target_units"] == 1
    assert actions[1]["goal_action_id"] == "wga_cardio_sessions_001"
    assert actions[1]["weekly_goal_action_id"] == "wga_cardio_sessions_001"
    assert actions[1]["period"] == "weekly"
    assert actions[1]["target_units"] == 2


def test_activity_board_exposes_assignment_tracking_fields():
    action_plan = {
        "activities": [
            {
                "activity_id": "act_cardio",
                "activity_family_id": "fam_cardio",
                "activity_type": "fitness",
                "title": "Zone 2 aerobic session",
                "details": "Maintain HR between 120-140.",
                "frequency": {"type": "weekly", "count": 3},
                "duration_minutes": 40,
                "load_level": "medium",
                "facilitator_type": "trainer",
                "required_provider_ids": ["provider_trainer_01"],
                "allowed_locations": ["gym", "home"],
                "remote_allowed": True,
                "prep_required": True,
                "prep_source": "bike setup",
                "substitution_activity_ids": ["act_cardio_walk"],
                "skip_adjustment": {
                    "if_skipped": "Move to next available evening.",
                    "next_action": "Lower intensity if delayed.",
                },
                "metrics_to_collect": ["heart_rate", "RPE"],
                "goal_contributions": [
                    {
                        "goal_action_id": "ga_cardio",
                        "counts_toward_weekly_target": True,
                        "role": "core",
                    }
                ],
                "dependencies": [],
                "priority": 5,
                "is_primary": True,
            }
        ]
    }
    member_profile = {
        "goal_actions": [
            {
                "goal_action_id": "ga_cardio",
                "label": "Aerobic conditioning",
                "target": {"period": "weekly", "units": 3},
            }
        ]
    }
    traces = [{"trace_id": "trace_1", "activity_id": "act_cardio", "final_status": "scheduled"}]

    view_model = build_calendar_interface(
        [],
        {"availability_blocks": []},
        traces,
        {},
        action_plan=action_plan,
        member_profile=member_profile,
    )

    row = view_model["activity_board"][0]["activities"][0]
    assert row["details"] == "Maintain HR between 120-140."
    assert row["facilitator_type"] == "trainer"
    assert row["provider_ids"] == ["provider_trainer_01"]
    assert row["locations"] == ["gym", "home"]
    assert row["remote_allowed"] is True
    assert row["prep_required"] is True
    assert row["prep_source"] == "bike setup"
    assert row["backup_activity_ids"] == ["act_cardio_walk"]
    assert row["skip_adjustment"] == "Move to next available evening. Lower intensity if delayed."
    assert row["metrics"] == ["heart_rate", "RPE"]


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


def test_calendar_marks_travel_between_different_locations():
    calendar_rows = [
        {
            "calendar_row_id": "row_1",
            "date": "2026-06-02",
            "start_time": "17:00",
            "end_time": "17:30",
            "title": "Office check-in",
            "activity_type": "consultation",
            "goal_tags": ["care"],
            "load_level": "low",
            "location_id": "office",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": "trace_1",
        },
        {
            "calendar_row_id": "row_2",
            "date": "2026-06-02",
            "start_time": "18:00",
            "end_time": "18:45",
            "title": "Gym session",
            "activity_type": "fitness",
            "goal_tags": ["strength"],
            "load_level": "medium",
            "location_id": "gym",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": "trace_2",
        },
    ]

    view_model = build_calendar_interface(
        calendar_rows,
        {"availability_blocks": []},
        [],
        {},
        resource_universe={
            "travel_time_rules": [
                {"from_location_id": "office", "to_location_id": "gym", "minutes": 15}
            ]
        },
    )

    second_activity = view_model["weeks"][0]["activities"][1]
    assert second_activity["travel_to"] == "🚇 Travel to gym · 15m"


def test_calendar_does_not_mark_travel_to_home_after_away_activity():
    calendar_rows = [
        {
            "calendar_row_id": "row_1",
            "date": "2026-06-02",
            "start_time": "08:30",
            "end_time": "09:15",
            "title": "Gym session",
            "activity_type": "fitness",
            "goal_tags": ["cardio"],
            "load_level": "medium",
            "location_id": "gym",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": "trace_1",
        },
        {
            "calendar_row_id": "row_2",
            "date": "2026-06-02",
            "start_time": "11:00",
            "end_time": "11:50",
            "title": "Home session",
            "activity_type": "fitness",
            "goal_tags": ["strength"],
            "load_level": "medium",
            "location_id": "home",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": "trace_2",
        },
    ]

    view_model = build_calendar_interface(calendar_rows, {"availability_blocks": []}, [], {})

    second_activity = view_model["weeks"][0]["activities"][1]
    assert second_activity["travel_to"] is None


def test_calendar_marks_travel_to_first_non_home_activity():
    calendar_rows = [
        {
            "calendar_row_id": "row_lab",
            "date": "2026-06-02",
            "start_time": "07:30",
            "end_time": "08:00",
            "title": "Fasting blood panel",
            "activity_type": "consultation",
            "goal_tags": ["lab"],
            "load_level": "low",
            "location_id": "clinic",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": "trace_lab",
        }
    ]

    view_model = build_calendar_interface(
        calendar_rows,
        {"availability_blocks": []},
        [],
        {},
        resource_universe={
            "travel_time_rules": [
                {"from_location_id": "home", "to_location_id": "clinic", "minutes": 20}
            ]
        },
    )

    first_activity = view_model["weeks"][0]["activities"][0]
    assert first_activity["travel_to"] == "🚇 Travel to clinic · 20m"


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


def test_food_activity_card_omits_meal_tracking_and_source_summaries():
    calendar_rows = [
        {
            "calendar_row_id": "row_task_breakfast",
            "date": "2026-06-01",
            "start_time": "08:00",
            "end_time": "08:30",
            "title": "High-protein breakfast",
            "activity_type": "food",
            "goal_tags": ["nutrition", "breakfast"],
            "load_level": "low",
            "location_id": "home",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": "trace_1",
        }
    ]
    personalized_plan = {
        "tasks": [{"task_id": "task_breakfast", "activity_id": "act_breakfast"}]
    }
    action_plan = {
        "activities": [
            {
                "activity_id": "act_breakfast",
                "activity_type": "food",
                "meal_slot": "breakfast",
                "prep_source": "chef_prepped",
                "metrics_to_collect": ["meal_completion", "protein_servings"],
                "goal_contributions": [
                    {
                        "goal_action_id": "ga_structured_meals_weekly",
                        "counts_toward_weekly_target": True,
                    }
                ],
                "dependencies": [
                    {
                        "type": "prep_task",
                        "provider_type": "chef",
                        "can_be_done_by_member": True,
                        "can_be_done_by_provider": True,
                        "prep_duration_minutes": 30,
                        "offset_minutes_min": 30,
                    }
                ],
            }
        ]
    }

    view_model = build_calendar_interface(
        calendar_rows,
        {"availability_blocks": []},
        [],
        {},
        personalized_plan,
        {"providers": []},
        action_plan,
    )

    activity = view_model["weeks"][0]["activities"][0]
    assert activity["prep_summary"] is None
    assert activity["meal_summary"] is None


def test_food_activity_card_omits_source_without_required_prep():
    calendar_rows = [
        {
            "calendar_row_id": "row_task_lunch",
            "date": "2026-06-01",
            "start_time": "12:00",
            "end_time": "12:25",
            "title": "Office lunch",
            "activity_type": "food",
            "goal_tags": ["nutrition", "lunch"],
            "load_level": "low",
            "location_id": "office",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": "trace_1",
        }
    ]
    personalized_plan = {"tasks": [{"task_id": "task_lunch", "activity_id": "act_lunch"}]}
    action_plan = {
        "activities": [
            {
                "activity_id": "act_lunch",
                "activity_type": "food",
                "meal_slot": "lunch",
                "prep_required": False,
                "prep_source": "member_assembled",
                "metrics_to_collect": ["meal_completion"],
                "goal_contributions": [],
            }
        ]
    }

    view_model = build_calendar_interface(
        calendar_rows,
        {"availability_blocks": []},
        [],
        {},
        personalized_plan,
        {"providers": []},
        action_plan,
    )

    activity = view_model["weeks"][0]["activities"][0]
    assert activity["prep_summary"] is None
    assert activity["meal_summary"] is None


def test_low_complexity_medication_habits_are_compacted_out_of_activity_cards():
    calendar_rows = [
        {
            "calendar_row_id": "row_task_cgm",
            "date": "2026-06-01",
            "start_time": "07:00",
            "end_time": "07:03",
            "title": "Morning CGM check and log",
            "activity_type": "medication",
            "goal_tags": ["cgm", "metabolic"],
            "load_level": "low",
            "location_id": "home",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": "trace_cgm",
        },
        {
            "calendar_row_id": "row_task_breakfast",
            "date": "2026-06-01",
            "start_time": "08:00",
            "end_time": "08:30",
            "title": "High-protein breakfast",
            "activity_type": "food",
            "goal_tags": ["breakfast"],
            "load_level": "low",
            "location_id": "home",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": "trace_breakfast",
        },
    ]

    view_model = build_calendar_interface(calendar_rows, {"availability_blocks": []}, [], {})
    week = view_model["weeks"][0]

    assert [activity["title"] for activity in week["activities"]] == ["High-protein breakfast"]
    assert week["habit_blocks"] == [
        {
            "day_index": 0,
            "count": 1,
            "summary": "Habits: 07:00 CGM check",
            "items": [{"time": "07:00", "title": "CGM check"}],
        }
    ]


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


def test_calendar_interface_builds_visual_member_profile_model():
    member_profile = {
        "member_id": "member_001",
        "name": "Avery Lee",
        "age_range": "45-49",
        "occupation": "Regional executive",
        "timezone": "Asia/Singapore",
        "profile_summary": "Avery needs a travel-aware healthspan schedule.",
        "goals": [
            {
                "goal_id": "goal_strength",
                "name": "Build strength",
                "priority": 1,
                "description": "Increase strength without knee flare-ups.",
            },
            {
                "goal_id": "goal_sleep",
                "label": "Improve sleep",
                "weekly_target": {"minimum": 2, "preferred": 3, "unit": "sessions"},
            },
        ],
        "preferences": {
            "exercise_timing": {"preferred": ["06:30-08:00"]},
            "training_preferences": ["trainer-led strength"],
        },
        "dietary_access_plan": {
            "home_chef_access": True,
            "office_meal_access": "packed lunch delivery",
            "chef_capacity_per_week": 2,
            "member_assembly_limit_per_week": 2,
            "dining_out_allowance_per_week": 3,
            "explicit_meal_scheduling": ["breakfast", "lunch", "dinner"],
        },
        "constraints": {
            "physical": [
                {
                    "name": "Mild knee discomfort",
                    "severity": "mild",
                    "implications": ["prefer knee-safe strength"],
                }
            ],
            "schedule": ["frequent travel"],
        },
        "baseline_metrics": {
            "body_composition": {"weight_kg": 78, "waist_cm": 92},
            "sleep": {"average_sleep_duration_hours": 6.3},
        },
        "journey_phases": [
            {
                "phase_id": "phase_001",
                "phase_type": "baseline",
                "start_date": "2026-06-01",
                "end_date": "2026-06-21",
                "primary_goals": ["goal_strength"],
            }
        ],
        "travel_windows": [
            {
                "travel_window_id": "travel_hk",
                "start": "2026-06-17T08:00:00+08:00",
                "end": "2026-06-21T21:00:00+08:00",
                "destination": "Hong Kong",
                "travel_type": "planned",
                "notes": "Hotel gym available.",
            }
        ],
        "scheduling_rules": {
            "planning_start_date": "2026-06-01",
            "planning_months": 3,
            "prefer_morning_exercise": True,
        },
    }

    view_model = build_calendar_interface(
        [],
        {"availability_blocks": []},
        [],
        {},
        resource_universe={
            "providers": [
                {
                    "provider_id": "provider_chef_01",
                    "provider_type": "chef",
                    "display_name": "Chef Liyang",
                    "modalities_supported": ["in_person", "prepped_dropoff"],
                    "location_ids": ["home", "office"],
                    "remote_supported": False,
                    "travel_compatible": False,
                    "care_context_supported": ["meal_prep"],
                    "notes": "Prepares metabolic meals.",
                }
            ]
        },
        member_profile=member_profile,
    )

    profile = view_model["member_profile"]
    assert profile["identity"]["name"] == "Avery Lee"
    assert profile["identity"]["summary"] == "Avery needs a travel-aware healthspan schedule."
    assert profile["stats"][0] == {"label": "Age", "value": "45-49"}
    assert profile["goals"][0]["label"] == "Build strength"
    assert profile["goals"][1]["target"] == "minimum 2, preferred 3 sessions"
    assert profile["preferences"][0]["value"] == "06:30-08:00"
    assert profile["dietary_access"][1] == {
        "label": "Office meals",
        "value": "packed lunch delivery",
    }
    assert profile["constraints"][0]["label"] == "Mild knee discomfort"
    assert profile["baseline"][0]["label"] == "Body composition"
    assert profile["journey_phases"][0]["label"] == "baseline"
    assert profile["travel_windows"][0]["destination"] == "Hong Kong"
    assert profile["provider_universe"][0]["name"] == "Chef Liyang"
    assert profile["provider_universe"][0]["locations"] == ["home", "office"]
    assert profile["scheduling_rules"][0]["value"] == "2026-06-01 for 3 months"


def test_goal_coverage_uses_weekly_goal_actions_when_available():
    member_profile = {
        "weekly_goal_actions": [
            {
                "weekly_goal_action_id": "wga_cardio_sessions_001",
                "goal_id": "goal_cardio",
                "label": "Complete aerobic conditioning",
                "role": "core",
                "target_per_week": 2,
                "activity_types": ["fitness"],
                "required_meal_slots": [],
                "substitutions_allowed": True,
                "counts_substitutions": True,
                "support_only": False,
                "notes": "Zone 2 work counts directly.",
            },
            {
                "weekly_goal_action_id": "wga_adherence_protocol_001",
                "goal_id": "goal_adherence",
                "label": "Complete support protocol actions",
                "role": "support",
                "target_per_week": 7,
                "activity_types": ["medication"],
                "required_meal_slots": [],
                "substitutions_allowed": False,
                "counts_substitutions": False,
                "support_only": True,
                "notes": "Support only.",
            },
        ]
    }
    action_plan = {
        "activities": [
            {
                "activity_id": "act_cardio",
                "title": "Zone 2 bike",
                "goal_tags": ["cardio"],
                "goal_contributions": [
                    {
                        "goal_id": "goal_cardio",
                        "weekly_goal_action_id": "wga_cardio_sessions_001",
                        "role": "core",
                        "counts_toward_weekly_target": True,
                        "unit": "activity",
                        "value": 1,
                    }
                ],
            },
            {
                "activity_id": "act_cardio_missed",
                "title": "Zone 2 walk",
                "goal_tags": ["cardio"],
                "goal_contributions": [
                    {
                        "goal_id": "goal_cardio",
                        "weekly_goal_action_id": "wga_cardio_sessions_001",
                        "role": "core",
                        "counts_toward_weekly_target": True,
                        "unit": "activity",
                        "value": 1,
                    }
                ],
                "frequency": {"target_date": "2026-06-05"},
            },
            {
                "activity_id": "act_supplement",
                "title": "Morning supplement protocol",
                "goal_tags": ["adherence"],
                "goal_contributions": [
                    {
                        "goal_id": "goal_adherence",
                        "weekly_goal_action_id": "wga_adherence_protocol_001",
                        "role": "support",
                        "counts_toward_weekly_target": False,
                        "unit": "activity",
                        "value": 0,
                    }
                ],
            },
        ]
    }
    calendar_rows = [
        {
            "calendar_row_id": "row_task_cardio",
            "date": "2026-06-02",
            "start_time": "07:00",
            "end_time": "07:40",
            "title": "Zone 2 bike",
            "activity_type": "fitness",
            "goal_tags": ["cardio"],
            "load_level": "medium",
            "location_id": "gym",
            "mode": "in_person",
            "substitution_status": "substitution",
            "trace_id": "trace_1",
        },
        {
            "calendar_row_id": "row_task_supplement",
            "date": "2026-06-02",
            "start_time": "08:00",
            "end_time": "08:10",
            "title": "Morning supplement protocol",
            "activity_type": "medication",
            "goal_tags": ["adherence"],
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
            "activity_id": "act_cardio_missed",
            "final_status": "unscheduled",
            "policy_fit_summary": "No valid slot.",
            "rejected_candidates": [{"reasons": ["No provider available."]}],
            "constraint_checks": [],
            "dependency_checks": [],
            "task_instance_id": "task_cardio_missed",
        }
    ]
    personalized_plan = {
        "tasks": [
            {"task_id": "task_cardio", "activity_id": "act_cardio"},
            {"task_id": "task_supplement", "activity_id": "act_supplement"},
            {
                "task_id": "task_cardio_missed",
                "activity_id": "act_cardio_missed",
                "target_date": "2026-06-05",
            },
        ]
    }

    view_model = build_calendar_interface(
        calendar_rows,
        {"availability_blocks": []},
        traces,
        {"act_cardio_missed": {"unscheduled_count": 1}},
        personalized_plan,
        {"providers": []},
        action_plan,
        member_profile,
    )

    cardio = view_model["weeks"][0]["goal_coverage"][0]
    assert cardio["weekly_goal_action_id"] == "wga_cardio_sessions_001"
    assert cardio["label"] == "Complete aerobic conditioning"
    assert cardio["goal_tag"] == "goal_cardio"
    assert cardio["target_per_week"] == 2
    assert cardio["scheduled"] == 1
    assert cardio["unscheduled"] == 1
    assert cardio["planned"] == 2
    assert cardio["substitutions"] == 1
    assert cardio["status"] == "at_risk"

    support = view_model["weeks"][0]["goal_coverage"][1]
    assert support["weekly_goal_action_id"] == "wga_adherence_protocol_001"
    assert support["support_only"] is True
    assert support["scheduled"] == 0
    assert support["support_scheduled"] == 1
    assert support["status"] == "support_only"


def test_three_month_recap_summarizes_horizon_goal_completion():
    member_profile = {
        "scheduling_rules": {
            "planning_start_date": "2026-06-01",
            "planning_months": 1,
        },
        "goals": [
            {
                "goal_id": "goal_cardio",
                "name": "Improve aerobic base",
                "priority": 1,
                "description": "Build weekly zone 2 consistency.",
            }
        ],
        "weekly_goal_actions": [
            {
                "weekly_goal_action_id": "wga_cardio_sessions_001",
                "goal_id": "goal_cardio",
                "label": "Complete aerobic conditioning",
                "role": "core",
                "target_per_week": 2,
                "support_only": False,
                "notes": "Zone 2 work counts directly.",
            }
        ],
    }
    action_plan = {
        "activities": [
            {
                "activity_id": "act_cardio",
                "title": "Zone 2 bike",
                "goal_contributions": [
                    {
                        "goal_id": "goal_cardio",
                        "weekly_goal_action_id": "wga_cardio_sessions_001",
                        "role": "core",
                        "counts_toward_weekly_target": True,
                        "unit": "activity",
                        "value": 1,
                    }
                ],
            },
            {
                "activity_id": "act_cardio_missed",
                "title": "Zone 2 walk",
                "goal_contributions": [
                    {
                        "goal_id": "goal_cardio",
                        "weekly_goal_action_id": "wga_cardio_sessions_001",
                        "role": "core",
                        "counts_toward_weekly_target": True,
                        "unit": "activity",
                        "value": 1,
                    }
                ],
            },
        ]
    }
    calendar_rows = [
        {
            "calendar_row_id": "row_task_cardio",
            "date": "2026-06-02",
            "start_time": "07:00",
            "end_time": "07:40",
            "title": "Zone 2 bike",
            "activity_type": "fitness",
            "goal_tags": ["cardio"],
            "load_level": "medium",
            "location_id": "gym",
            "mode": "in_person",
            "substitution_status": "substitution",
            "trace_id": "trace_1",
        }
    ]
    traces = [
        {
            "trace_id": "trace_2",
            "activity_id": "act_cardio_missed",
            "final_status": "unscheduled",
            "policy_fit_summary": "No valid slot.",
            "rejected_candidates": [{"reasons": ["No provider available."]}],
            "constraint_checks": [],
            "dependency_checks": [],
            "task_instance_id": "task_cardio_missed",
        }
    ]
    personalized_plan = {
        "tasks": [
            {"task_id": "task_cardio", "activity_id": "act_cardio"},
            {"task_id": "task_cardio_missed", "activity_id": "act_cardio_missed"},
        ]
    }

    view_model = build_calendar_interface(
        calendar_rows,
        {"availability_blocks": []},
        traces,
        {},
        personalized_plan,
        {"providers": []},
        action_plan,
        member_profile,
    )

    recap = view_model["three_month_recap"]
    assert recap["horizon"]["week_count"] == 5
    assert recap["horizon"]["label"] == "1 months · 5 weeks"
    assert recap["totals"]["goal_count"] == 1
    assert recap["totals"]["at_risk"] == 1

    goal = recap["goals"][0]
    action = goal["actions"][0]
    assert goal["label"] == "Improve aerobic base"
    assert goal["status"] == "at_risk"
    assert action["horizon_target"] == 10
    assert action["scheduled"] == 1
    assert action["remaining"] == 9
    assert action["substitutions"] == 1
    assert action["blocked_instances"] == 1
    assert action["weeks_with_coverage"] == 1
    assert action["completion_percent"] == 10
    assert action["top_activities"] == [{"title": "Zone 2 bike", "count": 1}]


def test_three_month_recap_handles_weekly_and_three_month_goal_actions():
    weekly_actions = [
        {
            "goal_action_id": "ga_cardio_weekly",
            "goal_id": "goal_metabolic_health",
            "label": "Complete cardio",
            "target": {"period": "weekly", "units": 2, "unit_label": "sessions"},
            "support_only": False,
        },
        {
            "goal_action_id": "ga_clinical_review",
            "goal_id": "goal_metabolic_health",
            "label": "Complete clinical review package",
            "target": {"period": "3_month", "units": 1, "unit_label": "package"},
            "support_only": False,
        },
    ]
    activities = {
        "act_cardio": {
            "activity_id": "act_cardio",
            "goal_contributions": [{"goal_action_id": "ga_cardio_weekly", "value": 1}],
        },
        "act_review": {
            "activity_id": "act_review",
            "goal_contributions": [{"goal_action_id": "ga_clinical_review", "value": 1}],
        },
    }

    rows = recap_action_rows(
        calendar_rows=[
            {"calendar_row_id": "row_task_cardio", "date": "2026-06-01", "title": "Cardio"},
            {"calendar_row_id": "row_task_review", "date": "2026-06-08", "title": "Review"},
        ],
        traces=[],
        plan_tasks={
            "task_cardio": {"activity_id": "act_cardio"},
            "task_review": {"activity_id": "act_review"},
        },
        activities=activities,
        weekly_actions=weekly_actions,
        horizon_weeks=13,
    )

    targets = {row["goal_action_id"]: row["horizon_target"] for row in rows}
    assert targets["ga_cardio_weekly"] == 26
    assert targets["ga_clinical_review"] == 1


def test_calendar_interface_uses_period_aware_goal_actions_without_legacy_weekly_actions():
    member_profile = {
        "scheduling_rules": {
            "planning_start_date": "2026-06-01",
            "planning_months": 3,
        },
        "goals": [
            {
                "goal_id": "goal_clinical",
                "name": "Complete clinical baseline",
                "priority": 1,
            }
        ],
        "goal_actions": [
            {
                "goal_action_id": "ga_clinical_review",
                "goal_id": "goal_clinical",
                "label": "Complete clinical review package",
                "target": {"period": "3_month", "units": 1, "unit_label": "package"},
                "support_only": False,
            }
        ],
    }
    action_plan = {
        "activities": [
            {
                "activity_id": "act_review",
                "title": "Physician review",
                "goal_contributions": [
                    {
                        "goal_action_id": "ga_clinical_review",
                        "counts_toward_weekly_target": True,
                        "value": 1,
                    }
                ],
            }
        ]
    }
    calendar_rows = [
        {
            "calendar_row_id": "row_task_review",
            "date": "2026-06-08",
            "start_time": "09:00",
            "end_time": "09:45",
            "title": "Physician review",
            "activity_type": "consultation",
            "goal_tags": ["clinical"],
            "load_level": "low",
            "location_id": "clinic",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": "trace_review",
        }
    ]

    view_model = build_calendar_interface(
        calendar_rows,
        {"availability_blocks": []},
        [],
        {},
        {"tasks": [{"task_id": "task_review", "activity_id": "act_review"}]},
        {"providers": []},
        action_plan,
        member_profile,
    )

    action = view_model["three_month_recap"]["goals"][0]["actions"][0]
    assert action["goal_action_id"] == "ga_clinical_review"
    assert action["horizon_target"] == 1
    assert action["scheduled"] == 1


def test_weekly_goal_coverage_caps_target_progress_and_reports_extra_work():
    member_profile = {
        "weekly_goal_actions": [
            {
                "weekly_goal_action_id": "wga_cardio_sessions_001",
                "goal_id": "goal_cardio",
                "label": "Complete aerobic conditioning",
                "role": "core",
                "target_per_week": 2,
                "activity_types": ["fitness"],
                "required_meal_slots": [],
                "substitutions_allowed": True,
                "counts_substitutions": True,
                "support_only": False,
                "notes": "Zone 2 work counts directly.",
            }
        ]
    }
    action_plan = {
        "activities": [
            {
                "activity_id": f"act_cardio_{index}",
                "title": f"Zone 2 session {index}",
                "goal_contributions": [
                    {
                        "goal_id": "goal_cardio",
                        "weekly_goal_action_id": "wga_cardio_sessions_001",
                        "role": "core",
                        "counts_toward_weekly_target": True,
                        "unit": "activity",
                        "value": 1,
                    }
                ],
            }
            for index in range(1, 5)
        ]
    }
    calendar_rows = [
        {
            "calendar_row_id": f"row_task_cardio_{index}",
            "date": "2026-06-02",
            "start_time": f"0{index + 6}:00",
            "end_time": f"0{index + 6}:40",
            "title": f"Zone 2 session {index}",
            "activity_type": "fitness",
            "goal_tags": ["cardio"],
            "load_level": "medium",
            "location_id": "gym",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": f"trace_{index}",
        }
        for index in range(1, 5)
    ]
    personalized_plan = {
        "tasks": [
            {"task_id": f"task_cardio_{index}", "activity_id": f"act_cardio_{index}"}
            for index in range(1, 5)
        ]
    }

    view_model = build_calendar_interface(
        calendar_rows,
        {"availability_blocks": []},
        [],
        {},
        personalized_plan,
        {"providers": []},
        action_plan,
        member_profile,
    )

    coverage = view_model["weeks"][0]["goal_coverage"][0]
    assert coverage["scheduled"] == 2
    assert coverage["scheduled_total"] == 4
    assert coverage["extra_scheduled"] == 2
    assert coverage["status"] == "covered_with_extras"


def test_weekly_category_time_summarizes_five_activity_types():
    calendar_rows = [
        {
            "calendar_row_id": "row_task_fitness",
            "date": "2026-06-02",
            "start_time": "07:00",
            "end_time": "07:45",
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
            "calendar_row_id": "row_task_food",
            "date": "2026-06-02",
            "start_time": "08:00",
            "end_time": "08:20",
            "title": "Breakfast",
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
        calendar_rows,
        {"availability_blocks": []},
        [],
        {},
        {"tasks": []},
        {"providers": []},
        {"activities": []},
        {"weekly_goal_actions": []},
    )

    category_time = {
        item["category"]: item for item in view_model["weeks"][0]["category_time"]
    }
    assert category_time["fitness"]["minutes"] == 45
    assert category_time["fitness"]["activity_count"] == 1
    assert category_time["food"]["minutes"] == 20
    assert category_time["food"]["activity_count"] == 1
    assert category_time["consultation"]["minutes"] == 0
    assert set(category_time) == {"consultation", "fitness", "food", "medication", "therapy"}


def test_weekly_category_time_handles_cross_midnight_rows():
    calendar_rows = [
        {
            "calendar_row_id": "row_task_consult",
            "date": "2026-06-02",
            "start_time": "23:30",
            "end_time": "00:15",
            "title": "Late remote check-in",
            "activity_type": "consultation",
            "goal_tags": ["adherence"],
            "load_level": "low",
            "location_id": "remote",
            "mode": "remote",
            "substitution_status": "primary",
            "trace_id": "trace_1",
        }
    ]

    view_model = build_calendar_interface(
        calendar_rows,
        {"availability_blocks": []},
        [],
        {},
        {"tasks": []},
        {"providers": []},
        {"activities": []},
        {"weekly_goal_actions": []},
    )

    category_time = {
        item["category"]: item for item in view_model["weeks"][0]["category_time"]
    }
    assert category_time["consultation"]["minutes"] == 45


def test_weekly_category_time_excludes_passive_fasting_prep_blocks():
    calendar_rows = [
        {
            "calendar_row_id": "row_task_fasting",
            "date": "2026-06-02",
            "start_time": "21:00",
            "end_time": "07:00",
            "title": "Fasting prep block before blood panel",
            "activity_type": "consultation",
            "goal_tags": ["fasting_prep"],
            "load_level": "low",
            "location_id": "home",
            "mode": "in_person",
            "substitution_status": "primary",
            "trace_id": "trace_1",
        }
    ]
    action_plan = {
        "activities": [
            {
                "activity_id": "act_fasting",
                "title": "Fasting prep block before blood panel",
                "goal_tags": ["fasting_prep"],
            }
        ]
    }
    personalized_plan = {
        "tasks": [{"task_id": "task_fasting", "activity_id": "act_fasting"}]
    }

    view_model = build_calendar_interface(
        calendar_rows,
        {"availability_blocks": []},
        [],
        {},
        personalized_plan,
        {"providers": []},
        action_plan,
        {"weekly_goal_actions": []},
    )

    category_time = {
        item["category"]: item for item in view_model["weeks"][0]["category_time"]
    }
    assert category_time["consultation"]["minutes"] == 0
    assert category_time["consultation"]["activity_count"] == 0


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


def test_calendar_interface_exposes_wfh_location_band():
    availability = {
        "availability_blocks": [
            {
                "resource_id": "wfh_20260612",
                "resource_type": "member_location",
                "start": "2026-06-12T00:00:00+08:00",
                "end": "2026-06-13T00:00:00+08:00",
                "location_id": "home",
                "notes": "WFH day. Member location override: home.",
            }
        ]
    }

    view_model = build_calendar_interface(
        [], availability, [], {}, {"tasks": []}, {"providers": []}
    )

    week = view_model["weeks"][0]
    assert week["location_bands"][0]["label"] == "WFH day. Member location override: home."
    assert week["location_bands"][0]["resource_type"] == "member_location"
    assert week["location_bands"][0]["location_id"] == "home"


def test_calendar_interface_carries_travel_band_into_following_week():
    availability = {
        "availability_blocks": [
            {
                "resource_type": "member_travel",
                "start": "2026-06-05T15:00:00+08:00",
                "end": "2026-06-09T10:30:00+08:00",
                "location_id": "travel_hotel",
                "notes": "Tokyo planned travel.",
            },
        ]
    }

    view_model = build_calendar_interface(
        [], availability, [], {}, {"tasks": []}, {"providers": []}
    )

    first_week, second_week = view_model["weeks"]
    assert first_week["start_date"] == "2026-06-01"
    assert first_week["location_bands"][0]["start_day_index"] == 4
    assert first_week["location_bands"][0]["end_day_index"] == 6
    assert first_week["travel_blocks"][0]["day_index"] == 4
    assert first_week["travel_blocks"][0]["start_hour"] == 15

    assert second_week["start_date"] == "2026-06-08"
    assert second_week["location_bands"][0]["start_day_index"] == 0
    assert second_week["location_bands"][0]["end_day_index"] == 1
    assert second_week["travel_blocks"][0]["day_index"] == 0
    assert second_week["travel_blocks"][0]["start_hour"] == 0
    assert second_week["travel_blocks"][0]["duration_hours"] == 34.5


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
