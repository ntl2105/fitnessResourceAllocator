from datetime import date
from datetime import datetime, timezone

from src.models.availability import AvailabilityBlock, AvailabilityData
from src.scheduler.task_instances import expand_primary_activities


def test_expands_primary_and_substitution_activities_for_supported_frequency_types():
    action_plan = {
        "activities": [
            {
                "activity_id": "once_primary",
                "activity_family_id": "fam_once",
                "is_primary": True,
                "priority": 1,
                "goal_tags": ["baseline"],
                "frequency": {"type": "once", "target_date": "2026-06-03"},
                "duration_minutes": 30,
                "required_provider_ids": ["provider_1"],
                "required_equipment_ids": ["eq_1"],
                "allowed_locations": ["clinic"],
                "dependencies": [{"type": "fasting"}],
            },
            {
                "activity_id": "daily_primary",
                "activity_family_id": "fam_daily",
                "is_primary": True,
                "priority": 3,
                "goal_tags": ["habit"],
                "frequency": {"type": "daily", "count": 1},
                "duration_minutes": 10,
                "required_provider_ids": [],
                "required_equipment_ids": [],
                "allowed_locations": [],
                "dependencies": [],
            },
            {
                "activity_id": "weekly_primary",
                "activity_family_id": "fam_weekly",
                "is_primary": True,
                "priority": 2,
                "goal_tags": [],
                "frequency": {
                    "type": "weekly",
                    "count": 2,
                    "preferred_days": ["monday", "wednesday"],
                },
                "duration_minutes": 20,
                "required_provider_ids": [],
                "required_equipment_ids": [],
                "allowed_locations": ["home"],
                "dependencies": [],
            },
            {
                "activity_id": "monthly_primary",
                "activity_family_id": "fam_monthly",
                "is_primary": True,
                "priority": 4,
                "goal_tags": [],
                "frequency": {
                    "type": "monthly",
                    "count": 1,
                    "preferred_days": ["friday"],
                    "preferred_week": "first",
                },
                "duration_minutes": 45,
                "required_provider_ids": [],
                "required_equipment_ids": [],
                "allowed_locations": ["remote"],
                "dependencies": [],
            },
            {
                "activity_id": "substitution",
                "activity_family_id": "fam_once",
                "is_primary": False,
                "priority": 1,
                "goal_tags": ["baseline"],
                "frequency": {"type": "once", "target_date": "2026-06-03"},
                "duration_minutes": 30,
                "required_provider_ids": [],
                "required_equipment_ids": [],
                "allowed_locations": [],
                "dependencies": [],
            },
        ]
    }
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[],
    )

    tasks = expand_primary_activities(action_plan, availability)

    task_ids = [task.activity_id for task in tasks]
    assert task_ids.count("substitution") == 1
    assert task_ids.count("once_primary") == 1
    assert task_ids.count("daily_primary") == 30
    assert task_ids.count("weekly_primary") == 9
    assert task_ids.count("monthly_primary") == 1
    substitution_task = next(task for task in tasks if task.activity_id == "substitution")
    assert substitution_task.is_substitution is True
    assert substitution_task.activity_family_id == "fam_once"


def test_expanded_task_preserves_activity_fields_and_required_resources(load_seed):
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[],
    )

    action_plan = load_seed("action_plan.json")
    tasks = expand_primary_activities(action_plan, availability)
    expanded_activity_ids = {task.activity_id for task in tasks}
    source_activity = next(
        activity
        for activity in action_plan["activities"]
        if activity["is_primary"]
        and not (activity.get("activity_type") == "food" and activity.get("meal_slot"))
        and activity["activity_id"] in expanded_activity_ids
        and (
            activity.get("required_provider_ids")
            or activity.get("required_equipment_ids")
            or activity.get("allowed_locations")
            or activity.get("dependencies")
        )
    )
    expanded_task = next(
        task for task in tasks if task.activity_id == source_activity["activity_id"]
    )

    assert expanded_task.activity_family_id == source_activity["activity_family_id"]
    assert expanded_task.is_substitution is False
    assert expanded_task.priority == source_activity["priority"]
    assert expanded_task.goal_tags == source_activity["goal_tags"]
    assert expanded_task.required_resources == {
        "provider_ids": source_activity.get("required_provider_ids", []),
        "equipment_ids": source_activity.get("required_equipment_ids", []),
        "location_ids": source_activity.get("allowed_locations", []),
    }
    assert expanded_task.dependencies == source_activity.get("dependencies", [])
    assert expanded_task.status == "pending"


