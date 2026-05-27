from datetime import date, datetime, timedelta, timezone

from src.models.availability import AvailabilityBlock, AvailabilityData
from src.models.schedule import ScheduledTask, TaskInstance
from src.scheduler.availability import check_required_resources
from src.scheduler.engine import schedule_tasks
from src.scheduler.placement import candidate_slots
from src.scheduler.policy import evaluate_policy


UTC = timezone.utc


def _task(
    activity_id: str,
    *,
    priority: int = 1,
    target_date: date = date(2026, 6, 1),
    resources: dict | None = None,
    dependencies: list | None = None,
) -> TaskInstance:
    return TaskInstance(
        task_instance_id=f"task_{activity_id}",
        activity_id=activity_id,
        activity_family_id=f"fam_{activity_id}",
        is_substitution=False,
        target_date=target_date,
        target_week=f"{target_date.isocalendar().year}-W{target_date.isocalendar().week:02d}",
        duration_minutes=30,
        priority=priority,
        goal_tags=["goal"],
        required_resources=resources or {},
        dependencies=dependencies or [],
        status="pending",
    )


def test_availability_requires_each_resource_to_cover_candidate_slot():
    task = _task(
        "needs_provider",
        resources={"provider_ids": ["provider_1"], "equipment_ids": [], "location_ids": []},
    )
    start = datetime(2026, 6, 1, 9, tzinfo=UTC)
    end = start + timedelta(minutes=30)
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[
            AvailabilityBlock(
                resource_id="provider_1",
                resource_type="provider",
                start=start,
                end=end,
                timezone="UTC",
            )
        ],
    )

    passed, checks = check_required_resources(task, start, end, availability)

    assert passed is True
    assert checks[0].name == "resource_available:provider_1"
    assert checks[0].passed is True


def test_availability_checks_physical_location_but_not_remote_location():
    start = datetime(2026, 6, 1, 9, tzinfo=UTC)
    end = start + timedelta(minutes=30)
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[
            AvailabilityBlock(
                resource_id="clinic",
                resource_type="location",
                start=start,
                end=end,
                timezone="UTC",
                location_id="clinic",
            )
        ],
    )
    physical_task = _task("physical", resources={"location_ids": ["lab"]})
    remote_task = _task("remote", resources={"location_ids": ["remote"]})

    physical_passed, physical_checks = check_required_resources(
        physical_task, start, end, availability
    )
    remote_passed, remote_checks = check_required_resources(remote_task, start, end, availability)

    assert physical_passed is False
    assert physical_checks[0].name == "location_available:lab"
    assert "No availability block covers physical location lab" in physical_checks[0].reason
    assert remote_passed is True
    assert remote_checks[0].name == "location_available:remote"
    assert "Remote location does not require" in remote_checks[0].reason


def test_home_and_office_locations_do_not_require_facility_availability_blocks():
    start = datetime(2026, 6, 1, 9, tzinfo=UTC)
    end = start + timedelta(minutes=30)
    availability = AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1)
    home_task = _task("home", resources={"location_ids": ["home"]})
    office_task = _task("office", resources={"location_ids": ["office"]})

    home_passed, home_checks = check_required_resources(home_task, start, end, availability)
    office_passed, office_checks = check_required_resources(office_task, start, end, availability)

    assert home_passed is True
    assert home_checks[0].name == "location_available:home"
    assert "member-context location" in home_checks[0].reason
    assert office_passed is True
    assert office_checks[0].name == "location_available:office"
    assert "member-context location" in office_checks[0].reason


def test_policy_rejects_standalone_movement_blocks_too_close_together():
    task = _task("stretch", resources={"location_ids": ["home"]})
    start = datetime(2026, 6, 1, 19, 15, tzinfo=UTC)
    end = start + timedelta(minutes=20)
    scheduled = ScheduledTask(
        task_id="task_cardio",
        activity_id="cardio",
        title="Seated band aerobic session",
        start=datetime(2026, 6, 1, 18, 45, tzinfo=UTC),
        end=datetime(2026, 6, 1, 19, 5, tzinfo=UTC),
        activity_type="fitness",
        load_level="medium",
        status="scheduled",
    )

    passed, checks = evaluate_policy(
        task,
        start,
        end,
        [scheduled],
        activity={
            "activity_id": "stretch",
            "activity_type": "therapy",
            "title": "Short evening stretch routine",
            "load_level": "low",
        },
        candidate_location_id="home",
    )

    movement_check = next(check for check in checks if check.name == "movement_spacing")
    assert passed is False
    assert movement_check.passed is False
    assert "90 minutes" in movement_check.reason


def test_candidate_slots_cover_all_allowed_locations():
    task = _task(
        "multi_location",
        resources={"location_ids": ["home", "travel_hotel"]},
    )
    availability = AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1)
    activity = {
        "activity_id": "multi_location",
        "allowed_locations": ["home", "travel_hotel"],
        "frequency": {"preferred_time_windows": ["09:00-10:00"]},
    }

    slots = candidate_slots(task, activity, availability)

    first_day_slots = [slot for slot in slots if slot["start"].date() == date(2026, 6, 1)]
    assert {slot["location_id"] for slot in first_day_slots} == {"home", "travel_hotel"}


