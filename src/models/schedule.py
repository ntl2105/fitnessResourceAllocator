from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from src.models.activity import ActivityType


class FlexibleModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class TaskInstance(FlexibleModel):
    task_instance_id: str
    activity_id: str
    activity_family_id: str
    is_substitution: bool
    target_date: date | None = None
    target_week: str | None = None
    duration_minutes: int
    priority: int
    goal_tags: list[str] = []
    required_resources: dict[str, Any] = {}
    dependencies: list[Any] = []
    status: str


class ScheduledTask(FlexibleModel):
    task_id: str
    activity_id: str
    start: datetime
    end: datetime
    activity_type: str | None = None
    load_level: str | None = None
    location_id: str | None = None
    provider_ids: list[str] = []
    equipment_ids: list[str] = []
    status: str = "scheduled"
    trace_id: str | None = None


class PersonalizedPlan(FlexibleModel):
    run_id: str | None = None
    tasks: list[ScheduledTask] = []
    metadata: dict[str, Any] = {}
    goal_report: dict[str, Any] | None = None


class CalendarRow(FlexibleModel):
    calendar_row_id: str
    date: date
    start_time: str
    end_time: str
    title: str
    activity_type: ActivityType
    goal_tags: list[str] = []
    load_level: str
    location_id: str | None = None
    mode: str
    substitution_status: str
    trace_id: str | None = None
    compact_group_key: str | None = None
    original_target_date: date | None = None
