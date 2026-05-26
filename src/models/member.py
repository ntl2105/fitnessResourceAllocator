from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class FlexibleModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class TravelWindow(FlexibleModel):
    travel_window_id: str
    destination: str | None = None
    start: datetime
    end: datetime


class JourneyPhase(FlexibleModel):
    phase_id: str
    phase_type: str
    start_date: date
    end_date: date
    trigger: str | None = None
    primary_goals: list[str] = []
    scheduling_biases: list[str] = []


class MemberProfile(FlexibleModel):
    member_id: str
    name: str
    timezone: str
    age_range: str | None = None
    occupation: str | None = None
    typical_work_hours: dict[str, Any] = {}
    goals: list[Any] = []
    preferences: dict[str, Any] = {}
    constraints: dict[str, Any] = {}
    baseline_metrics: dict[str, Any] = {}
    scheduling_rules: dict[str, Any] = {}
    journey_phases: list[JourneyPhase] = []
    location_rhythm: dict[str, Any] = {}
    travel_windows: list[TravelWindow] = []