def test_remote_titled_activity_only_uses_remote_location():
    task = _task(
        "remote_strength",
        resources={"location_ids": ["home", "remote", "travel_hotel"]},
    )
    activity = {
        "activity_id": "remote_strength",
        "title": "Remote trainer-led strength session",
        "allowed_locations": ["home", "remote", "travel_hotel"],
        "frequency": {"preferred_time_windows": ["11:00-12:00"]},
    }

    slots = candidate_slots(
        task,
        activity,
        AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1),
    )

    assert {slot["location_id"] for slot in slots} == {"remote"}


def test_candidate_slots_stop_before_planning_horizon_end():
    task = _task(
        "near_horizon",
        target_date=date(2026, 8, 30),
        resources={"location_ids": ["home"]},
    )
    availability = AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=3)

    slots = candidate_slots(task, {"activity_id": "near_horizon"}, availability)

    assert slots
    assert max(slot["start"].date() for slot in slots) < date(2026, 9, 1)


def test_scheduler_falls_back_to_later_allowed_location_when_first_is_unavailable():
    start = datetime(2026, 6, 1, 9, tzinfo=UTC)
    task = _task(
        "fallback_location",
        resources={"location_ids": ["lab", "travel_hotel"]},
    )
    activity = {
        "activity_id": "fallback_location",
        "title": "Location fallback session",
        "activity_type": "consultation",
        "load_level": "low",
        "allowed_locations": ["lab", "travel_hotel"],
        "frequency": {"preferred_time_windows": ["09:00-10:00"]},
    }
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[
            AvailabilityBlock(
                resource_id="travel_hotel",
                resource_type="location",
                start=start,
                end=start + timedelta(hours=1),
                timezone="UTC",
                location_id="travel_hotel",
            )
        ],
    )

    result = schedule_tasks([task], {"fallback_location": activity}, availability)

    assert len(result.plan.tasks) == 1
    assert result.plan.tasks[0].location_id == "travel_hotel"
    trace = result.traces[0]
    assert trace.selected_slot["location_id"] == "travel_hotel"
    assert trace.rejected_candidates[0]["location_id"] == "lab"
    assert any("physical location lab" in reason for reason in trace.rejected_candidates[0]["reasons"])


def test_member_blocked_rejects_overlapping_candidate():
    start = datetime(2026, 6, 1, 9, tzinfo=UTC)
    task = _task("blocked", resources={"location_ids": ["home"]})
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[
            AvailabilityBlock(
                resource_id="member_1",
                resource_type="member_blocked",
                start=start,
                end=start + timedelta(hours=1),
                timezone="UTC",
                location_id="office",
                notes="Work block.",
            )
        ],
    )

    passed, checks = evaluate_policy(
        task,
        start,
        start + timedelta(minutes=30),
        [],
        dependency_state={"availability": availability},
        candidate_location_id="home",
    )

    assert passed is False
    member_check = next(check for check in checks if check.name == "member_availability")
    assert "Member blocked by Work block." in member_check.reason


def test_low_load_office_movement_allowed_during_work_block():
    start = datetime(2026, 6, 1, 10, 30, tzinfo=UTC)
    task = _task("office_walk", resources={"location_ids": ["office"]})
    task.duration_minutes = 10
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[
            AvailabilityBlock(
                resource_id="member_1",
                resource_type="member_blocked",
                start=datetime(2026, 6, 1, 8, 30, tzinfo=UTC),
                end=datetime(2026, 6, 1, 18, 30, tzinfo=UTC),
                timezone="UTC",
                location_id="office",
                notes=(
                    "Core work hours; member unavailable for healthspan activities "
                    "except low-complexity remote/office/home tasks."
                ),
            )
        ],
    )

    passed, checks = evaluate_policy(
        task,
        start,
        start + timedelta(minutes=10),
        [],
        activity={
            "activity_id": "office_walk",
            "activity_type": "fitness",
            "title": "Office walking break",
            "load_level": "low",
            "duration_minutes": 10,
            "facilitator_type": "member",
        },
        dependency_state={"availability": availability},
        candidate_location_id="office",
    )

    assert passed is True
    assert next(check for check in checks if check.name == "member_availability").passed is True


def test_member_travel_rejects_non_travel_physical_location():
    start = datetime(2026, 6, 10, 9, tzinfo=UTC)
    task = _task("travel", resources={"location_ids": ["gym", "travel_hotel"]})
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[
            AvailabilityBlock(
                resource_id="member_1",
                resource_type="member_travel",
                start=start - timedelta(hours=1),
                end=start + timedelta(hours=1),
                timezone="UTC",
                location_id="travel_hotel",
                notes="Travel window.",
            )
        ],
    )

    failed, failed_checks = evaluate_policy(
        task,
        start,
        start + timedelta(minutes=30),
        [],
        activity={"allowed_locations": ["gym", "travel_hotel"]},
        dependency_state={"availability": availability},
        candidate_location_id="gym",
    )
    passed, passed_checks = evaluate_policy(
        task,
        start,
        start + timedelta(minutes=30),
        [],
        activity={"allowed_locations": ["gym", "travel_hotel"]},
        dependency_state={"availability": availability},
        candidate_location_id="travel_hotel",
    )

    assert failed is False
    assert "member travel" in next(
        check for check in failed_checks if check.name == "member_travel_location"
    ).reason
    assert passed is True
    assert next(
        check for check in passed_checks if check.name == "member_travel_location"
    ).passed is True


