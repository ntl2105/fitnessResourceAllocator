import re
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

from src.io_utils import load_json


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEMO_RUN_DIR = PROJECT_ROOT / "data" / "runs" / "demo-run"


def _demo_json(relative_path: str):
    return load_json(DEMO_RUN_DIR / relative_path)


def _reason_text(trace: dict) -> str:
    rejected_reasons = [
        reason
        for candidate in trace.get("rejected_candidates", [])
        for reason in candidate.get("reasons", [])
    ]
    check_reasons = [check.get("reason", "") for check in trace.get("constraint_checks", [])]
    return " ".join(rejected_reasons + check_reasons).lower()


def test_calendar_contains_remote_and_travel_adapted_rows_in_travel_windows():
    calendar_rows = _demo_json("04_calendar/calendar_rows.json")
    availability = _demo_json("00_inputs/availability.json")

    remote_rows = [row for row in calendar_rows if row.get("mode") == "remote"]
    travel_hotel_rows = [
        row for row in calendar_rows if row.get("location_id") == "travel_hotel"
    ]
    assert remote_rows
    assert travel_hotel_rows

    travel_windows = [
        (
            datetime.fromisoformat(block["start"]).date(),
            datetime.fromisoformat(block["end"]).date(),
        )
        for block in availability["availability_blocks"]
        if block.get("resource_type") == "member_travel"
    ]
    assert travel_windows
    assert any(
        row.get("location_id") == "travel_hotel"
        and any(start <= datetime.fromisoformat(row["date"]).date() <= end for start, end in travel_windows)
        for row in calendar_rows
    )


def test_travel_specific_calendar_rows_only_appear_during_travel_windows():
    calendar_rows = _demo_json("04_calendar/calendar_rows.json")
    availability = _demo_json("00_inputs/availability.json")
    traces = _demo_json("03_scheduling/decision_traces.json")
    action_plan = _demo_json("00_inputs/action_plan.json")

    trace_activity_ids = {trace["trace_id"]: trace["activity_id"] for trace in traces}
    activities = {activity["activity_id"]: activity for activity in action_plan["activities"]}
    travel_windows = [
        (
            datetime.fromisoformat(block["start"]).date(),
            datetime.fromisoformat(block["end"]).date(),
        )
        for block in availability["availability_blocks"]
        if block.get("resource_type") == "member_travel"
    ]

    violations = []
    for row in calendar_rows:
        activity = activities.get(trace_activity_ids.get(row["trace_id"]), {})
        title = activity.get("title", "").lower()
        allowed_locations = set(activity.get("allowed_locations", []))
        goal_tags = {tag.lower() for tag in activity.get("goal_tags", [])}
        is_travel_specific = "travel-compatible" in title or (
            "travel" in goal_tags and allowed_locations.issubset({"remote", "travel_hotel"})
        )
        row_date = datetime.fromisoformat(row["date"]).date()
        if is_travel_specific and not any(start <= row_date <= end for start, end in travel_windows):
            violations.append(row)

    assert not violations


def test_decision_traces_explain_rejections_and_include_handoff_summaries():
    traces = _demo_json("03_scheduling/decision_traces.json")

    traces_with_rejections = [
        trace for trace in traces if trace.get("rejected_candidates")
    ]
    assert traces_with_rejections
    assert any(
        any(check.get("passed") is False and check.get("reason") for check in trace["constraint_checks"])
        for trace in traces_with_rejections
    )
    assert all(
        candidate.get("reasons")
        for trace in traces_with_rejections
        for candidate in trace["rejected_candidates"]
    )

    handoff_traces = [
        trace for trace in traces if trace.get("provider_handoff_summary")
    ]
    assert handoff_traces
    assert any(trace.get("final_status") == "scheduled" for trace in handoff_traces)
    assert any(trace.get("final_status") == "unscheduled" for trace in handoff_traces)
    assert all("Share care context" in trace["provider_handoff_summary"] for trace in handoff_traces)


