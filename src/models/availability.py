from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class FlexibleModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class AvailabilityBlock(FlexibleModel):
    resource_id: str
    resource_type: str
    start: datetime
    end: datetime
    timezone: str
    location_id: str | None = None
    remote_supported: bool = False
    travel_compatible: bool = False
    notes: str | None = None


class AvailabilityData(FlexibleModel):
    planning_start_date: date
    planning_months: int
    availability_blocks: list[AvailabilityBlock] = []