def test_travel_specific_remote_activity_requires_active_travel_window():
    start = datetime(2026, 6, 10, 9, tzinfo=UTC)
    task = _task("travel_meal", resources={"location_ids": ["remote"]})
    activity = {
        "activity_id": "act_travel_restaurant_meal",
        "title": "Travel-compatible restaurant meal",
        "goal_tags": ["travel"],
        "allowed_locations": ["remote", "travel_hotel"],
    }
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[
            AvailabilityBlock(
                resource_id="member_1",
                resource_type="member_travel",
                start=start + timedelta(days=2),
                end=start + timedelta(days=3),
                timezone="UTC",
                location_id="travel_hotel",
                notes="Future travel window.",
            )
        ],
    )

    failed, failed_checks = evaluate_policy(
        task,
        start,
        start + timedelta(minutes=30),
        [],
        activity=activity,
        dependency_state={"availability": availability},
        candidate_location_id="remote",
    )
    passed, passed_checks = evaluate_policy(
        task,
        start + timedelta(days=2, hours=1),
        start + timedelta(days=2, hours=1, minutes=30),
        [],
        activity=activity,
        dependency_state={"availability": availability},
        candidate_location_id="remote",
    )

    assert failed is False
    assert "active travel window" in next(
        check for check in failed_checks if check.name == "active_travel_required"
    ).reason
    assert passed is True
    assert next(
        check for check in passed_checks if check.name == "active_travel_required"
    ).passed is True


def test_food_task_dependency_requires_nearby_same_day_meal():
    breakfast_start = datetime(2026, 6, 10, 7, tzinfo=UTC)
    breakfast = ScheduledTask(
        task_id="task_breakfast",
        activity_id="act_breakfast",
        activity_family_id="fam_breakfast",
        title="High-protein breakfast",
        goal_tags=["breakfast", "structured_meal"],
        start=breakfast_start,
        end=breakfast_start + timedelta(minutes=20),
        location_id="home",
        provider_ids=[],
        equipment_ids=[],
        status="scheduled",
        trace_id="trace_breakfast",
    )
    supplement_task = _task(
        "supplement",
        resources={"location_ids": ["home"]},
        dependencies=[
            {
                "type": "food_task",
                "meal_slot": "breakfast",
                "offset_minutes_max": 30,
            }
        ],
    )

    failed, failed_checks = evaluate_policy(
        supplement_task,
        breakfast_start + timedelta(hours=1),
        breakfast_start + timedelta(hours=1, minutes=5),
        [breakfast],
        candidate_location_id="home",
    )
    passed, passed_checks = evaluate_policy(
        supplement_task,
        breakfast_start + timedelta(minutes=30),
        breakfast_start + timedelta(minutes=35),
        [breakfast],
        candidate_location_id="home",
    )

    assert failed is False
    assert "same-day breakfast" in next(
        check for check in failed_checks if check.name == "dependency:food_task"
    ).reason
    assert passed is True
    assert next(
        check for check in passed_checks if check.name == "dependency:food_task"
    ).passed is True


def test_scheduler_allows_only_one_meal_slot_per_day():
    start_date = date(2026, 6, 1)
    task_one = _task("breakfast_one", target_date=start_date, resources={"location_ids": ["home"]})
    task_two = _task("breakfast_two", target_date=start_date, resources={"location_ids": ["home"]})
    activities = {
        "breakfast_one": {
            "activity_id": "breakfast_one",
            "title": "High-protein breakfast",
            "activity_type": "food",
            "meal_slot": "breakfast",
            "load_level": "low",
            "allowed_locations": ["home"],
            "frequency": {"preferred_time_windows": ["07:00-08:00"]},
        },
        "breakfast_two": {
            "activity_id": "breakfast_two",
            "title": "Weekend structured breakfast",
            "activity_type": "food",
            "meal_slot": "breakfast",
            "load_level": "low",
            "allowed_locations": ["home"],
            "frequency": {"preferred_time_windows": ["08:00-09:00"]},
        },
    }

    result = schedule_tasks(
        [task_one, task_two],
        activities,
        AvailabilityData(planning_start_date=start_date, planning_months=1),
    )

    assert len(result.calendar_rows) == 1
    blocked_trace = next(trace for trace in result.traces if trace.final_status == "unscheduled")
    assert any(
        "already covers breakfast" in reason
        for candidate in blocked_trace.rejected_candidates
        for reason in candidate["reasons"]
    )


def test_food_tasks_do_not_drift_off_target_date():
    target_date = date(2026, 6, 6)
    task = _task("weekend_breakfast", target_date=target_date, resources={"location_ids": ["home"]})
    activity = {
        "activity_id": "weekend_breakfast",
        "title": "Weekend structured breakfast",
        "activity_type": "food",
        "meal_slot": "breakfast",
        "load_level": "low",
        "allowed_locations": ["home"],
        "frequency": {"preferred_time_windows": ["08:00-09:00"]},
    }
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[
            AvailabilityBlock(
                resource_id="member",
                resource_type="member_blocked",
                start=datetime(2026, 6, 6, 0, tzinfo=UTC),
                end=datetime(2026, 6, 7, 0, tzinfo=UTC),
                timezone="UTC",
                location_id="home",
                notes="Target day blocked.",
            )
        ],
    )

    result = schedule_tasks([task], {"weekend_breakfast": activity}, availability)

    assert result.calendar_rows == []
    assert result.traces[0].final_status == "unscheduled"
    rejected_dates = {
        candidate["start"][:10] for candidate in result.traces[0].rejected_candidates
    }
    assert rejected_dates == {"2026-06-06"}


