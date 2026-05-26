from __future__ import annotations

from typing import Any


def provider_handoff_summary(activity: dict[str, Any]) -> str | None:
    care_context = activity.get("care_context_required") or []
    provider_ids = activity.get("required_provider_ids") or []
    if not care_context:
        return None
    recipient = ", ".join(provider_ids) if provider_ids else "care team"
    return f"Share care context with {recipient}: {'; '.join(care_context)}."
