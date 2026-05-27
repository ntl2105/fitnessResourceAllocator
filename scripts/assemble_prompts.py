from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROMPTS = PROJECT_ROOT / "prompts"
DATA = PROJECT_ROOT / "data"

BATCHES = [
    (
        "001_metabolic_nutrition",
        "b01_nutrition",
        "metabolic nutrition, structured meals, meal-source logic, supplements or medication tied to food, CGM or hydration support, and travel meal substitutions",
        12,
        "1-100",
    ),
    (
        "002_cardiorespiratory_fitness",
        "b02_cardio",
        "cardiorespiratory fitness, zone 2 work, swimming, cycling, rowing, walking, metabolic conditioning, and travel-safe aerobic substitutions",
        10,
        "101-180",
    ),
    (
        "003_strength_mobility_pain",
        "b03_strength",
        "strength, mobility, knee-safe training, physiotherapy-informed pain resilience, hotel or home substitutions, and lower-load adjustments",
        10,
        "181-260",
    ),
    (
        "004_recovery_sleep_stress",
        "b04_recovery",
        "recovery, sleep, fatigue management, stress regulation, evening routines, post-travel adjustment, and therapy modalities",
        8,
        "261-330",
    ),
    (
        "005_clinical_review_measurement",
        "b05_clinical",
        "clinical review, lab measurements, fasting prerequisites, biometric checks, physician and dietitian review, physiotherapy reassessment, trainer handoff, and care coordination",
        10,
        "331-430",
    ),
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def json_block(value: Any) -> str:
    return "```json\n" + json.dumps(value, indent=2, sort_keys=True) + "\n```"


def section(title: str, body: str) -> str:
    return f"## {title}\n\n{body.strip()}\n"


def write_prompt(path: Path, title: str, parts: list[tuple[str, str]]) -> None:
    body = [f"# Assembled Prompt: {title}", "", "Send this prompt to OpenAI.", ""]
    for heading, content in parts:
        body.extend(["---", "", section(heading, content)])
    path.write_text("\n".join(body).strip() + "\n", encoding="utf-8")


def base_parts() -> list[tuple[str, str]]:
    return [
        ("System Role", read(PROMPTS / "fragments/system_role.prompt.md")),
        ("Client Profile Rules", read(PROMPTS / "fragments/client_profile.prompt.md")),
        ("Realism Rules", read(PROMPTS / "fragments/realism_rules.prompt.md")),
    ]


def assemble_stage_01(out: Path) -> None:
    write_prompt(
        out / "01_member_profile.prompt.md",
        "Stage 01 Member Profile",
        [
            *base_parts(),
            ("Stage Instructions", read(PROMPTS / "stages/01_member_profile.prompt.md")),
            ("Original Persona", read(PROMPTS / "inputs/original_persona.md")),
            ("One-Shot Structural Example", read(PROMPTS / "examples/member_profile.one_shot_example.json")),
        ],
    )


def assemble_stage_02(out: Path) -> None:
    write_prompt(
        out / "02_resource_universe.prompt.md",
        "Stage 02 Resource Universe",
        [
            *base_parts(),
            ("Resource Universe Rules", read(PROMPTS / "fragments/resource_universe.prompt.md")),
            ("Stage Instructions", read(PROMPTS / "stages/02_resource_universe.prompt.md")),
            ("member_profile.json", json_block(load_json(DATA / "member_profile.json"))),
        ],
    )


def assemble_stage_03(out: Path) -> None:
    write_prompt(
        out / "03_known_frictions.prompt.md",
        "Stage 03 Known Frictions",
        [
            *base_parts(),
            ("Known Friction Rules", read(PROMPTS / "fragments/known_frictions.prompt.md")),
            ("Stage Instructions", read(PROMPTS / "stages/03_known_frictions.prompt.md")),
            ("member_profile.json", json_block(load_json(DATA / "member_profile.json"))),
            ("resource_universe.json", json_block(load_json(DATA / "resource_universe.json"))),
        ],
    )


def assemble_stage_04(out: Path) -> None:
    write_prompt(
        out / "04_availability.prompt.md",
        "Stage 04 Availability Patterns",
        [
            *base_parts(),
            ("Availability Context Rules", read(PROMPTS / "fragments/availability_context.prompt.md")),
            ("Stage Instructions", read(PROMPTS / "stages/04_availability.prompt.md")),
            ("member_profile.json", json_block(load_json(DATA / "member_profile.json"))),
            ("resource_universe.json", json_block(load_json(DATA / "resource_universe.json"))),
            ("known_frictions.json", json_block(load_json(DATA / "known_frictions.json"))),
        ],
    )


def activity_family_summaries(before_prefix: str | None = None) -> list[dict[str, Any]]:
    payload = load_json(DATA / "activity_families.json")
    summaries = []
    for family in payload.get("activity_families", []):
        family_id = family.get("activity_family_id", "")
        if before_prefix and family_id >= before_prefix:
            continue
        primary = family.get("primary_activity", {})
        summaries.append(
            {
                "activity_family_id": family_id,
                "intent": family.get("intent"),
                "primary_activity_id": primary.get("activity_id"),
                "primary_title": primary.get("title"),
                "activity_type": primary.get("activity_type"),
                "meal_slot": primary.get("meal_slot"),
                "allowed_locations": primary.get("allowed_locations", []),
                "goal_action_ids": family.get("goal_action_ids", []),
            }
        )
    return summaries


def activity_blueprints_for_batch(batch_id: str) -> list[dict[str, Any]]:
    path = DATA / "activity_family_blueprint.json"
    if not path.is_file():
        return []
    payload = load_json(path)
    return [
        blueprint
        for blueprint in payload.get("activity_family_blueprints", [])
        if blueprint.get("batch_id") == batch_id
    ]


def assemble_stage_05a(out: Path) -> None:
    write_prompt(
        out / "05A_activity_family_blueprint.prompt.md",
        "Stage 05A Activity Family Blueprint",
        [
            ("System Role", read(PROMPTS / "fragments/system_role.prompt.md")),
            ("Client Profile Rules", read(PROMPTS / "fragments/client_profile.prompt.md")),
            ("Realism Rules", read(PROMPTS / "fragments/realism_rules.prompt.md")),
            ("member_profile.json", json_block(load_json(DATA / "member_profile.json"))),
            ("resource_universe.json", json_block(load_json(DATA / "resource_universe.json"))),
            ("known_frictions.json", json_block(load_json(DATA / "known_frictions.json"))),
            (
                "goal_action_budget.json",
                json_block(load_json(DATA / "goal_action_budget.json")),
            ),
            ("Stage Instructions", read(PROMPTS / "stages/05A_activity_family_blueprint.prompt.md")),
        ],
    )


def assemble_stage_05(out: Path) -> None:
    for stale_prompt in out.glob("05_activity_family_batch_*.prompt.md"):
        stale_prompt.unlink()
    for batch_id, prefix, theme, family_count, priority_range in BATCHES:
        minimum_scheduler_activities = family_count * 2
        blueprints = activity_blueprints_for_batch(batch_id)
        blueprint_text = (
            json_block(blueprints)
            if blueprints
            else "No approved blueprint file found yet. Generate and validate `data/activity_family_blueprint.json` with Stage 05A before treating this prompt as final."
        )
        scope = f"""# Batch Scope

Batch ID prefix: `{prefix}`.

Care domain: {batch_id}.

Theme: {theme}.

Generate exactly {family_count} activity families. Each family must have exactly one primary activity. Include 0-3 substitutions only when realistic.

Minimum scheduler-facing activities in this batch: {minimum_scheduler_activities}.

Priority range: {priority_range}.

Existing activity summaries from previous accepted batches:

{json_block(activity_family_summaries(prefix))}

Approved activity family blueprints for this batch:

{blueprint_text}

Target counts remaining: final merged board needs at least 100 scheduler-facing activities from activity families across all accepted care-domain batches. This batch must provide at least {minimum_scheduler_activities} scheduler-facing activities while preserving exactly {family_count} families. Use the requested prefix exactly and avoid duplicate activity/family IDs.

Every family must include `care_domain` and `family_target`. The family target must use a weekly or 3-month period, map back to a member goal action, and state whether substitutions count toward the same target.
"""
        write_prompt(
            out / f"05_activity_family_batch_{batch_id}.prompt.md",
            f"Stage 05 Activity Family Batch {batch_id}",
            [
                ("System Role", read(PROMPTS / "fragments/system_role.prompt.md")),
                ("Activity Schema Rules", read(PROMPTS / "fragments/activity_schema.prompt.md")),
                ("Batch Instructions", read(PROMPTS / "fragments/batch_instructions.prompt.md")),
                ("Client Profile Rules", read(PROMPTS / "fragments/client_profile.prompt.md")),
                ("Realism Rules", read(PROMPTS / "fragments/realism_rules.prompt.md")),
                ("member_profile.json", json_block(load_json(DATA / "member_profile.json"))),
                ("resource_universe.json", json_block(load_json(DATA / "resource_universe.json"))),
                ("known_frictions.json", json_block(load_json(DATA / "known_frictions.json"))),
                (
                    "goal_action_budget.json",
                    json_block(load_json(DATA / "goal_action_budget.json")),
                ),
                ("Batch Scope", scope),
                ("Stage Instructions", read(PROMPTS / "stages/05_activity_family_batch.prompt.md")),
            ],
        )


def assemble_stage_06(out: Path) -> None:
    write_prompt(
        out / "06_activity_board_review.prompt.md",
        "Stage 06 Activity Board Review",
        [
            ("System Role", read(PROMPTS / "fragments/system_role.prompt.md")),
            ("Stage Instructions", read(PROMPTS / "stages/06_activity_board_review.prompt.md")),
            ("member_profile.json", json_block(load_json(DATA / "member_profile.json"))),
            ("resource_universe.json", json_block(load_json(DATA / "resource_universe.json"))),
            ("known_frictions.json", json_block(load_json(DATA / "known_frictions.json"))),
            ("activity_families.json", json_block(load_json(DATA / "activity_families.json"))),
            ("action_plan.json", json_block(load_json(DATA / "action_plan.json"))),
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=PROMPTS / "assembled")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    assemble_stage_01(args.out)
    assemble_stage_02(args.out)
    assemble_stage_03(args.out)
    assemble_stage_04(args.out)
    assemble_stage_05a(args.out)
    assemble_stage_05(args.out)
    assemble_stage_06(args.out)
    print(f"Wrote assembled prompts to {args.out}")


if __name__ == "__main__":
    main()