def test_fitness_tasks_can_use_target_date_or_next_day_only():
    target_date = date(2026, 6, 6)
    task = _task("fitness", target_date=target_date, resources={"location_ids": ["home"]})
    availability = AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1)

    slots = candidate_slots(
        task,
        {
            "activity_id": "fitness",
            "activity_type": "fitness",
            "allowed_locations": ["home"],
            "frequency": {"preferred_time_windows": ["18:45-20:00"]},
        },
        availability,
    )

    assert {slot["start"].date() for slot in slots} == {
        target_date,
        target_date + timedelta(days=1),
    }
    next_day_slots = [
        slot for slot in slots if slot["start"].date() == target_date + timedelta(days=1)
    ]
    assert next_day_slots[0]["start"].strftime("%H:%M") == "18:45"


def test_travel_time_buffer_rejects_office_to_gym_gap_under_rule():
    office_end = datetime(2026, 6, 1, 18, 30, tzinfo=UTC)
    task = _task("gym", resources={"location_ids": ["gym"]})
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[
            AvailabilityBlock(
                resource_id="member_1",
                resource_type="member_blocked",
                start=office_end - timedelta(hours=8),
                end=office_end,
                timezone="UTC",
                location_id="office",
                notes="Work block.",
            )
        ],
    )

    passed, checks = evaluate_policy(
        task,
        office_end + timedelta(minutes=5),
        office_end + timedelta(minutes=35),
        [],
        dependency_state={
            "availability": availability,
            "travel_time_rules": [
                {"from_location_id": "office", "to_location_id": "gym", "minutes": 15}
            ],
        },
        candidate_location_id="gym",
    )

    assert passed is False
    travel_check = next(check for check in checks if check.name == "travel_time_buffer")
    assert "office->gym requires 15 minutes" in travel_check.reason


def test_policy_rejects_overlap_and_same_day_repeat_for_activity():
    task = _task("repeatable", target_date=date(2026, 6, 1))
    start = datetime(2026, 6, 1, 9, tzinfo=UTC)
    scheduled = [
        ScheduledTask(
            task_id="existing",
            activity_id="repeatable",
            start=start + timedelta(minutes=15),
            end=start + timedelta(minutes=45),
        )
    ]

    passed, checks = evaluate_policy(task, start, start + timedelta(minutes=30), scheduled)

    assert passed is False
    failed_names = {check.name for check in checks if not check.passed}
    assert {"no_overlap", "same_day_repeat"}.issubset(failed_names)


def test_policy_rejects_back_to_back_consultations_with_same_provider():
    start = datetime(2026, 6, 1, 18, 30, tzinfo=UTC)
    task = _task(
        "adherence",
        resources={"provider_ids": ["provider_remote_coach_01"], "location_ids": ["remote"]},
    )
    scheduled = [
        ScheduledTask(
            task_id="existing",
            activity_id="progression",
            title="Remote coach review of aerobic progression",
            start=datetime(2026, 6, 1, 18, tzinfo=UTC),
            end=datetime(2026, 6, 1, 18, 20, tzinfo=UTC),
            activity_type="consultation",
            provider_ids=["provider_remote_coach_01"],
            location_id="remote",
        )
    ]

    failed, failed_checks = evaluate_policy(
        task,
        start,
        start + timedelta(minutes=10),
        scheduled,
        activity={"activity_id": "adherence", "activity_type": "consultation"},
        candidate_location_id="remote",
    )
    passed, passed_checks = evaluate_policy(
        task,
        datetime(2026, 6, 1, 19, tzinfo=UTC),
        datetime(2026, 6, 1, 19, 10, tzinfo=UTC),
        scheduled,
        activity={"activity_id": "adherence", "activity_type": "consultation"},
        candidate_location_id="remote",
    )

    assert failed is False
    spacing_check = next(
        check for check in failed_checks if check.name == "same_provider_consultation_spacing"
    )
    assert "provider_remote_coach_01" in spacing_check.reason
    assert passed is True
    assert next(
        check for check in passed_checks if check.name == "same_provider_consultation_spacing"
    ).passed is True


def test_dependency_checks_are_specific_for_supported_seed_dependency_types():
    task = _task(
        "with_dependencies",
        dependencies=[
            {"type": "fasting", "hours": 10},
            {"type": "hydration", "target": "500ml"},
            {"type": "food_timing", "window": "post-workout"},
            {
                "type": "prep_task",
                "provider_type": "chef",
                "can_be_done_by_member": True,
                "can_be_done_by_provider": True,
            },
        ],
    )
    start = datetime(2026, 6, 1, 9, tzinfo=UTC)

    passed, checks = evaluate_policy(task, start, start + timedelta(minutes=30), [])

    assert passed is True
    dependency_checks = [check for check in checks if check.name.startswith("dependency:")]
    assert [check.name for check in dependency_checks] == [
        "dependency:fasting",
        "dependency:hydration",
        "dependency:food_timing",
        "dependency:prep_task",
    ]
    reasons = " ".join(check.reason for check in dependency_checks)
    assert "fasting requirement is represented" in reasons
    assert "hydration requirement is represented" in reasons
    assert "food timing metadata is present" in reasons
    assert "prep task can be done by member" in reasons


