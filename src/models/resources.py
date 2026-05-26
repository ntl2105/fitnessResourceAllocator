from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class FlexibleModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class Provider(FlexibleModel):
    provider_id: str
    provider_type: str
    display_name: str
    modalities_supported: list[str] = []
    location_ids: list[str] = []
    remote_supported: bool = False
    travel_compatible: bool = False
    care_context_supported: list[str] = []
    notes: str | None = None


class Equipment(FlexibleModel):
    equipment_id: str
    equipment_type: str
    display_name: str
    location_ids: list[str] = []
    travel_compatible: bool = False
    availability_required: bool = False
    notes: str | None = None


class Location(FlexibleModel):
    location_id: str
    location_type: str | None = None
    display_name: str
    timezone: str | None = None
    travel_compatible: bool = False
    available_equipment_ids: list[str] = []
    notes: str | None = None


class TravelWindow(FlexibleModel):
    travel_window_id: str
    destination: str | None = None
    start: datetime
    end: datetime
    available_location_ids: list[str] = []


class TravelTimeRule(FlexibleModel):
    from_location_id: str
    to_location_id: str
    minutes: int


class ResourceUniverse(FlexibleModel):
    providers: list[Provider] = []
    equipment: list[Equipment] = []
    locations: list[Location] = []
    travel_windows: list[TravelWindow] = []
    travel_time_rules: list[TravelTimeRule] = []

    def provider_ids(self) -> list[str]:
        return [provider.provider_id for provider in self.providers]

    def equipment_ids(self) -> list[str]:
        return [equipment.equipment_id for equipment in self.equipment]

    def location_ids(self) -> list[str]:
        return [location.location_id for location in self.locations]
