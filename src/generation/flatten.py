from pathlib import Path
from typing import Any

from src.io_utils import load_json, save_json
from src.models.activity import ActivityFamiliesDocument, ActivityFamily, ActivityPrescription


def load_activity_families_payload(payload: Any) -> list[ActivityFamily]:
    if isinstance(payload, dict):
        document = ActivityFamiliesDocument.model_validate(payload)
        return document.activity_families
    if isinstance(payload, list):
        return [ActivityFamily.model_validate(item) for item in payload]
    raise ValueError("Activity families payload must be an array or an object wrapper.")


def flatten_activity_families(
    activity_families: list[ActivityFamily],
) -> list[ActivityPrescription]:
    return [
        activity
        for family in activity_families
        for activity in family.flattened_activities()
    ]


def action_plan_payload(activities: list[ActivityPrescription]) -> dict[str, list[dict[str, Any]]]:
    return {
        "activities": [
            activity.model_dump(mode="json", exclude_none=True) for activity in activities
        ]
    }


def write_action_plan(source_path: str | Path, output_path: str | Path) -> list[ActivityPrescription]:
    families = load_activity_families_payload(load_json(source_path))
    activities = flatten_activity_families(families)
    save_json(output_path, action_plan_payload(activities))
    return activities
