import json
import subprocess
import sys
from pathlib import Path

from src.generation.activity_blueprint import validate_activity_blueprint


def _blueprint(
    family_id: str,
    batch_id: str,
    action_id: str,
    *,
    activity_type: str = "fitness",
    counts: bool = True,
    weekly_estimate: float = 1,
    meal_slot: str | None = None,
    travel_context: bool = False,
    substitution_count: int = 1,
) -> dict:
    return {
        "activity_family_id": family_id,
        "batch_id": batch_id,
        "goal_action_ids": [action_id],
        "primary_role": "core" if counts else "support",
        "primary_activity_type": activity_type,
        "primary_intent": meal_slot or "core_action",
        "primary_counts_toward_weekly_target": counts,
        "primary_frequency": {"type": "weekly", "count": weekly_estimate},
        "primary_weekly_frequency_estimate": weekly_estimate,
        "meal_slot": meal_slot,
        "phase_scope": ["phase_marcus_001"],
        "location_strategy": "home",
        "substitution_count": substitution_count,
        "substitution_reason_codes": ["time_conflict"] if substitution_count else [],
        "travel_context": travel_context,
        "semantic_notes": ["test blueprint"],
    }


def test_activity_blueprint_validator_accepts_budgeted_shape(load_seed):
    budget = load_seed("goal_action_budget.json")
    member = load_seed("member_profile.json")
    blueprints = []
    batch_budgets = {
        item["batch_id"]: item["primary_family_budget"]
        for item in budget["batch_budgets"]
    }
    core_actions = [
        ("ga_structured_meals_weekly", "food", "breakfast", 0.25),
        ("ga_structured_meals_weekly", "food", "lunch", 0.25),
        ("ga_structured_meals_weekly", "food", "dinner", 0.25),
        ("ga_aerobic_conditioning_weekly", "fitness", None, 0.25),
        ("ga_strength_sessions_weekly", "fitness", None, 0.25),
        ("ga_sleep_recovery_weekly", "therapy", None, 0.25),
        ("ga_clinical_review_3month", "consultation", None, 0.25),
    ]
    action_index = 0
    for batch_id, count in batch_budgets.items():
        for item_index in range(count):
            if action_index < len(core_actions):
                action_id, activity_type, slot, weekly_estimate = core_actions[action_index]
                counts = True
            else:
                action_id = "ga_adherence_support_weekly"
                activity_type = "medication"
                slot = None
                weekly_estimate = 0
                counts = False
            blueprints.append(
                _blueprint(
                    f"fam_{batch_id}_{item_index}",
                    batch_id,
                    action_id,
                    activity_type=activity_type,
                    counts=counts,
                    weekly_estimate=weekly_estimate,
                    meal_slot=slot,
                    travel_context=False,
                )
            )
            action_index += 1

    report = validate_activity_blueprint(
        {"activity_family_blueprints": blueprints},
        budget,
        member,
    )

    assert report["status"] == "pass"
    assert report["family_count"] == budget["minimum_primary_family_count"]
    assert set(report["food_slot_counts"]) == {"breakfast", "lunch", "dinner"}


def test_activity_blueprint_validator_rejects_overproduced_cardio(load_seed):
    budget = load_seed("goal_action_budget.json")
    member = load_seed("member_profile.json")
    blueprints = []
    for item in budget["batch_budgets"]:
        for item_index in range(item["primary_family_budget"]):
            blueprints.append(
                _blueprint(
                    f"fam_{item['batch_id']}_{item_index}",
                    item["batch_id"],
                    "ga_aerobic_conditioning_weekly",
                    weekly_estimate=1,
                )
            )

    report = validate_activity_blueprint(
        {"activity_family_blueprints": blueprints},
        budget,
        member,
    )

    assert report["status"] == "fail"
    assert any("ga_aerobic_conditioning_weekly" in error for error in report["errors"])


def test_activity_blueprint_validator_accepts_goal_action_ids_and_family_target():
    budget = {
        "minimum_primary_family_count": 1,
        "batch_budgets": [
            {"batch_id": "001_metabolic_nutrition", "primary_family_budget": 1}
        ],
        "goal_action_budgets": [
            {
                "goal_action_id": "ga_structured_meals",
                "primary_family_budget": 1,
                "max_counting_primary_weekly_frequency": 3,
                "canonical_meal_slots": ["breakfast"],
            }
        ],
    }
    member = {"goal_actions": [{"goal_action_id": "ga_structured_meals"}]}
    blueprint = _blueprint(
        "fam_nutrition_001",
        "001_metabolic_nutrition",
        "ga_structured_meals",
        activity_type="food",
        meal_slot="breakfast",
    )
    blueprint["goal_action_ids"] = ["ga_structured_meals"]
    blueprint["care_domain"] = "metabolic_nutrition"
    blueprint["family_target"] = {
        "goal_action_id": "ga_structured_meals",
        "period": "weekly",
        "target_units": 3,
        "substitutions_count": True,
    }

    report = validate_activity_blueprint(
        {"activity_family_blueprints": [blueprint]},
        budget,
        member,
    )

    assert report["status"] == "pass"