def test_synthetic_quality_report_contains_expected_sections_and_counts():
    report_path = DEMO_RUN_DIR / "00_inputs" / "synthetic_data_quality_report.md"
    report = report_path.read_text(encoding="utf-8")
    action_plan = _demo_json("00_inputs/action_plan.json")

    activity_count = len(action_plan["activities"])
    primary_count = sum(1 for activity in action_plan["activities"] if activity["is_primary"])

    assert report.startswith("# Synthetic Data Quality Report")
    assert "Status: pass" in report
    assert "## Validation Checks" in report
    assert f"Activities: {activity_count}" in report
    assert f"Primary activities: {primary_count}" in report
    assert "Modalities: consultation, fitness, food, medication, therapy" in report
    assert len(re.findall(r"^- PASS:", report, flags=re.MULTILINE)) >= 10


def test_traces_capture_member_travel_and_travel_time_buffer_rejections():
    traces = _demo_json("03_scheduling/decision_traces.json")

    assert any(
        any(
            candidate.get("location_id") != "travel_hotel"
            and "member travel" in " ".join(candidate.get("reasons", [])).lower()
            for candidate in trace.get("rejected_candidates", [])
        )
        for trace in traces
    )
    assert any(
        "requires" in reason
        and "minutes" in reason
        for trace in traces
        for candidate in trace.get("rejected_candidates", [])
        for reason in candidate.get("reasons", [])
    )


def test_calendar_contains_scheduled_substitutions():
    calendar_rows = _demo_json("04_calendar/calendar_rows.json")

    assert any(row.get("substitution_status") == "substitution" for row in calendar_rows)


def test_latest_calendar_has_high_touch_consultations():
    calendar_rows = _demo_json("04_calendar/calendar_rows.json")
    consultations = [row for row in calendar_rows if row["activity_type"] == "consultation"]

    assert len(consultations) >= 10


def test_latest_calendar_has_specialist_and_allied_health_consultation_mix():
    plan = _demo_json("03_scheduling/personalized_plan.json")
    resource_universe = _demo_json("00_inputs/resource_universe.json")
    providers = {
        provider["provider_id"]: provider
        for provider in resource_universe["providers"]
    }
    consultations = [
        task for task in plan["tasks"] if task["activity_type"] == "consultation"
    ]
    provider_types = Counter(
        providers[provider_id]["provider_type"]
        for task in consultations
        for provider_id in task.get("provider_ids", [])
        if provider_id in providers
    )

    assert len(consultations) >= 24
    assert provider_types["physician"] >= 2
    assert provider_types["physiotherapist"] >= 2
    assert provider_types["dietitian"] >= 3


def test_latest_calendar_spreads_consultations_after_due_week():
    plan = _demo_json("03_scheduling/personalized_plan.json")
    consultations_by_week: dict[str, int] = {}
    for task in plan["tasks"]:
        if task["activity_type"] != "consultation":
            continue
        task_start = datetime.fromisoformat(task["start"])
        week = f"{task_start.isocalendar().year}-W{task_start.isocalendar().week:02d}"
        consultations_by_week[week] = consultations_by_week.get(week, 0) + 1

    assert consultations_by_week["2026-W23"] <= 4
    assert all(
        count <= 3
        for week, count in consultations_by_week.items()
        if week != "2026-W23"
    )


def test_latest_schedule_uses_expanded_trainer_provider_universe():
    plan = _demo_json("03_scheduling/personalized_plan.json")
    scheduled_provider_ids = {
        provider_id
        for task in plan["tasks"]
        for provider_id in task.get("provider_ids", [])
    }

    assert "provider_trainer_01" in scheduled_provider_ids
    assert "provider_physio_01" in scheduled_provider_ids


