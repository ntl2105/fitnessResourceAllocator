from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict


class FlexibleModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class ActivityType(StrEnum):
    FITNESS = "fitness"
    FOOD = "food"
    MEDICATION = "medication"
    THERAPY = "therapy"
    CONSULTATION = "consultation"


class ActivityPrescription(FlexibleModel):
    activity_id: str
    priority: int
    goal_tags: list[str] = []
    activity_type: ActivityType
    title: str
    frequency: dict[str, Any]
    duration_minutes: int
    load_level: str
    details: str | None = None
    facilitator_type: str | None = None
    required_provider_ids: list[str] = []
    required_equipment_ids: list[str] = []
    allowed_locations: list[str] = []
    remote_allowed: bool = False
    prep_required: bool = False
    dependencies: list[Any] = []
    substitution_activity_ids: list[str] = []
    skip_adjustment: Any = None
    metrics_to_collect: list[str] = []
    care_context_required: list[str] = []
    share_with_provider_types: list[str] = []
    raw_clinical_data_required: bool = False
    journey_phase_applicability: list[str] = []
    same_day_repeat_allowed: bool = False
    is_primary: bool
    activity_family_id: str


class ActivityFamily(FlexibleModel):
    activity_family_id: str
    intent: str
    goal_tags: list[str] = []
    primary_activity: ActivityPrescription
    substitution_activities: list[ActivityPrescription] = []
    substitution_rules: list[dict[str, Any]] = []
    family_validation_notes: list[str] = []

    def flattened_activities(self) -> list[ActivityPrescription]:
        return [self.primary_activity, *self.substitution_activities]

    def flatten_activities(self) -> list[ActivityPrescription]:
        return self.flattened_activities()

    def flattened_activity_ids(self) -> list[str]:
        return [activity.activity_id for activity in self.flattened_activities()]


class ActivityFamiliesDocument(FlexibleModel):
    activity_families: list[ActivityFamily]

    def flattened_activities(self) -> list[ActivityPrescription]:
        return [
            activity
            for family in self.activity_families
            for activity in family.flattened_activities()
        ]

    def flatten_activities(self) -> list[ActivityPrescription]:
        return self.flattened_activities()

    def flattened_activity_ids(self) -> list[str]:
        return [activity.activity_id for activity in self.flattened_activities()]
