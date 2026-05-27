from pathlib import Path
from typing import Any

from src.io_utils import load_json


def _join_values(values: list[Any]) -> str:
    return ", ".join(str(value) for value in values) if values else "none"


def _format_time_window(values: list[str]) -> str:
    return ", ".join(values) if values else "not specified"


def _format_work_hours(profile: dict[str, Any]) -> list[str]:
    work_hours = profile.get("typical_work_hours", {})
    lines = []
    for label, hours in work_hours.items():
        display_label = label.replace("_", " ").title()
        if isinstance(hours, dict):
            raw_start = hours.get("start")
            raw_end = hours.get("end")
            notes = hours.get("notes")
            if raw_start is None and raw_end is None:
                detail = f"{display_label}: off"
            else:
                start = raw_start or "off"
                end = raw_end or "off"
                detail = f"{display_label}: {start}-{end}"
            if notes:
                detail += f" ({notes})"
        else:
            detail = f"{display_label}: {hours}"
        lines.append(f"- {detail}")
    return lines


def _format_goals(profile: dict[str, Any]) -> list[str]:
    lines = []
    sorted_goals = sorted(
        enumerate(profile.get("goals", []), start=1),
        key=lambda item: item[1].get("priority", item[0]),
    )
    for fallback_priority, goal in sorted_goals:
        priority = goal.get("priority", fallback_priority)
        name = goal.get("name") or goal.get("label") or goal.get("goal_id")
        description = goal.get("description")
        indicators = goal.get("success_indicators", [])
        weekly_target = goal.get("weekly_target", {})
        detail_parts = []
        if description:
            detail_parts.append(description)
        if indicators:
            detail_parts.append(f"Success indicators: {_join_values(indicators)}.")
        if weekly_target:
            detail_parts.append(
                "Weekly target: "
                f"minimum {weekly_target.get('minimum', 'n/a')}, "
                f"preferred {weekly_target.get('preferred', 'n/a')} "
                f"{weekly_target.get('unit', 'actions')}."
            )
        lines.append(f"{priority}. {name} ({goal.get('goal_id')}): {' '.join(detail_parts)}")
    return lines or ["- No goals supplied."]


def _format_preferences(profile: dict[str, Any]) -> list[str]:
    preferences = profile.get("preferences", {})
    exercise = preferences.get("exercise_timing", {})
    session_length = preferences.get("session_length", {})
    communication = preferences.get("communication_preferences", {})
    if not exercise and preferences.get("exercise_time"):
        exercise = {"preferred": [preferences["exercise_time"]], "acceptable": [], "avoid": []}
    return [
        f"- Morning exercise preference: {_format_time_window(exercise.get('preferred', []))}.",
        f"- Acceptable fallback windows: {_format_time_window(exercise.get('acceptable', []))}.",
        f"- Avoids: {_format_time_window(exercise.get('avoid', []))}.",
        "- Session limits: "
        f"{session_length.get('weekday_max_minutes', 'n/a')} minutes on weekdays, "
        f"{session_length.get('weekend_max_minutes', 'n/a')} minutes on weekends.",
        f"- Training preferences: {_join_values(preferences.get('training_preferences', []))}.",
        f"- Nutrition preferences: {_join_values(preferences.get('nutrition_preferences') or preferences.get('food_preferences', []))}.",
        f"- Consultation preferences: {_join_values(preferences.get('consultation_preferences', []))}.",
        "- Communication style: "
        f"{communication.get('style', 'not specified')}; "
        f"detail level {communication.get('detail_level', 'not specified')}; "
        f"channels {_join_values(communication.get('preferred_channels', []))}.",
    ]


def _format_constraints(profile: dict[str, Any]) -> list[str]:
    constraints = profile.get("constraints", {})
    lines = []
    for physical in constraints.get("physical", []):
        lines.append(
            f"- {physical.get('name')} ({physical.get('severity')}): "
            f"{physical.get('description')} Implications: "
            f"{_join_values(physical.get('implications', []))}."
        )
    for category in ("schedule", "behavioral", "medical_safety"):
        values = constraints.get(category, [])
        if values:
            lines.append(f"- {category.replace('_', ' ').title()}: {_join_values(values)}.")
    for category, values in constraints.items():
        if category in {"physical", "schedule", "behavioral", "medical_safety"}:
            continue
        if isinstance(values, dict):
            lines.append(f"- {category.replace('_', ' ').title()}: {_flatten_mapping(values)}.")
        elif values:
            lines.append(f"- {category.replace('_', ' ').title()}: {_join_values(values)}.")
    return lines or ["- No constraints supplied."]


def _flatten_mapping(mapping: dict[str, Any]) -> str:
    parts = []
    for key, value in mapping.items():
        label = key.replace("_", " ")
        if isinstance(value, dict):
            parts.append(f"{label}: {_flatten_mapping(value)}")
        elif isinstance(value, list):
            parts.append(f"{label}: {_join_values(value)}")
        else:
            parts.append(f"{label}: {value}")
    return "; ".join(parts)


