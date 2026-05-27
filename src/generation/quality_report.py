from src.models.activity import ActivityPrescription


def build_quality_report(validation_report: dict) -> str:
    checks = validation_report["checks"]
    lines = [
        "# Synthetic Data Quality Report",
        "",
        f"Status: {validation_report['status']}",
        f"Activities: {validation_report['activity_count']}",
        f"Primary activities: {validation_report['primary_activity_count']}",
        f"Availability blocks: {validation_report.get('availability_block_count', 0)}",
        f"Modalities: {', '.join(validation_report['modalities_present'])}",
        "",
        "## Availability Block Counts",
    ]
    lines.extend(
        f"- {resource_type}: {count}"
        for resource_type, count in sorted(
            validation_report.get("availability_resource_type_counts", {}).items()
        )
    )
    lines.extend(
        [
            "",
            "## Validation Checks",
        ]
    )
    lines.extend(
        f"- {'PASS' if check['passed'] else 'FAIL'}: {name} - {check['message']}"
        for name, check in checks.items()
    )
    lines.append("")
    return "\n".join(lines)


def build_activity_board_review(activities: list[ActivityPrescription]) -> str:
    primary_count = sum(1 for activity in activities if activity.is_primary)
    substitution_count = len(activities) - primary_count
    by_modality: dict[str, int] = {}
    for activity in activities:
        by_modality[activity.activity_type.value] = (
            by_modality.get(activity.activity_type.value, 0) + 1
        )

    lines = [
        "# Activity Board Review",
        "",
        f"Total activities: {len(activities)}",
        f"Primary activities: {primary_count}",
        f"Substitution activities: {substitution_count}",
        "",
        "## Modality Counts",
    ]
    lines.extend(f"- {modality}: {count}" for modality, count in sorted(by_modality.items()))
    lines.extend(
        [
            "",
            "## QA Flags",
        ]
    )
    flags = activity_board_qa_flags(activities)
    lines.extend(f"- {flag}" for flag in flags)
    if not flags:
        lines.append("- No activity-board QA flags detected.")
    lines.append("")
    return "\n".join(lines)


def activity_board_qa_flags(activities: list[ActivityPrescription]) -> list[str]:
    flags: list[str] = []
    flags.extend(duplicate_meal_slot_flags(activities))
    flags.extend(frequency_contradiction_flags(activities))
    flags.extend(orphan_support_activity_flags(activities))
    flags.extend(travel_core_goal_flags(activities))
    flags.extend(substitution_metadata_flags(activities))
    flags.extend(travel_primary_activity_flags(activities))
    return flags


def duplicate_meal_slot_flags(activities: list[ActivityPrescription]) -> list[str]:
    by_slot: dict[str, list[ActivityPrescription]] = {}
    for activity in activities:
        meal_slot = str(getattr(activity, "meal_slot", "") or "").lower()
        if activity.activity_type.value != "food" or not meal_slot or not activity.is_primary:
            continue
        by_slot.setdefault(meal_slot, []).append(activity)

    flags = []
    for meal_slot, slot_activities in sorted(by_slot.items()):
        if len(slot_activities) <= 1:
            continue
        titles = ", ".join(activity.title for activity in slot_activities[:4])
        flags.append(
            f"{meal_slot} has {len(slot_activities)} primary food activities; confirm meal-slot exclusivity and weekly denominator intent: {titles}"
        )
    return flags


def frequency_contradiction_flags(activities: list[ActivityPrescription]) -> list[str]:
    flags = []
    for activity in activities:
        details = (activity.details or "").lower()
        count = activity.frequency.get("count")
        numeric_count = int(count) if isinstance(count, (int, str)) and str(count).isdigit() else 0
        if numeric_count > 1 and ("max 1" in details or "maximum 1" in details):
            flags.append(
                f"{activity.activity_id} frequency count is {count}, but details say max 1."
            )
    return flags


def orphan_support_activity_flags(activities: list[ActivityPrescription]) -> list[str]:
    flags = []
    support_terms = ("prep", "activation", "protocol", "check", "log", "hydration", "supplement")
    for activity in activities:
        text = f"{activity.title} {' '.join(activity.goal_tags)}".lower()
        if not any(term in text for term in support_terms):
            continue
        if activity.dependencies:
            continue
        if any(
            contribution.get("counts_toward_weekly_target") is not False
            for contribution in activity.goal_contributions
        ):
            continue
        flags.append(
            f"{activity.activity_id} looks like support/prep/protocol work but has no dependency link."
        )
    return flags


def travel_core_goal_flags(activities: list[ActivityPrescription]) -> list[str]:
    flags = []
    for activity in activities:
        for contribution in activity.goal_contributions:
            action_id = str(contribution.get("weekly_goal_action_id", "")).lower()
            if "travel" not in action_id:
                continue
            if contribution.get("counts_toward_weekly_target") is False:
                continue
            flags.append(
                f"{activity.activity_id} counts toward travel weekly action {contribution.get('weekly_goal_action_id')}; travel adaptation should usually be substitution logic, not a core denominator."
            )
            break
    return flags


def substitution_metadata_flags(activities: list[ActivityPrescription]) -> list[str]:
    flags = []
    for activity in activities:
        if activity.is_primary:
            continue
        if not getattr(activity, "substitution_for_activity_id", None):
            flags.append(
                f"{activity.activity_id} is a substitution but is missing substitution_for_activity_id."
            )
        if not getattr(activity, "substitution_reason_codes", None):
            flags.append(
                f"{activity.activity_id} is a substitution but is missing substitution_reason_codes."
            )
    return flags


def travel_primary_activity_flags(activities: list[ActivityPrescription]) -> list[str]:
    flags = []
    for activity in activities:
        if not activity.is_primary:
            continue
        text = " ".join(
            [
                activity.activity_id,
                activity.title,
                activity.details or "",
                " ".join(activity.goal_tags),
                " ".join(activity.allowed_locations),
            ]
        ).lower()
        if "travel" not in text and "hotel" not in text:
            continue
        has_counting_underlying_goal = any(
            contribution.get("counts_toward_weekly_target") is not False
            and "travel" not in str(contribution.get("weekly_goal_action_id", "")).lower()
            for contribution in activity.goal_contributions
        )
        if not has_counting_underlying_goal:
            flags.append(
                f"{activity.activity_id} is travel-context primary work; confirm it should not be a substitution under an underlying meal, cardio, strength, recovery, or consultation family."
            )
    return flags
