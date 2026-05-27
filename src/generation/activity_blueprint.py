from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from pydantic import BaseModel, ConfigDict


class FlexibleModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class ActivityFamilyBlueprint(FlexibleModel):
    activity_family_id: str
    batch_id: str
    care_domain: str | None = None
    family_target: dict[str, Any] | None = None
    goal_action_ids: list[str] = []
    weekly_goal_action_ids: list[str] = []
    primary_role: str
    primary_activity_type: str
    primary_intent: str
    primary_counts_toward_weekly_target: bool
    primary_frequency: dict[str, Any]
    primary_weekly_frequency_estimate: float = 0
    meal_slot: str | None = None
    phase_scope: list[str] = []
    location_strategy: str | None = None
    substitution_count: int = 0
    substitution_reason_codes: list[str] = []
    travel_context: bool = False
    semantic_notes: list[str] = []


class ActivityFamilyBlueprintDocument(FlexibleModel):
    activity_family_blueprints: list[ActivityFamilyBlueprint]
    count_self_check: dict[str, Any] = {}


def _goal_action_ids(member_payload: dict[str, Any]) -> set[str]:
    ids = {
        action["goal_action_id"]
        for action in member_payload.get("goal_actions", [])
        if action.get("goal_action_id")
    }
    ids.update(
        action["weekly_goal_action_id"]
        for action in member_payload.get("weekly_goal_actions", [])
        if action.get("weekly_goal_action_id")
    )
    return ids


def _budget_by_batch(budget_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item["batch_id"]: item
        for item in budget_payload.get("batch_budgets", [])
        if item.get("batch_id")
    }


def _budget_by_goal_action(budget_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        (item.get("goal_action_id") or item.get("weekly_goal_action_id")): item
        for item in budget_payload.get("goal_action_budgets", [])
        + budget_payload.get("weekly_goal_action_budgets", [])
        if item.get("goal_action_id") or item.get("weekly_goal_action_id")
    }


def _blueprint_goal_action_ids(item: ActivityFamilyBlueprint) -> list[str]:
    return list(dict.fromkeys([*item.goal_action_ids, *item.weekly_goal_action_ids]))


def _family_target_action_id(item: ActivityFamilyBlueprint) -> str | None:
    if not item.family_target:
        return None
    return item.family_target.get("goal_action_id") or item.family_target.get(
        "weekly_goal_action_id"
    )