def test_chef_prep_dependency_requires_provider_availability_before_candidate():
    task = _task(
        "chef_prep",
        dependencies=[
            {
                "type": "prep_task",
                "provider_type": "chef",
                "can_be_done_by_provider": True,
            }
        ],
    )
    start = datetime(2026, 6, 1, 9, tzinfo=UTC)

    failed, failed_checks = evaluate_policy(
        task,
        start,
        start + timedelta(minutes=30),
        [],
        dependency_state={"availability": AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1)},
    )
    passed, passed_checks = evaluate_policy(
        task,
        start,
        start + timedelta(minutes=30),
        [],
        dependency_state={
            "availability": AvailabilityData(
                planning_start_date=date(2026, 6, 1),
                planning_months=1,
                availability_blocks=[
                    AvailabilityBlock(
                        resource_id="provider_chef_001",
                        resource_type="provider",
                        start=start - timedelta(minutes=30),
                        end=start,
                        timezone="UTC",
                    )
                ],
            )
        },
    )

    assert failed is False
    assert next(check for check in failed_checks if check.name == "dependency:prep_task").passed is False
    passed_check = next(check for check in passed_checks if check.name == "dependency:prep_task")
    assert passed is True
    assert passed_check.passed is True
    assert "30 minute provider prep window ending 0 minutes before candidate" in passed_check.reason


def test_prep_task_dependency_requires_duration_and_offset_window():
    start = datetime(2026, 6, 1, 9, tzinfo=UTC)
    task = _task(
        "prep_window",
        dependencies=[
            {
                "type": "prep_task",
                "provider_type": "chef",
                "can_be_done_by_provider": True,
                "prep_duration_minutes": 45,
                "offset_minutes_min": 15,
            }
        ],
    )
    too_short_availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[
            AvailabilityBlock(
                resource_id="provider_chef_001",
                resource_type="provider",
                start=start - timedelta(minutes=45),
                end=start - timedelta(minutes=15),
                timezone="UTC",
            )
        ],
    )
    covering_availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[
            AvailabilityBlock(
                resource_id="provider_chef_001",
                resource_type="provider",
                start=start - timedelta(minutes=60),
                end=start - timedelta(minutes=15),
                timezone="UTC",
            )
        ],
    )

    failed, failed_checks = evaluate_policy(
        task,
        start,
        start + timedelta(minutes=30),
        [],
        dependency_state={"availability": too_short_availability},
    )
    passed, passed_checks = evaluate_policy(
        task,
        start,
        start + timedelta(minutes=30),
        [],
        dependency_state={"availability": covering_availability},
    )

    assert failed is False
    assert "45 minute provider prep window ending 15 minutes before candidate" in next(
        check for check in failed_checks if check.name == "dependency:prep_task"
    ).reason
    assert passed is True
    assert "45 minute provider prep window ending 15 minutes before candidate" in next(
        check for check in passed_checks if check.name == "dependency:prep_task"
    ).reason


def test_substitution_task_schedules_with_substitution_calendar_row():
    start = datetime(2026, 6, 1, 9, tzinfo=UTC)
    task = _task("sub", resources={"location_ids": ["remote"]})
    task.is_substitution = True
    activity = {
        "activity_id": "sub",
        "title": "Remote substitute",
        "activity_type": "consultation",
        "load_level": "low",
        "allowed_locations": ["remote"],
    }

    result = schedule_tasks(
        [task],
        {"sub": activity},
        AvailabilityData(planning_start_date=start.date(), planning_months=1),
    )

    assert result.plan.tasks[0].activity_id == "sub"
    assert result.calendar_rows[0].substitution_status == "substitution"


def test_scheduler_tries_family_primary_before_substitution_even_when_substitution_has_higher_priority():
    primary = _task("bike", priority=90, resources={"location_ids": ["home"]})
    substitution = _task("band", priority=70, resources={"location_ids": ["remote"]})
    primary.task_instance_id = "task_bike_20260601_001"
    substitution.task_instance_id = "task_band_20260601_001"
    substitution.activity_family_id = primary.activity_family_id
    substitution.is_substitution = True
    activities = {
        "bike": {
            "activity_id": "bike",
            "title": "Zone 2 stationary bike",
            "activity_type": "fitness",
            "load_level": "medium",
            "allowed_locations": ["home"],
        },
        "band": {
            "activity_id": "band",
            "title": "Bodyweight and band aerobic circuit",
            "activity_type": "fitness",
            "load_level": "medium",
            "allowed_locations": ["remote"],
        },
    }

    result = schedule_tasks(
        [substitution, primary],
        activities,
        AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1),
    )

    assert [row.title for row in result.calendar_rows] == ["Zone 2 stationary bike"]
    assert any(
        trace.activity_id == "band"
        and trace.final_status == "skipped"
        and "already scheduled for this activity family occurrence" in trace.policy_fit_summary
        for trace in result.traces
    )


def test_scheduler_uses_planned_variety_after_primary_weekly_cap():
    availability = AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1)
    primary = {
        "activity_id": "chef_meal",
        "activity_type": "food",
        "meal_slot": "dinner",
        "title": "Chef meal",
        "load_level": "low",
        "allowed_locations": ["home"],
        "weekly_primary_cap": 1,
        "goal_contributions": [
            {
                "goal_action_id": "ga_meals",
                "counts_toward_weekly_target": True,
                "value": 1,
            }
        ],
    }
    restaurant = {
        "activity_id": "restaurant_meal",
        "activity_type": "food",
        "meal_slot": "dinner",
        "title": "Restaurant meal",
        "load_level": "low",
        "allowed_locations": ["restaurant"],
        "substitution_for_activity_id": "chef_meal",
        "variety_role": "planned_variety",
        "goal_contributions": [
            {
                "goal_action_id": "ga_meals",
                "counts_toward_weekly_target": True,
                "value": 1,
            }
        ],
    }
    tasks = [
        _task("chef_meal", target_date=date(2026, 6, 1)),
        _task("restaurant_meal", target_date=date(2026, 6, 1)),
        _task("chef_meal", target_date=date(2026, 6, 2)),
        _task("restaurant_meal", target_date=date(2026, 6, 2)),
    ]
    for task in tasks:
        task.activity_family_id = "fam_meal"
        task.duration_minutes = 30
        task.required_resources = {
            "location_ids": ["home" if task.activity_id == "chef_meal" else "restaurant"]
        }
        task.is_substitution = task.activity_id == "restaurant_meal"

    result = schedule_tasks(
        tasks,
        {"chef_meal": primary, "restaurant_meal": restaurant},
        availability,
        goal_actions=[
            {
                "goal_action_id": "ga_meals",
                "target": {"period": "weekly", "units": 14},
            }
        ],
    )

    scheduled_ids = [task.activity_id for task in result.plan.tasks]
    assert scheduled_ids == ["chef_meal", "restaurant_meal"]


