from src.models.activity import ActivityPrescription


def build_quality_report(validation_report: dict) -> str:
    checks = validation_report["checks"]
    lines = [
        "# Synthetic Data Quality Report",
        "",
        f"Status: {validation_report['status']}",
        f"Activities: {validation_report['activity_count']}",
        f"Primary activities: {validation_report['primary_activity_count']}",
        f"Modalities: {', '.join(validation_report['modalities_present'])}",
        "",
        "## Validation Checks",
    ]
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
    lines.append("")
    return "\n".join(lines)