def _format_baseline(profile: dict[str, Any]) -> list[str]:
    metrics = profile.get("baseline_metrics", {})
    body = metrics.get("body_composition", {})
    fitness = metrics.get("fitness", {})
    sleep = metrics.get("sleep", {})
    metabolic = metrics.get("metabolic", {})
    subjective = metrics.get("subjective", {})
    markers = [
        f"{marker.get('name')}: {marker.get('value')}"
        for marker in metabolic.get("synthetic_markers", [])
    ]
    return [
        "- Body composition: "
        f"{body.get('weight_kg', 'n/a')} kg, {body.get('height_cm', 'n/a')} cm, "
        f"estimated body fat {body.get('estimated_body_fat_percent', body.get('body_fat_percent_estimate', 'n/a'))}%, "
        f"waist {body.get('waist_cm', 'n/a')} cm.",
        "- Fitness: "
        f"resting HR {fitness.get('resting_heart_rate_bpm', 'n/a')} bpm, "
        f"VO2max category {fitness.get('estimated_vo2max_category', 'n/a')}, "
        f"strength level {fitness.get('strength_level', metrics.get('strength', 'n/a'))}, "
        f"cardio pattern {fitness.get('cardio_pattern', 'n/a')}.",
        "- Sleep: "
        f"Average sleep duration: {sleep.get('average_sleep_duration_hours', 'n/a')} hours; "
        f"bedtime {sleep.get('average_bedtime', 'n/a')}; "
        f"wake time {sleep.get('wake_time', 'n/a')}; "
        f"main issue {sleep.get('main_issue', 'n/a')}; "
        f"recent sleep score {metrics.get('recent_sleep_score', 'n/a')}.",
        "- Metabolic: "
        f"risk level {metabolic.get('risk_level', metrics.get('metabolic_markers', 'n/a'))}; "
        f"synthetic markers {_join_values(markers)}.",
        "- Subjective energy: "
        f"morning {subjective.get('morning_energy_average', 'n/a')}, "
        f"afternoon {subjective.get('afternoon_energy_average', 'n/a')}, "
        f"travel week {subjective.get('travel_week_energy_average', 'n/a')}.",
    ]


def _format_journey(profile: dict[str, Any]) -> list[str]:
    lines = []
    for phase in profile.get("journey_phases", []):
        lines.append(
            f"- {phase.get('phase_id')} ({phase.get('phase_type')}), "
            f"{phase.get('start_date')} to {phase.get('end_date')}: "
            f"{phase.get('trigger')} Goals: {_join_values(phase.get('primary_goals', []))}. "
            f"Scheduling biases: {_join_values(phase.get('scheduling_biases', []))}."
        )
    return lines or ["- No journey phases supplied."]


def _format_travel(profile: dict[str, Any]) -> list[str]:
    lines = []
    for window in profile.get("travel_windows", []):
        destination = window.get("destination", "destination not specified")
        resources = _join_values(window.get("available_resources") or window.get("facilities", []))
        notes = window.get("notes") or window.get("resource_notes")
        line = (
            f"- {window.get('travel_window_id')}: {window.get('start')} to {window.get('end')} "
            f"({window.get('travel_type', 'planned' if window.get('planned') else 'last-minute')}) in {destination}. "
            f"Available resources: {resources}."
        )
        if notes:
            line += f" {notes}"
        lines.append(line)
    return lines or ["- No travel windows supplied."]


def _format_scheduling_implications(profile: dict[str, Any]) -> list[str]:
    rules = profile.get("scheduling_rules", {})
    return [
        f"- Planning horizon: {rules.get('planning_start_date')} for {rules.get('planning_months')} months.",
        f"- Prefer morning exercise: {rules.get('prefer_morning_exercise', False)}.",
        "- Load guardrails: "
        f"max {rules.get('max_high_load_activities_per_day', rules.get('max_core_sessions_per_day', 'n/a'))} high-load/core activity per day; "
        f"max {rules.get('max_medium_or_high_load_activities_per_day', rules.get('max_training_sessions_per_week', 'n/a'))} medium/high activities per day or training sessions per week.",
        "- Recovery guardrails: "
        f"avoid high intensity after poor sleep below {rules.get('poor_sleep_threshold_hours', 'n/a')} hours; "
        f"avoid heavy lower body for {rules.get('avoid_heavy_lower_body_after_flight_hours', 'n/a')} hours after flights; "
        f"avoid heavy lower body after travel over 3h is {rules.get('avoid_heavy_lower_body_after_travel_over_3h', False)}.",
        f"- Calendar presentation: compact recurring low-complexity tasks is {rules.get('compact_recurring_low_complexity_tasks_in_calendar', rules.get('compact_low_complexity_tasks', False))}.",
    ]


def build_member_profile_brief(profile: dict[str, Any]) -> str:
    lines = [
        f"# Member Profile Brief: {profile.get('name', 'Unknown Member')}",
        "",
        "## Narrative Summary",
        "",
        profile.get("profile_summary")
        or (
            f"{profile.get('name', 'The member')} is a {profile.get('age_range', 'unknown age range')} "
            f"{profile.get('occupation', 'member')} based in timezone {profile.get('timezone', 'unknown')}. "
            "The profile combines goals, constraints, baseline metrics, travel windows, and scheduling rules "
            "into one source of truth for the Resource Allocator demo."
        ),
        "",
        "## Identity And Work Rhythm",
        "",
        f"- Member ID: {profile.get('member_id')}",
        f"- Age range: {profile.get('age_range')}",
        f"- Occupation: {profile.get('occupation')}",
        f"- Timezone: {profile.get('timezone')}",
        *_format_work_hours(profile),
        "",
        "## Goals",
        "",
        *_format_goals(profile),
        "",
        "## Preferences",
        "",
        *_format_preferences(profile),
        "",
        "## Constraints",
        "",
        *_format_constraints(profile),
        "",
        "## Baseline Snapshot",
        "",
        *_format_baseline(profile),
        "",
        "## Journey Timeline",
        "",
        *_format_journey(profile),
        "",
        "## Travel Windows",
        "",
        *_format_travel(profile),
        "",
        "## Scheduling Implications",
        "",
        *_format_scheduling_implications(profile),
        "",
    ]
    return "\n".join(lines)


def write_member_profile_brief(profile_path: str | Path, output_path: str | Path) -> str:
    brief = build_member_profile_brief(load_json(profile_path))
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(brief, encoding="utf-8")
    return brief
