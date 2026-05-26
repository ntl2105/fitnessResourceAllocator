from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def new_trace_id() -> str:
    return f"trace_{uuid4().hex}"


class FlexibleModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class ConstraintCheck(FlexibleModel):
    name: str
    passed: bool
    reason: str


class DecisionTrace(FlexibleModel):
    trace_id: str = Field(default_factory=new_trace_id)
    task_instance_id: str
    activity_id: str
    final_status: str
    selected_slot: dict[str, Any] | None = None
    policy_fit_summary: str | None = None
    resource_fit_summary: str | None = None
    constraint_checks: list[ConstraintCheck] = []
    rejected_candidates: list[dict[str, Any]] = []
    substitution_reason: str | None = None
    dependency_checks: list[Any] = []
    provider_handoff_summary: str | None = None
    skip_adjustment_applied: Any = None
    source_artifact_paths: list[str] = []