def test_scheduler_uses_family_substitution_after_primary_fails():
    primary = _task("bike", priority=90, resources={"location_ids": ["lab"]})
    substitution = _task("band", priority=70, resources={"location_ids": ["home"]})
    primary.task_instance_id = "task_bike_20260601_001"
    substitution.task_instance_id = "task_band_20260601_001"
    substitution.activity_family_id = primary.activity_family_id
    substitution.is_substitution = True
    activities = {
        "bike": {
            "activity_id": "bike",
            "title": "Zone 2 stationary bike",
            "activity_type": "fitness",
            "load_level": "medium",
            "allowed_locations": ["lab"],
        },
        "band": {
            "activity_id": "band",
            "title": "Bodyweight and band aerobic circuit",
            "activity_type": "fitness",
            "load_level": "medium",
            "allowed_locations": ["home"],
        },
    }

    result = schedule_tasks(
        [substitution, primary],
        activities,
        AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1),
    )

    assert [row.title for row in result.calendar_rows] == ["Bodyweight and band aerobic circuit"]
    assert result.calendar_rows[0].substitution_status == "substitution"
    primary_trace = next(trace for trace in result.traces if trace.activity_id == "bike")
    assert primary_trace.final_status == "unscheduled"


def test_scheduler_uses_deterministic_trace_ids_across_outputs():
    start = datetime(2026, 6, 1, 9, tzinfo=UTC)
    task = _task("stable_trace", resources={"location_ids": ["remote"]})
    activity = {
        "activity_id": "stable_trace",
        "title": "Stable trace",
        "activity_type": "consultation",
        "load_level": "low",
        "allowed_locations": ["remote"],
    }

    result = schedule_tasks(
        [task],
        {"stable_trace": activity},
        AvailabilityData(planning_start_date=start.date(), planning_months=1),
    )

    expected_trace_id = "trace_task_stable_trace"
    assert result.traces[0].trace_id == expected_trace_id
    assert result.plan.tasks[0].trace_id == expected_trace_id
    assert result.calendar_rows[0].trace_id == expected_trace_id


def test_rejection_summary_aggregates_repeated_unscheduled_activity_instances():
    task_one = _task("never_places", target_date=date(2026, 6, 1), resources={"location_ids": ["lab"]})
    task_one.task_instance_id = "task_never_places_one"
    task_two = _task("never_places", target_date=date(2026, 6, 2), resources={"location_ids": ["lab"]})
    task_two.task_instance_id = "task_never_places_two"
    activity = {
        "activity_id": "never_places",
        "title": "Never places",
        "activity_type": "consultation",
        "load_level": "low",
        "allowed_locations": ["lab"],
    }
    availability = AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1)

    result = schedule_tasks([task_one, task_two], {"never_places": activity}, availability)

    assert result.rejection_summary["never_places"]["unscheduled_count"] == 2
    assert result.rejection_summary["never_places"]["rejected_candidate_count"] == (
        len(result.traces[0].rejected_candidates) + len(result.traces[1].rejected_candidates)
    )


def test_scheduler_skips_core_activity_after_weekly_goal_target_is_met():
    tasks = [
        _task(
            f"recovery_{index}",
            target_date=date(2026, 6, 1 + index),
            resources={"location_ids": ["home"]},
        )
        for index in range(3)
    ]
    activities = {
        task.activity_id: {
            "activity_id": task.activity_id,
            "title": f"Recovery action {index}",
            "activity_type": "therapy",
            "load_level": "low",
            "allowed_locations": ["home"],
            "goal_contributions": [
                {
                    "weekly_goal_action_id": "wga_recovery",
                    "counts_toward_weekly_target": True,
                    "value": 1,
                }
            ],
        }
        for index, task in enumerate(tasks)
    }

    result = schedule_tasks(
        tasks,
        activities,
        AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1),
        weekly_goal_actions=[
            {
                "weekly_goal_action_id": "wga_recovery",
                "label": "Complete recovery actions",
                "target_per_week": 2,
                "support_only": False,
            }
        ],
    )

    assert len(result.calendar_rows) == 2
    assert result.traces[-1].final_status == "skipped"
    assert "weekly target coverage is already met" in result.traces[-1].policy_fit_summary


