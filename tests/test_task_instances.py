from datetime import date

from src.models.availability import AvailabilityData
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

    tasks = expand_primary_activities(load_seed("action_plan.json"), availability)
    lab_task = next(task for task in tasks if task.activity_id == "act_001")

    assert lab_task.activity_family_id == "fam_001"
    assert lab_task.is_substitution is False
    assert lab_task.priority == 1
    assert lab_task.goal_tags == ["metabolic_health", "preventive_care"]
    assert lab_task.required_resources == {
        "provider_ids": ["provider_lab_001"],
        "equipment_ids": ["eq_lab_draw_station"],
        "location_ids": ["lab"],
    }
    assert lab_task.dependencies == [{"hours": 10, "must_happen": "before", "type": "fasting"}]
    assert lab_task.status == "pending"