def _duplicate_values(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def validate_activity_blueprint(
    blueprint_payload: dict[str, Any],
    budget_payload: dict[str, Any],
    member_payload: dict[str, Any],
) -> dict[str, Any]:
    document = ActivityFamilyBlueprintDocument.model_validate(blueprint_payload)
    blueprints = document.activity_family_blueprints
    batch_budgets = _budget_by_batch(budget_payload)
    action_budgets = _budget_by_goal_action(budget_payload)
    valid_action_ids = _goal_action_ids(member_payload)

    errors: list[str] = []
    warnings: list[str] = []
    family_ids = [item.activity_family_id for item in blueprints]
    duplicate_family_ids = _duplicate_values(family_ids)
    if duplicate_family_ids:
        errors.append(f"Duplicate activity_family_id values: {', '.join(duplicate_family_ids)}")

    family_count = len(blueprints)
    minimum_family_count = int(budget_payload.get("minimum_primary_family_count", 0))
    if family_count < minimum_family_count:
        errors.append(
            f"Blueprint has {family_count} families; minimum is {minimum_family_count}."
        )

    batch_counts = Counter(item.batch_id for item in blueprints)
    for batch_id, budget in batch_budgets.items():
        expected = int(budget.get("primary_family_budget", 0))
        actual = batch_counts.get(batch_id, 0)
        if actual != expected:
            errors.append(
                f"Batch {batch_id} has {actual} families; expected {expected}."
            )

    unknown_batches = sorted(set(batch_counts) - set(batch_budgets))
    if unknown_batches:
        errors.append(f"Unknown batch IDs: {', '.join(unknown_batches)}")

    self_check = document.count_self_check or {}
    if self_check:
        for batch_id, actual in batch_counts.items():
            stated = self_check.get(batch_id)
            if stated != actual:
                errors.append(
                    f"count_self_check for {batch_id} says {stated}; actual is {actual}."
                )
        stated_total = self_check.get("total")
        if stated_total != family_count:
            errors.append(
                f"count_self_check total says {stated_total}; actual is {family_count}."
            )

    goal_frequency_totals: dict[str, float] = defaultdict(float)
    goal_counting_families: dict[str, int] = defaultdict(int)
    goal_support_families: dict[str, int] = defaultdict(int)
    food_slots = Counter()
    substitution_reason_codes = {
        "travel_window",
        "provider_unavailable",
        "facility_unavailable",
        "equipment_unavailable",
        "lower_load_needed",
        "pain_or_fatigue",
        "remote_delivery_needed",
        "time_conflict",
        "prep_unavailable",
    }

    for item in blueprints:
        action_ids = _blueprint_goal_action_ids(item)
        if not action_ids:
            errors.append(f"{item.activity_family_id} does not reference any goal actions.")

        family_target_action_id = _family_target_action_id(item)
        if item.family_target and family_target_action_id not in action_ids:
            errors.append(
                f"{item.activity_family_id} family_target references "
                f"{family_target_action_id}, but goal_action_ids does not include it."
            )

        for action_id in action_ids:
            if action_id not in valid_action_ids:
                errors.append(
                    f"{item.activity_family_id} references unknown goal action {action_id}."
                )
                continue
            budget = action_budgets.get(action_id)
            if not budget:
                errors.append(
                    f"{item.activity_family_id} references {action_id}, but it has no budget entry."
                )
                continue
            if item.primary_counts_toward_weekly_target:
                goal_frequency_totals[action_id] += item.primary_weekly_frequency_estimate
                goal_counting_families[action_id] += 1
            else:
                goal_support_families[action_id] += 1

            if (
                item.travel_context
                and item.primary_counts_toward_weekly_target
                and not budget.get("travel_primary_allowed", False)
            ):
                errors.append(
                    f"{item.activity_family_id} is travel-context and counting toward "
                    f"{action_id}, but that action does not allow travel primaries."
                )

        cadence = str(item.primary_frequency.get("cadence") or item.primary_frequency.get("type") or "")
        non_normal_cadences = {"due-week", "due_week", "monthly", "travel-window", "travel_window", "once"}
        if (
            item.primary_counts_toward_weekly_target
            and item.primary_weekly_frequency_estimate <= 0
            and cadence not in non_normal_cadences
        ):
            errors.append(
                f"{item.activity_family_id} counts toward a weekly target but has "
                "primary_weekly_frequency_estimate <= 0."
            )

        if item.primary_activity_type == "food":
            if item.primary_counts_toward_weekly_target:
                if item.meal_slot not in {"breakfast", "lunch", "dinner"}:
                    errors.append(
                        f"{item.activity_family_id} is a counting food family without a canonical meal_slot."
                    )
                else:
                    food_slots[item.meal_slot] += 1

        if item.substitution_count > 0:
            if not item.substitution_reason_codes:
                errors.append(
                    f"{item.activity_family_id} plans substitutions without reason codes."
                )
            invalid_codes = sorted(set(item.substitution_reason_codes) - substitution_reason_codes)
            if invalid_codes:
                errors.append(
                    f"{item.activity_family_id} uses invalid substitution reason codes: "
                    f"{', '.join(invalid_codes)}."
                )
        elif item.substitution_reason_codes:
            warnings.append(
                f"{item.activity_family_id} has substitution reason codes but substitution_count is 0."
            )

    for action_id, budget in action_budgets.items():
        max_frequency = budget.get("max_counting_primary_weekly_frequency")
        if max_frequency is not None:
            actual = goal_frequency_totals.get(action_id, 0)
            if actual > float(max_frequency):
                errors.append(
                    f"{action_id} has weekly counting estimate {actual:g}; cap is {float(max_frequency):g}."
                )
        expected_primary = int(budget.get("primary_family_budget", 0))
        actual_primary = goal_counting_families.get(action_id, 0)
        if actual_primary == 0 and expected_primary > 0 and float(max_frequency or 0) > 0:
            warnings.append(f"{action_id} has no counting primary families.")

    structured_budget = action_budgets.get("ga_structured_meals_weekly", {})
    required_slots = set(structured_budget.get("canonical_meal_slots", []))
    missing_slots = sorted(required_slots - set(food_slots))
    if missing_slots:
        errors.append(
            "Structured food blueprints are missing canonical meal slots: "
            + ", ".join(missing_slots)
        )

    return {
        "status": "fail" if errors else "pass",
        "family_count": family_count,
        "minimum_family_count": minimum_family_count,
        "batch_counts": dict(sorted(batch_counts.items())),
        "goal_counting_weekly_frequency_estimates": dict(
            sorted(goal_frequency_totals.items())
        ),
        "goal_counting_family_counts": dict(sorted(goal_counting_families.items())),
        "goal_support_family_counts": dict(sorted(goal_support_families.items())),
        "food_slot_counts": dict(sorted(food_slots.items())),
        "errors": errors,
        "warnings": warnings,
    }