def test_scheduler_skips_unlinked_support_substitution():
    task = _task("warmup", resources={"location_ids": ["gym"]})
    task.is_substitution = True
    activity = {
        "activity_id": "warmup",
        "title": "Member-led movement prep and activation",
        "activity_type": "fitness",
        "load_level": "low",
        "allowed_locations": ["gym"],
        "facilitator_type": "member",
        "goal_contributions": [
            {
                "weekly_goal_action_id": "wga_support",
                "counts_toward_weekly_target": False,
                "value": 0,
            }
        ],
    }

    result = schedule_tasks(
        [task],
        {"warmup": activity},
        AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1),
    )

    assert result.calendar_rows == []
    assert result.traces[0].final_status == "skipped"
    assert "prep or activation support" in result.traces[0].policy_fit_summary


def test_scheduler_skips_unlinked_prep_activation_support_primary():
    task = _task("activation", resources={"location_ids": ["gym"]})
    activity = {
        "activity_id": "activation",
        "title": "Trainer-led movement prep and activation",
        "activity_type": "fitness",
        "load_level": "low",
        "allowed_locations": ["gym"],
        "facilitator_type": "trainer",
        "goal_contributions": [
            {
                "weekly_goal_action_id": "wga_support",
                "counts_toward_weekly_target": False,
                "value": 0,
            }
        ],
    }

    result = schedule_tasks(
        [task],
        {"activation": activity},
        AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1),
    )

    assert result.calendar_rows == []
    assert result.traces[0].final_status == "skipped"
    assert "prep or activation support" in result.traces[0].policy_fit_summary


def test_scheduler_skips_provider_only_chef_prep_activity():
    task = _task("chef_prep", resources={"location_ids": ["home"], "provider_ids": ["provider_chef"]})
    activity = {
        "activity_id": "chef_prep",
        "title": "Chef batch meal prep",
        "activity_type": "food",
        "load_level": "low",
        "allowed_locations": ["home"],
        "facilitator_type": "chef",
        "required_provider_ids": ["provider_chef"],
        "goal_contributions": [
            {
                "weekly_goal_action_id": "wga_support",
                "counts_toward_weekly_target": False,
                "value": 0,
            }
        ],
    }

    result = schedule_tasks(
        [task],
        {"chef_prep": activity},
        AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1),
    )

    assert result.calendar_rows == []
    assert result.traces[0].final_status == "skipped"
    assert "chef prep is provider work" in result.traces[0].policy_fit_summary


def test_scheduler_skips_passive_fasting_prep_block():
    task = _task("fasting_prep", resources={"location_ids": ["home"]})
    activity = {
        "activity_id": "fasting_prep",
        "title": "Fasting prep block before blood panel",
        "activity_type": "consultation",
        "load_level": "low",
        "allowed_locations": ["home"],
        "goal_tags": ["fasting_prep", "lab"],
        "goal_contributions": [
            {
                "weekly_goal_action_id": "wga_lab",
                "counts_toward_weekly_target": False,
                "value": 0,
            }
        ],
    }

    result = schedule_tasks(
        [task],
        {"fasting_prep": activity},
        AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1),
    )

    assert result.calendar_rows == []
    assert result.traces[0].final_status == "skipped"
    assert "passive lab dependency" in result.traces[0].policy_fit_summary


def test_member_led_mobility_displays_as_fitness_not_therapy():
    task = _task("mobility", resources={"location_ids": ["home"]})
    activity = {
        "activity_id": "mobility",
        "title": "Member-led knee and lower-back mobility session",
        "activity_type": "therapy",
        "facilitator_type": "member",
        "load_level": "low",
        "allowed_locations": ["home"],
    }

    result = schedule_tasks(
        [task],
        {"mobility": activity},
        AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1),
    )

    assert result.calendar_rows[0].activity_type == "fitness"


def test_trace_source_paths_include_resource_universe_when_travel_rules_are_provided():
    task = _task("with_provenance", resources={"location_ids": ["home"]})
    result = schedule_tasks(
        [task],
        {
            "with_provenance": {
                "activity_id": "with_provenance",
                "title": "With provenance",
                "activity_type": "fitness",
                "load_level": "low",
                "allowed_locations": ["home"],
            }
        },
        AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1),
        travel_time_rules=[{"from_location_id": "office", "to_location_id": "home", "minutes": 5}],
        source_artifact_paths=[
            "data/action_plan.json",
            "data/availability.json",
            "data/resource_universe.json",
        ],
    )

    assert "data/resource_universe.json" in result.traces[0].source_artifact_paths


def test_prerequisite_activity_matches_required_title_before_candidate():
    task = _task(
        "review",
        dependencies=[
            {
                "type": "prerequisite_activity",
                "activity_title_contains": "Baseline fasting metabolic lab panel",
                "offset_days_min": 2,
            }
        ],
        target_date=date(2026, 6, 12),
    )
    start = datetime(2026, 6, 12, 9, tzinfo=UTC)
    wrong_prior = ScheduledTask(
        task_id="wrong",
        activity_id="act_other",
        title="Baseline movement and knee assessment",
        start=datetime(2026, 6, 4, 9, tzinfo=UTC),
        end=datetime(2026, 6, 4, 10, tzinfo=UTC),
    )
    matching_prior = ScheduledTask(
        task_id="right",
        activity_id="act_001",
        title="Baseline fasting metabolic lab panel",
        start=datetime(2026, 6, 4, 9, tzinfo=UTC),
        end=datetime(2026, 6, 4, 10, tzinfo=UTC),
    )

    failed, failed_checks = evaluate_policy(
        task, start, start + timedelta(minutes=30), [wrong_prior]
    )
    passed, passed_checks = evaluate_policy(
        task, start, start + timedelta(minutes=30), [wrong_prior, matching_prior]
    )

    failed_check = next(
        check for check in failed_checks if check.name == "dependency:prerequisite_activity"
    )
    passed_check = next(
        check for check in passed_checks if check.name == "dependency:prerequisite_activity"
    )
    assert failed is False
    assert "title containing 'Baseline fasting metabolic lab panel'" in failed_check.reason
    assert passed is True
    assert "title containing 'Baseline fasting metabolic lab panel'" in passed_check.reason