def test_activity_blueprint_validator_rejects_mismatched_count_self_check():
    budget = {
        "minimum_primary_family_count": 1,
        "batch_budgets": [
            {"batch_id": "001_metabolic_nutrition", "primary_family_budget": 1}
        ],
        "goal_action_budgets": [
            {
                "goal_action_id": "ga_structured_meals",
                "primary_family_budget": 1,
                "max_counting_primary_weekly_frequency": 3,
                "canonical_meal_slots": ["breakfast"],
            }
        ],
    }
    member = {"goal_actions": [{"goal_action_id": "ga_structured_meals"}]}
    blueprint = _blueprint(
        "fam_nutrition_001",
        "001_metabolic_nutrition",
        "ga_structured_meals",
        activity_type="food",
        meal_slot="breakfast",
    )
    blueprint["care_domain"] = "metabolic_nutrition"
    blueprint["family_target"] = {
        "goal_action_id": "ga_structured_meals",
        "period": "weekly",
        "target_units": 3,
        "substitutions_count": True,
    }

    report = validate_activity_blueprint(
        {
            "activity_family_blueprints": [blueprint],
            "count_self_check": {"001_metabolic_nutrition": 2, "total": 2},
        },
        budget,
        member,
    )

    assert report["status"] == "fail"
    assert any("count_self_check" in error for error in report["errors"])


def test_assemble_prompts_writes_blueprint_prompt_and_batch_budget():
    subprocess.run(
        [sys.executable, "scripts/assemble_prompts.py"],
        check=True,
    )

    blueprint_prompt = open(
        "prompts/assembled/05A_activity_family_blueprint.prompt.md",
        encoding="utf-8",
    ).read()
    assembled = Path("prompts/assembled")
    batch_paths = sorted(assembled.glob("05_activity_family_batch_*.prompt.md"))
    batch_prompt = (assembled / "05_activity_family_batch_001_metabolic_nutrition.prompt.md").read_text(
        encoding="utf-8"
    )

    assert "goal_action_budget.json" in blueprint_prompt
    assert [path.name for path in batch_paths] == [
        "05_activity_family_batch_001_metabolic_nutrition.prompt.md",
        "05_activity_family_batch_002_cardiorespiratory_fitness.prompt.md",
        "05_activity_family_batch_003_strength_mobility_pain.prompt.md",
        "05_activity_family_batch_004_recovery_sleep_stress.prompt.md",
        "05_activity_family_batch_005_clinical_review_measurement.prompt.md",
    ]
    assert "Approved activity family blueprints for this batch" in batch_prompt
    assert "Care domain" in batch_prompt
    assert "family_target" in batch_prompt
    assert "primary need -> availability/resources -> primary activity -> same-family substitution" in batch_prompt
    assert "load adjustment" in batch_prompt
    assert "provider_unavailable" in batch_prompt
    assert "facility_unavailable" in batch_prompt
    assert "Minimum scheduler-facing activities in this batch: 24" in batch_prompt
    assert "Each batch should contribute enough substitutions" in batch_prompt
    assert '"period": "3_month"' in batch_prompt


def test_stage05_prompts_do_not_expose_legacy_weekly_goal_action_contract():
    subprocess.run(
        [sys.executable, "scripts/assemble_prompts.py"],
        check=True,
    )

    assembled = Path("prompts/assembled")
    prompt_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            assembled / "05A_activity_family_blueprint.prompt.md",
            *sorted(assembled.glob("05_activity_family_batch_*.prompt.md")),
        ]
    )

    legacy_terms = [
        "weekly_goal_actions",
        "weekly_goal_action_id",
        "weekly_goal_action_ids",
        "target_per_week",
        "wga_",
    ]
    assert not any(term in prompt_text for term in legacy_terms)


def test_blueprint_budget_file_is_valid_json():
    with open("data/goal_action_budget.json", encoding="utf-8") as budget_file:
        budget = json.load(budget_file)

    assert budget["minimum_primary_family_count"] == 50
    assert sum(item["primary_family_budget"] for item in budget["batch_budgets"]) == 50
    assert [item["batch_id"] for item in budget["batch_budgets"]] == [
        "001_metabolic_nutrition",
        "002_cardiorespiratory_fitness",
        "003_strength_mobility_pain",
        "004_recovery_sleep_stress",
        "005_clinical_review_measurement",
    ]
