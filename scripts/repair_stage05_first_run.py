from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = PROJECT_ROOT / "data" / "generated" / "stage05_activity_families"
BATCH_DIR = GENERATED_DIR / "batches"
DATA_DIR = PROJECT_ROOT / "data"

BATCH_FILES = {
    "001_metabolic_nutrition": "batch_001_metabolic_nutrition.json",
    "002_cardiorespiratory_fitness": "batch_002_cardiorespiratory_fitness.json",
    "003_strength_mobility_pain": "batch_003_strength_mobility_pain.json",
    "004_recovery_sleep_stress": "batch_004_recovery_sleep_stress.json",
    "005_clinical_review_measurement": "batch_005_clinical_review_measurement.json",
}

VARIANTS: list[tuple[str, str, dict[str, Any]]] = [
    (
        "001_metabolic_nutrition",
        "b01_nutrition_fasting_aware_meal_support",
        {
            "suffix": "remote_check",
            "title": "Remote fasting meal timing check",
            "details": "Remote review of fasting timing, hydration, and first-meal plan when lab timing changes or travel creates uncertainty.",
            "allowed_locations": ["remote"],
            "remote_allowed": True,
            "duration_minutes": 10,
            "required_provider_ids": ["provider_remote_coach_01"],
            "reason": ["remote_delivery_needed", "time_conflict"],
            "notes": "Preserves fasting-aware meal timing support when the member is remote or lab timing shifts.",
        },
    ),
    (
        "001_metabolic_nutrition",
        "b01_nutrition_supplement_protocol_support",
        {
            "suffix": "travel_timing",
            "title": "Travel supplement timing review",
            "details": "Travel-compatible supplement timing review tied to the available breakfast or dinner window, without replacing a meal.",
            "allowed_locations": ["remote", "travel_hotel"],
            "remote_allowed": True,
            "duration_minutes": 10,
            "required_provider_ids": ["provider_remote_coach_01"],
            "reason": ["travel_window", "remote_delivery_needed"],
            "notes": "Preserves supplement adherence support when travel disrupts the usual meal window.",
        },
    ),
    (
        "001_metabolic_nutrition",
        "b01_nutrition_travel_meal_adherence_check",
        {
            "suffix": "photo_review",
            "title": "Async travel meal photo review",
            "details": "Asynchronous dietitian or coach review of travel meal photos and notes to keep structured eating aligned with metabolic goals.",
            "allowed_locations": ["remote"],
            "remote_allowed": True,
            "duration_minutes": 10,
            "required_provider_ids": ["provider_dietitian_01"],
            "reason": ["travel_window", "time_conflict"],
            "notes": "Preserves travel meal adherence support when a live check-in cannot be scheduled.",
        },
    ),
    (
        "002_cardiorespiratory_fitness",
        "b02_cardio_remote_coach_progression_review",
        {
            "suffix": "async_log",
            "title": "Async aerobic log review",
            "details": "Coach reviews wearable or session notes asynchronously and adjusts the next aerobic target when schedules prevent a live review.",
            "allowed_locations": ["remote"],
            "remote_allowed": True,
            "duration_minutes": 10,
            "required_provider_ids": ["provider_remote_coach_01"],
            "reason": ["time_conflict", "remote_delivery_needed"],
            "notes": "Preserves aerobic progression support when live coach availability is blocked.",
        },
    ),
    (
        "002_cardiorespiratory_fitness",
        "b02_cardio_hydration_protocol_support",
        {
            "suffix": "hotel_protocol",
            "title": "Hotel-room hydration protocol",
            "details": "Travel-compatible hydration and electrolyte check using hotel-room supplies before or after aerobic work.",
            "allowed_locations": ["travel_hotel"],
            "remote_allowed": False,
            "duration_minutes": 5,
            "required_provider_ids": [],
            "reason": ["travel_window", "facility_unavailable"],
            "notes": "Preserves hydration support when the member is travelling or away from the usual setup.",
        },
    ),
    (
        "003_strength_mobility_pain",
        "b03_strength_trainer_remote_substitution",
        {
            "suffix": "async_plan",
            "title": "Async trainer strength plan",
            "details": "Trainer sends a knee-safe strength plan for self-guided completion when a live remote session cannot be scheduled.",
            "allowed_locations": ["remote", "home", "travel_hotel"],
            "remote_allowed": True,
            "duration_minutes": 15,
            "required_provider_ids": ["provider_trainer_01"],
            "reason": ["provider_unavailable", "time_conflict"],
            "notes": "Preserves strength-session planning when trainer availability or travel blocks live delivery.",
        },
    ),
    (
        "003_strength_mobility_pain",
        "b03_strength_mobility_pain_recovery_checkin",
        {
            "suffix": "pain_note",
            "title": "Async pain recovery note review",
            "details": "Coach or physio reviews pain, fatigue, and travel notes asynchronously and recommends the safest next session option.",
            "allowed_locations": ["remote"],
            "remote_allowed": True,
            "duration_minutes": 10,
            "required_provider_ids": ["provider_physio_01"],
            "reason": ["pain_or_fatigue", "remote_delivery_needed"],
            "notes": "Preserves pain-aware recovery support when a live check-in cannot fit.",
        },
    ),
    (
        "004_recovery_sleep_stress",
        "b04_recovery_sleep_routine_support",
        {
            "suffix": "hotel_wind_down",
            "title": "Hotel sleep wind-down routine",
            "details": "Hotel-room version of the wind-down protocol with breathwork, light mobility, and screen cutoff when Marcus is travelling.",
            "allowed_locations": ["travel_hotel"],
            "remote_allowed": False,
            "duration_minutes": 20,
            "required_provider_ids": [],
            "required_equipment_ids": ["eq_yoga_mat"],
            "reason": ["travel_window"],
            "notes": "Preserves sleep-routine intent when Marcus is away from home.",
        },
    ),
    (
        "004_recovery_sleep_stress",
        "b04_recovery_breathwork_support",
        {
            "suffix": "audio_guided",
            "title": "Audio-guided breathwork session",
            "details": "Self-guided breathwork using a short audio protocol when coach support or a quiet home window is not available.",
            "allowed_locations": ["home", "travel_hotel", "remote"],
            "remote_allowed": True,
            "duration_minutes": 10,
            "required_provider_ids": [],
            "reason": ["time_conflict", "remote_delivery_needed"],
            "notes": "Preserves stress-regulation intent with a lower-friction delivery mode.",
        },
    ),
    (
        "004_recovery_sleep_stress",
        "b04_recovery_remote_coach_recovery_checkin",
        {
            "suffix": "async_sleep_note",
            "title": "Async sleep recovery note review",
            "details": "Remote coach reviews sleep notes and travel context asynchronously, then updates the recovery plan.",
            "allowed_locations": ["remote"],
            "remote_allowed": True,
            "duration_minutes": 10,
            "required_provider_ids": ["provider_remote_coach_01"],
            "reason": ["time_conflict", "travel_window"],
            "notes": "Preserves recovery check-in support when live coach availability is limited.",
        },
    ),
    (
        "005_clinical_review_measurement",
        "b05_clinical_lab_reschedule_coordination",
        {
            "suffix": "facility_change",
            "title": "Alternate lab booking coordination",
            "details": "Care team coordinates an alternate lab booking when the preferred lab or due-week window becomes unavailable.",
            "allowed_locations": ["remote"],
            "remote_allowed": True,
            "duration_minutes": 15,
            "required_provider_ids": ["provider_remote_coach_01"],
            "reason": ["facility_unavailable", "time_conflict"],
            "notes": "Preserves clinical lab coordination when the usual lab slot cannot be used.",
        },
    ),
    (
        "005_clinical_review_measurement",
        "b05_clinical_biometric_review_support",
        {
            "suffix": "async_summary",
            "title": "Async biometric summary review",
            "details": "Care team reviews CGM, sleep, and session notes asynchronously and summarizes flags for physician or dietitian follow-up.",
            "allowed_locations": ["remote"],
            "remote_allowed": True,
            "duration_minutes": 15,
            "required_provider_ids": ["provider_remote_coach_01"],
            "reason": ["remote_delivery_needed", "time_conflict"],
            "notes": "Preserves biometric review support when a live care-team review is not realistic.",
        },
    ),
    (
        "005_clinical_review_measurement",
        "b05_clinical_trainer_physio_handoff",
        {
            "suffix": "async_handoff",
            "title": "Async trainer physio handoff",
            "details": "Trainer and physio exchange knee-pain and load notes asynchronously before the next strength progression.",
            "allowed_locations": ["remote"],
            "remote_allowed": True,
            "duration_minutes": 10,
            "required_provider_ids": ["provider_trainer_01", "provider_physio_01"],
            "reason": ["provider_unavailable", "time_conflict"],
            "notes": "Preserves trainer-physio coordination when both providers cannot meet live.",
        },
    ),
    (
        "005_clinical_review_measurement",
        "b05_clinical_adherence_checkin_support",
        {
            "suffix": "message_check",
            "title": "Message-based adherence check-in",
            "details": "Brief message-based adherence check-in to resolve barriers after missed sessions, travel disruption, or meal-prep gaps.",
            "allowed_locations": ["remote"],
            "remote_allowed": True,
            "duration_minutes": 10,
            "required_provider_ids": ["provider_remote_coach_01"],
            "reason": ["travel_window", "time_conflict"],
            "notes": "Preserves adherence support when the weekly live check-in cannot be scheduled.",
        },
    ),
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def add_variant(family: dict[str, Any], variant: dict[str, Any]) -> None:
    primary = family["primary_activity"]
    sub = copy.deepcopy(primary)
    activity_id = primary["activity_id"].removesuffix("_primary")
    sub["activity_id"] = f"{activity_id}_{variant['suffix']}_sub"
    sub["title"] = variant["title"]
    sub["details"] = variant["details"]
    sub["is_primary"] = False
    sub["substitution_activity_ids"] = []
    sub["substitution_for_activity_id"] = primary["activity_id"]
    sub["substitution_reason_codes"] = variant["reason"]
    sub["substitution_notes"] = variant["notes"]
    sub["allowed_locations"] = variant["allowed_locations"]
    sub["remote_allowed"] = variant["remote_allowed"]
    sub["duration_minutes"] = variant["duration_minutes"]
    sub["required_provider_ids"] = variant["required_provider_ids"]
    if "required_equipment_ids" in variant:
        sub["required_equipment_ids"] = variant["required_equipment_ids"]
    elif "remote" in variant["allowed_locations"] or "travel_hotel" in variant["allowed_locations"]:
        sub["required_equipment_ids"] = []
    sub["priority"] = min(int(primary.get("priority", 0)) + 3 + len(family.get("substitution_activities", [])), 430)
    sub["skip_adjustment"] = {
        "allowed_after_poor_sleep": True,
        "allowed_after_travel": True,
        "notes": "Use when the primary version is blocked by availability, travel, load, or timing.",
    }

    family_target = family.get("family_target", {})
    support_only = (
        family_target.get("support_counts") is False
        and family_target.get("target_units") == 0
    )
    for contribution in sub.get("goal_contributions", []):
        contribution["notes"] = variant["notes"]
        if support_only:
            contribution["counts_toward_weekly_target"] = False
            contribution["value"] = 0
            contribution.setdefault("role", "support")

    family.setdefault("substitution_activities", []).append(sub)
    primary.setdefault("substitution_activity_ids", []).append(sub["activity_id"])
    family.setdefault("substitution_rules", []).append(
        {
            "when": " or ".join(variant["reason"]),
            "prefer_activity_id": sub["activity_id"],
            "reason": variant["notes"],
        }
    )
    family.setdefault("family_validation_notes", []).append(
        "Includes an additional first-run repair substitution to meet the 100+ scheduler-facing activity requirement without adding families."
    )
    if family_target.get("target_units") not in (None, 0):
        family_target["substitutions_count"] = True


def activity_counts(document: dict[str, Any]) -> dict[str, Any]:
    activities = [
        activity
        for family in document["activity_families"]
        for activity in [family["primary_activity"], *family.get("substitution_activities", [])]
    ]
    modality_counts: dict[str, int] = {}
    for activity in activities:
        modality = activity["activity_type"]
        modality_counts[modality] = modality_counts.get(modality, 0) + 1
    return {
        "family_count": len(document["activity_families"]),
        "activity_count": len(activities),
        "primary_count": sum(1 for activity in activities if activity.get("is_primary")),
        "modality_counts": modality_counts,
    }


def main() -> None:
    documents = {
        batch_id: load_json(BATCH_DIR / filename)
        for batch_id, filename in BATCH_FILES.items()
    }
    for batch_id, family_id, variant in VARIANTS:
        families = documents[batch_id]["activity_families"]
        family = next(
            (candidate for candidate in families if candidate["activity_family_id"] == family_id),
            None,
        )
        if family is None:
            raise RuntimeError(f"Missing family {family_id}")
        add_variant(family, variant)

    all_families = []
    all_activities = []
    for batch_id, filename in BATCH_FILES.items():
        document = documents[batch_id]
        save_json(BATCH_DIR / filename, document)
        counts = activity_counts(document)
        metadata_path = GENERATED_DIR / f"metadata_{batch_id}_first.json"
        metadata = load_json(metadata_path)
        metadata["validation"] = counts
        metadata["repaired_after_generation"] = True
        metadata["repair_note"] = (
            "Added same-family substitutions to meet batch activity minimums "
            "after the initial model output under-expanded scheduler-facing activities."
        )
        save_json(metadata_path, metadata)
        all_families.extend(document["activity_families"])

    all_activities = [
        activity
        for family in all_families
        for activity in [family["primary_activity"], *family.get("substitution_activities", [])]
    ]
    save_json(DATA_DIR / "activity_families.json", {"activity_families": all_families})
    save_json(DATA_DIR / "action_plan.json", {"activities": all_activities})
    save_json(
        GENERATED_DIR / "merge_summary.json",
        {
            "merged_at": datetime.now(timezone.utc).isoformat(),
            "batch_count": len(BATCH_FILES),
            "family_count": len(all_families),
            "activity_count": len(all_activities),
            "primary_count": sum(1 for activity in all_activities if activity.get("is_primary")),
            "repaired_after_generation": True,
        },
    )
    print(f"Repaired Stage 05 first run: {len(all_families)} families, {len(all_activities)} activities.")


if __name__ == "__main__":
    main()