def test_scheduler_sorts_places_tasks_and_records_explainable_traces():
    start = datetime(2026, 6, 1, 9, tzinfo=UTC)
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[
            AvailabilityBlock(
                resource_id="provider_1",
                resource_type="provider",
                start=start,
                end=start + timedelta(hours=2),
                timezone="UTC",
                location_id="clinic",
            ),
            AvailabilityBlock(
                resource_id="clinic",
                resource_type="location",
                start=start,
                end=start + timedelta(hours=2),
                timezone="UTC",
                location_id="clinic",
            )
        ],
    )
    activities = {
        "high": {
            "activity_id": "high",
            "title": "High priority consult",
            "activity_type": "consultation",
            "load_level": "low",
            "remote_allowed": False,
            "allowed_locations": ["clinic"],
            "same_day_repeat_allowed": False,
            "care_context_required": ["summary", "constraints"],
            "required_provider_ids": ["provider_1"],
        },
        "low": {
            "activity_id": "low",
            "title": "Low priority follow-up",
            "activity_type": "consultation",
            "load_level": "low",
            "remote_allowed": False,
            "allowed_locations": ["clinic"],
            "same_day_repeat_allowed": False,
            "care_context_required": [],
            "required_provider_ids": ["provider_1"],
        },
    }
    tasks = [
        _task("low", priority=5, resources={"provider_ids": ["provider_1"]}),
        _task("high", priority=1, resources={"provider_ids": ["provider_1"]}),
    ]

    result = schedule_tasks(tasks, activities, availability, run_id="test-run")

    assert [task.activity_id for task in result.plan.tasks] == ["high", "low"]
    assert result.plan.tasks[0].end <= result.plan.tasks[1].start
    assert len(result.calendar_rows) == 2
    assert len(result.traces) == 2
    assert all(trace.constraint_checks for trace in result.traces)
    high_trace = next(trace for trace in result.traces if trace.activity_id == "high")
    assert high_trace.provider_handoff_summary == (
        "Share care context with provider_1: summary; constraints."
    )


def test_scheduler_caps_period_aware_goal_actions():
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[],
    )
    base_activity = {
        "activity_type": "consultation",
        "load_level": "low",
        "allowed_locations": ["remote"],
        "goal_contributions": [
            {
                "goal_action_id": "ga_recovery_checkin",
                "counts_toward_weekly_target": True,
                "value": 1,
            }
        ],
    }
    activities = {
        "first": {"activity_id": "first", "title": "First check-in", **base_activity},
        "second": {"activity_id": "second", "title": "Second check-in", **base_activity},
    }

    result = schedule_tasks(
        [
            _task("first", priority=1),
            _task("second", priority=2),
        ],
        activities,
        availability,
        goal_actions=[
            {
                "goal_action_id": "ga_recovery_checkin",
                "label": "Recovery check-in",
                "target": {"period": "weekly", "units": 1},
            }
        ],
    )

    assert [task.activity_id for task in result.plan.tasks] == ["first"]
    assert any(
        trace.activity_id == "second"
        and trace.final_status == "skipped"
        and "weekly target coverage is already met" in trace.policy_fit_summary
        for trace in result.traces
    )


def test_scheduler_reports_weekly_and_three_month_goal_coverage():
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[],
    )
    activities = {
        "weekly": {
            "activity_id": "weekly",
            "title": "Weekly action",
            "activity_type": "consultation",
            "load_level": "low",
            "allowed_locations": ["remote"],
            "goal_contributions": [
                {
                    "goal_action_id": "ga_weekly",
                    "counts_toward_weekly_target": True,
                    "value": 1,
                }
            ],
        },
        "review": {
            "activity_id": "review",
            "title": "Three-month review",
            "activity_type": "consultation",
            "load_level": "low",
            "allowed_locations": ["remote"],
            "goal_contributions": [
                {
                    "goal_action_id": "ga_review",
                    "counts_toward_weekly_target": True,
                    "value": 1,
                }
            ],
        },
    }

    result = schedule_tasks(
        [_task("weekly"), _task("review", target_date=date(2026, 6, 2))],
        activities,
        availability,
        goal_actions=[
            {
                "goal_action_id": "ga_weekly",
                "label": "Weekly action",
                "target": {"period": "weekly", "units": 1, "unit_label": "actions"},
            },
            {
                "goal_action_id": "ga_review",
                "label": "Three-month review",
                "target": {"period": "3_month", "units": 1, "unit_label": "reviews"},
            },
        ],
    )

    report = result.plan.goal_report
    assert report is not None
    weekly_items = [
        item for item in report["weekly"] if item["goal_action_id"] == "ga_weekly"
    ]
    assert weekly_items[0]["week"] == "2026-W23"
    assert weekly_items[0]["scheduled_units"] == 1
    assert weekly_items[0]["met"] is True
    assert report["three_month"] == [
        {
            "goal_action_id": "ga_review",
            "label": "Three-month review",
            "target_units": 1.0,
            "unit_label": "reviews",
            "period": "3_month",
            "scheduled_units": 1,
            "met": True,
        }
    ]