def test_latest_schedule_slots_every_daily_meal_at_member_location():
    plan = _demo_json("03_scheduling/personalized_plan.json")
    availability = _demo_json("00_inputs/availability.json")
    action_plan = _demo_json("00_inputs/action_plan.json")
    activity_by_id = {activity["activity_id"]: activity for activity in action_plan["activities"]}

    start = date.fromisoformat(availability["planning_start_date"])
    month_index = start.month - 1 + int(availability["planning_months"])
    end = date(start.year + month_index // 12, month_index % 12 + 1, 1)
    expected_slots = {"breakfast", "lunch", "dinner"}
    slots_by_date: dict[date, set[str]] = {}

    for task in plan["tasks"]:
        activity = activity_by_id.get(task["activity_id"], {})
        meal_slot = activity.get("meal_slot")
        if meal_slot in expected_slots:
            task_date = datetime.fromisoformat(task["start"]).date()
            slots_by_date.setdefault(task_date, set()).add(meal_slot)

    missing = {}
    current = start
    while current < end:
        absent = expected_slots - slots_by_date.get(current, set())
        if absent:
            missing[current.isoformat()] = sorted(absent)
        current += timedelta(days=1)

    assert not missing

    travel_windows = [
        (
            datetime.fromisoformat(block["start"]),
            datetime.fromisoformat(block["end"]),
        )
        for block in availability["availability_blocks"]
        if block.get("resource_type") == "member_travel"
    ]
    offsite_meals = []
    for task in plan["tasks"]:
        activity = activity_by_id.get(task["activity_id"], {})
        if activity.get("meal_slot") not in expected_slots:
            continue
        task_start = datetime.fromisoformat(task["start"])
        if any(start <= task_start <= end for start, end in travel_windows):
            if task.get("location_id") != "travel_hotel":
                offsite_meals.append(task)

    assert not offsite_meals


def test_latest_schedule_has_daily_medications_and_weekday_fitness_distribution():
    plan = _demo_json("03_scheduling/personalized_plan.json")
    availability = _demo_json("00_inputs/availability.json")
    action_plan = _demo_json("00_inputs/action_plan.json")
    activity_by_id = {activity["activity_id"]: activity for activity in action_plan["activities"]}

    start = date.fromisoformat(availability["planning_start_date"])
    month_index = start.month - 1 + int(availability["planning_months"])
    end = date(start.year + month_index // 12, month_index % 12 + 1, 1)

    daily_medication_dates = {
        datetime.fromisoformat(task["start"]).date()
        for task in plan["tasks"]
        if activity_by_id.get(task["activity_id"], {}).get("activity_type") == "medication"
        and activity_by_id.get(task["activity_id"], {}).get("frequency", {}).get("type") == "daily"
    }
    missing_medication_dates = []
    current = start
    while current < end:
        if current not in daily_medication_dates:
            missing_medication_dates.append(current.isoformat())
        current += timedelta(days=1)

    weekday_fitness_count = sum(
        1
        for task in plan["tasks"]
        if activity_by_id.get(task["activity_id"], {}).get("activity_type") == "fitness"
        and datetime.fromisoformat(task["start"]).date().weekday() < 5
    )

    assert not missing_medication_dates
    assert weekday_fitness_count >= 20


def test_latest_schedule_has_evening_fitness_and_weekend_variety():
    calendar_rows = _demo_json("04_calendar/calendar_rows.json")
    fitness_rows = [row for row in calendar_rows if row["activity_type"] == "fitness"]

    evening_rows = [
        row
        for row in fitness_rows
        if int(row["start_time"].split(":", maxsplit=1)[0]) >= 18
    ]
    weekend_titles = {
        row["title"]
        for row in fitness_rows
        if datetime.fromisoformat(row["date"]).date().weekday() >= 5
    }

    assert len(evening_rows) >= 4
    assert len(weekend_titles) >= 2
    assert all(row["end_time"] <= "20:30" for row in fitness_rows if row["load_level"] != "low")


def test_latest_schedule_avoids_back_to_back_same_provider_consultations():
    plan = _demo_json("03_scheduling/personalized_plan.json")
    consultations = sorted(
        [
            task
            for task in plan["tasks"]
            if task["activity_type"] == "consultation" and task.get("provider_ids")
        ],
        key=lambda task: task["start"],
    )
    violations = []
    for earlier, later in zip(consultations, consultations[1:]):
        shared_providers = set(earlier.get("provider_ids", [])) & set(
            later.get("provider_ids", [])
        )
        if not shared_providers:
            continue
        earlier_end = datetime.fromisoformat(earlier["end"])
        later_start = datetime.fromisoformat(later["start"])
        if earlier_end.date() == later_start.date() and later_start < earlier_end + timedelta(minutes=30):
            violations.append((earlier["title"], later["title"], sorted(shared_providers)))

    assert not violations


def test_latest_schedule_avoids_multiple_fitness_sessions_same_day():
    plan = _demo_json("03_scheduling/personalized_plan.json")
    fitness_by_date: dict[date, list[str]] = {}
    for task in plan["tasks"]:
        if task["activity_type"] != "fitness":
            continue
        task_date = datetime.fromisoformat(task["start"]).date()
        fitness_by_date.setdefault(task_date, []).append(task["title"])

    violations = {
        task_date.isoformat(): titles
        for task_date, titles in fitness_by_date.items()
        if len(titles) > 1
    }

    assert not violations


def test_latest_schedule_has_occasional_fitness_unavailability_and_replacements():
    plan = _demo_json("03_scheduling/personalized_plan.json")
    availability = _demo_json("00_inputs/availability.json")
    replacement_dates = {
        date(2026, 6, 11): date(2026, 6, 12),
        date(2026, 7, 9): date(2026, 7, 10),
        date(2026, 8, 20): date(2026, 8, 21),
    }
    occasional_blocks = [
        block
        for block in availability["availability_blocks"]
        if "Occasional member conflict during planned fitness slot" in block.get("notes", "")
    ]

    assert {
        datetime.fromisoformat(block["start"]).date()
        for block in occasional_blocks
    } == set(replacement_dates)

    rows = _demo_json("04_calendar/calendar_rows.json")
    for block in occasional_blocks:
        block_start = datetime.fromisoformat(block["start"])
        block_end = datetime.fromisoformat(block["end"])
        assert not [
            row
            for row in rows
            if row["activity_type"] == "fitness"
            and datetime.fromisoformat(f"{row['date']}T{row['start_time']}:00+08:00") < block_end
            and datetime.fromisoformat(f"{row['date']}T{row['end_time']}:00+08:00") > block_start
        ]


def test_latest_schedule_respects_hard_member_location_and_load_constraints():
    rows = _demo_json("04_calendar/calendar_rows.json")

    sunday_family_violations = []
    wfh_office_violations = []
    hk_fatigue_violations = []
    for row in rows:
        row_date = datetime.fromisoformat(row["date"]).date()
        row_start = datetime.fromisoformat(f"{row['date']}T{row['start_time']}:00+08:00")
        row_end = datetime.fromisoformat(f"{row['date']}T{row['end_time']}:00+08:00")
        if (
            row_date.weekday() == 6
            and row["start_time"] < "13:00"
            and row["end_time"] > "09:00"
            and row["activity_type"] != "food"
        ):
            sunday_family_violations.append(row)
        if row["date"] == "2026-08-07" and row.get("location_id") == "office":
            wfh_office_violations.append(row)
        if (
            row_start < datetime.fromisoformat("2026-06-20T10:00:00+08:00")
            and row_end > datetime.fromisoformat("2026-06-19T14:00:00+08:00")
            and row["activity_type"] in {"fitness", "therapy"}
            and row.get("load_level") != "low"
        ):
            hk_fatigue_violations.append(row)

    assert not sunday_family_violations
    assert not wfh_office_violations
    assert not hk_fatigue_violations


def test_latest_schedule_has_weekly_validation_and_mode_semantics():
    plan = _demo_json("03_scheduling/personalized_plan.json")
    rows = _demo_json("04_calendar/calendar_rows.json")
    report = plan["goal_report"]
    validations = report["weekly_validation"]
    check_ids = {item["check_id"] for item in validations}

    assert {
        "countable_structured_meals_target",
        "member_assembled_meals_cap",
        "chef_prep_sessions_cap",
        "aerobic_sessions_target",
        "strength_sessions_target",
        "recovery_actions_target",
    }.issubset(check_ids)
    assert all(
        item["actual_units"] <= 14
        for item in validations
        if item["check_id"] == "countable_structured_meals_target"
    )
    assert all(
        item["actual_units"] <= 2
        for item in validations
        if item["check_id"] == "member_assembled_meals_cap"
    )
    assert all(
        item["actual_units"] <= 2
        for item in validations
        if item["check_id"] == "chef_prep_sessions_cap"
    )
    assert not [
        row
        for row in rows
        if row["activity_type"] == "medication" and row.get("mode") == "remote"
    ]
    assert not [row for row in rows if "pain escalation" in row["title"].lower()]


def test_tokyo_travel_strength_prefers_hotel_gym_before_in_room_fallback():
    plan = _demo_json("03_scheduling/personalized_plan.json")
    tokyo_strength = [
        task
        for task in plan["tasks"]
        if task["activity_type"] == "fitness"
        and task["start"].startswith("2026-07-28")
        and "strength" in task["title"].lower()
    ]

    assert not any(
        task["activity_id"] == "act_b03_strength_home_strength_travel"
        for task in tokyo_strength
    )


def test_tokyo_travel_aerobic_prefers_hotel_gym_before_low_resource_fallbacks():
    plan = _demo_json("03_scheduling/personalized_plan.json")
    tokyo_aerobic = [
        task
        for task in plan["tasks"]
        if task["activity_type"] == "fitness"
        and "2026-07-22" <= task["start"][:10] <= "2026-07-29"
        and any(tag in task.get("goal_tags", []) for tag in ["aerobic_conditioning", "walking"])
    ]

    assert any(
        task["activity_id"] == "act_b02_cardio_zone2_travel_hotel_gym_primary"
        for task in tokyo_aerobic
    )
    assert not any(
        task["activity_id"]
        in {
            "act_b02_cardio_facility_unavailable_cardio_substitution_walk_sub",
            "act_b02_cardio_zone2_travel_bodyweight_primary",
            "act_b02_cardio_zone2_travel_bodyweight_walk_sub",
        }
        for task in tokyo_aerobic
    )


def test_travel_weeks_prioritize_fatigue_reduction_therapy():
    plan = _demo_json("03_scheduling/personalized_plan.json")
    availability = _demo_json("00_inputs/availability.json")
    travel_weeks = {
        f"{start.isocalendar().year}-W{start.isocalendar().week:02d}"
        for block in availability["availability_blocks"]
        if block.get("resource_type") == "member_travel"
        for start in [datetime.fromisoformat(block["start"]).date()]
    }

    therapy_by_week: dict[str, list[dict]] = {}
    travel_hotel_therapy_by_week: dict[str, list[dict]] = {}
    for task in plan["tasks"]:
        if task["activity_type"] != "therapy":
            continue
        task_date = datetime.fromisoformat(task["start"]).date()
        week = f"{task_date.isocalendar().year}-W{task_date.isocalendar().week:02d}"
        therapy_by_week.setdefault(week, []).append(task)
        if task.get("location_id") == "travel_hotel":
            travel_hotel_therapy_by_week.setdefault(week, []).append(task)

    assert all(len(therapy_by_week.get(week, [])) >= 4 for week in travel_weeks)
    assert all(len(travel_hotel_therapy_by_week.get(week, [])) >= 2 for week in travel_weeks)


def test_latest_schedule_caps_member_assembled_meals_and_avoids_travel_location_leaks():
    plan = _demo_json("03_scheduling/personalized_plan.json")
    availability = _demo_json("00_inputs/availability.json")
    action_plan = _demo_json("00_inputs/action_plan.json")
    activity_by_id = {activity["activity_id"]: activity for activity in action_plan["activities"]}
    member_assembled_by_week: dict[str, int] = {}
    travel_windows = [
        (
            datetime.fromisoformat(block["start"]),
            datetime.fromisoformat(block["end"]),
        )
        for block in availability["availability_blocks"]
        if block.get("resource_type") == "member_travel"
    ]
    location_leaks = []

    for task in plan["tasks"]:
        activity = activity_by_id.get(task["activity_id"], {})
        task_start = datetime.fromisoformat(task["start"])
        if activity.get("activity_type") == "food" and activity.get("prep_source") == "member_assembled":
            week = f"{task_start.isocalendar().year}-W{task_start.isocalendar().week:02d}"
            member_assembled_by_week[week] = member_assembled_by_week.get(week, 0) + 1
        if any(start <= task_start < end for start, end in travel_windows):
            if task.get("location_id") in {"home", "office", "gym", "restaurant"}:
                location_leaks.append(
                    (task["start"], task.get("location_id"), task["title"])
                )

    assert all(count <= 2 for count in member_assembled_by_week.values())
    assert not location_leaks


def test_rejection_summary_aggregates_unscheduled_and_rejected_candidate_counts():
    traces = _demo_json("03_scheduling/decision_traces.json")
    rejection_summary = _demo_json("03_scheduling/rejection_summary.json")

    expected = {}
    for trace in traces:
        if trace.get("final_status") != "unscheduled":
            continue
        activity_summary = expected.setdefault(
            trace["activity_id"],
            {"unscheduled_count": 0, "rejected_candidate_count": 0},
        )
        activity_summary["unscheduled_count"] += 1
        activity_summary["rejected_candidate_count"] += len(trace.get("rejected_candidates", []))

    assert expected
    assert rejection_summary == expected