def test_expands_planned_variety_substitution_from_primary_frequency():
    availability = AvailabilityData(planning_start_date=date(2026, 6, 1), planning_months=1)
    action_plan = {
        "activities": [
            {
                "activity_id": "meal_primary",
                "activity_family_id": "fam_meal",
                "is_primary": True,
                "duration_minutes": 30,
                "priority": 10,
                "goal_tags": ["nutrition"],
                "required_provider_ids": [],
                "required_equipment_ids": [],
                "allowed_locations": ["home"],
                "dependencies": [],
                "frequency": {
                    "type": "weekly",
                    "count": 2,
                    "preferred_days": ["monday", "tuesday"],
                },
            },
            {
                "activity_id": "meal_restaurant",
                "activity_family_id": "fam_meal",
                "is_primary": False,
                "substitution_for_activity_id": "meal_primary",
                "variety_role": "planned_variety",
                "duration_minutes": 30,
                "priority": 11,
                "goal_tags": ["nutrition"],
                "required_provider_ids": [],
                "required_equipment_ids": [],
                "allowed_locations": ["restaurant"],
                "dependencies": [],
                "frequency": {"type": "as_needed", "count": 0},
            },
        ]
    }

    tasks = expand_primary_activities(action_plan, availability)

    assert sum(1 for task in tasks if task.activity_id == "meal_primary") == 10
    assert sum(1 for task in tasks if task.activity_id == "meal_restaurant") == 10


def test_expands_daily_meal_coverage_by_member_location():
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[
            AvailabilityBlock(
                resource_id="travel_hk",
                resource_type="member_travel",
                start=datetime(2026, 6, 3, 0, tzinfo=timezone.utc),
                end=datetime(2026, 6, 4, 0, tzinfo=timezone.utc),
                timezone="UTC",
                location_id="travel_hotel",
            ),
            AvailabilityBlock(
                resource_id="wfh_20260605",
                resource_type="member_location",
                start=datetime(2026, 6, 5, 0, tzinfo=timezone.utc),
                end=datetime(2026, 6, 6, 0, tzinfo=timezone.utc),
                timezone="UTC",
                location_id="home",
                notes="WFH day.",
            ),
        ],
    )
    action_plan = {
        "activities": [
            _meal("breakfast_home", "breakfast", ["home"]),
            _meal("lunch_office", "lunch", ["office"]),
            _meal("lunch_home", "lunch", ["home"]),
            _meal("dinner_home", "dinner", ["home"]),
            _meal("breakfast_travel", "breakfast", ["travel_hotel"]),
            _meal("lunch_travel", "lunch", ["travel_hotel"]),
            _meal("dinner_travel", "dinner", ["travel_hotel"]),
        ]
    }

    tasks = expand_primary_activities(action_plan, availability)
    by_day_slot = {
        (task.target_date, task.activity_id)
        for task in tasks
        if task.task_instance_id.startswith("task_meal_coverage_")
    }

    assert (date(2026, 6, 2), "lunch_office") in by_day_slot
    assert (date(2026, 6, 5), "lunch_home") in by_day_slot
    assert {
        (date(2026, 6, 3), "breakfast_travel"),
        (date(2026, 6, 3), "lunch_travel"),
        (date(2026, 6, 3), "dinner_travel"),
    }.issubset(by_day_slot)


def test_daily_meal_coverage_rotates_eligible_variety_options():
    availability = AvailabilityData(
        planning_start_date=date(2026, 6, 1),
        planning_months=1,
        availability_blocks=[],
    )
    action_plan = {
        "activities": [
            _meal("breakfast_chef", "breakfast", ["home"]),
            _meal("breakfast_lowprep", "breakfast", ["home"]),
            _meal("lunch_office_delivery", "lunch", ["office"]),
            _meal("lunch_office_assembled", "lunch", ["office"]),
            _meal("dinner_home", "dinner", ["home"]),
            _meal("dinner_restaurant", "dinner", ["restaurant"]),
        ]
    }

    tasks = [
        task
        for task in expand_primary_activities(action_plan, availability)
        if task.task_instance_id.startswith("task_meal_coverage_")
    ]
    first_week = [task for task in tasks if task.target_date and task.target_date < date(2026, 6, 8)]
    by_slot = {
        slot: {task.activity_id for task in first_week if task.activity_id.startswith(slot)}
        for slot in ("breakfast", "lunch", "dinner")
    }

    assert by_slot == {
        "breakfast": {"breakfast_chef", "breakfast_lowprep"},
        "lunch": {"lunch_office_delivery", "lunch_office_assembled"},
        "dinner": {"dinner_home", "dinner_restaurant"},
    }


def _meal(activity_id: str, meal_slot: str, locations: list[str]) -> dict:
    return {
        "activity_id": activity_id,
        "activity_family_id": f"fam_{activity_id}",
        "activity_type": "food",
        "meal_slot": meal_slot,
        "title": activity_id.replace("_", " "),
        "is_primary": True,
        "duration_minutes": 30,
        "priority": 10,
        "goal_tags": [meal_slot],
        "required_provider_ids": [],
        "required_equipment_ids": [],
        "allowed_locations": locations,
        "dependencies": [],
        "frequency": {"type": "as_needed", "count": 0},
    }
