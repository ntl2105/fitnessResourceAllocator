from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.assemble_prompts import BATCHES
from src.generation.flatten import action_plan_payload, flatten_activity_families
from src.io_utils import load_json, save_json
from src.models.activity import ActivityFamiliesDocument, ActivityFamily


PROMPTS_DIR = PROJECT_ROOT / "prompts" / "assembled"
GENERATED_DIR = PROJECT_ROOT / "data" / "generated" / "stage05_activity_families"
BATCH_DIR = GENERATED_DIR / "batches"
DATA_DIR = PROJECT_ROOT / "data"


def load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", maxsplit=1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def batch_by_id(batch_id: str) -> tuple[str, str, str, int, str]:
    for batch in BATCHES:
        if batch[0] == batch_id:
            return batch
    raise ValueError(f"Unknown batch id: {batch_id}")


def selected_batches(batch_ids: list[str] | None) -> list[tuple[str, str, str, int, str]]:
    if not batch_ids:
        return BATCHES
    return [batch_by_id(batch_id) for batch_id in batch_ids]


def response_text(response: Any) -> str:
    text = getattr(response, "output_text", None)
    if text:
        return text
    chunks: list[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            value = getattr(content, "text", None)
            if value:
                chunks.append(value)
    if chunks:
        return "\n".join(chunks)
    raise ValueError("OpenAI response did not contain text output.")


def parse_json_response(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return json.loads(stripped)


def validate_batch(payload: dict[str, Any]) -> ActivityFamiliesDocument:
    document = ActivityFamiliesDocument.model_validate(payload)
    if not document.activity_families:
        raise ValueError("Generated batch contains no activity families.")
    missing_contract = []
    for family in document.activity_families:
        if not family.care_domain:
            missing_contract.append(f"{family.activity_family_id}: care_domain")
        if not family.family_target:
            missing_contract.append(f"{family.activity_family_id}: family_target")
        if not family.goal_action_ids:
            missing_contract.append(f"{family.activity_family_id}: goal_action_ids")
    if missing_contract:
        raise ValueError(
            "Generated batch is missing required Stage 05 family fields: "
            + ", ".join(missing_contract)
        )
    return document


def validate_batch_counts(
    document: ActivityFamiliesDocument,
    *,
    batch_id: str,
    expected_family_count: int,
) -> None:
    family_count = len(document.activity_families)
    activity_count = len(document.flattened_activities())
    minimum_activity_count = expected_family_count * 2
    if family_count != expected_family_count:
        raise ValueError(
            f"{batch_id} generated {family_count} families; expected "
            f"{expected_family_count}."
        )
    if activity_count < minimum_activity_count:
        raise ValueError(
            f"{batch_id} generated {activity_count} scheduler-facing activities; "
            f"expected at least {minimum_activity_count}."
        )


def metadata_payload(
    *,
    batch_id: str,
    prompt_path: Path,
    model: str,
    response: Any,
    raw_response_path: Path,
    candidate_path: Path,
    accepted_batch_path: Path,
    document: ActivityFamiliesDocument,
) -> dict[str, Any]:
    activities = document.flattened_activities()
    modality_counts: dict[str, int] = {}
    for activity in activities:
        modality_counts[activity.activity_type.value] = (
            modality_counts.get(activity.activity_type.value, 0) + 1
        )
    return {
        "stage": "05_activity_family_batch",
        "batch": batch_id,
        "prompt": str(prompt_path.relative_to(PROJECT_ROOT)),
        "model": model,
        "response_id": getattr(response, "id", None),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "raw_response_path": str(raw_response_path.relative_to(PROJECT_ROOT)),
        "candidate_path": str(candidate_path.relative_to(PROJECT_ROOT)),
        "accepted_batch_path": str(accepted_batch_path.relative_to(PROJECT_ROOT)),
        "validation": {
            "family_count": len(document.activity_families),
            "activity_count": len(activities),
            "primary_count": sum(1 for activity in activities if activity.is_primary),
            "modality_counts": modality_counts,
        },
        "passed": True,
    }


def generate_batch(
    client: OpenAI,
    batch_id: str,
    model: str,
    suffix: str,
    max_output_tokens: int,
    request_timeout: float,
) -> Path:
    prompt_path = PROMPTS_DIR / f"05_activity_family_batch_{batch_id}.prompt.md"
    prompt_text = prompt_path.read_text(encoding="utf-8")
    response = client.responses.create(
        model=model,
        input=prompt_text,
        temperature=0.2,
        max_output_tokens=max_output_tokens,
        timeout=request_timeout,
    )
    text = response_text(response)
    payload = parse_json_response(text)
    document = validate_batch(payload)
    validate_batch_counts(
        document,
        batch_id=batch_id,
        expected_family_count=batch_by_id(batch_id)[3],
    )

    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    suffix_part = f"_{suffix}" if suffix else ""
    raw_response_path = GENERATED_DIR / f"raw_response_{batch_id}{suffix_part}.txt"
    candidate_path = BATCH_DIR / f"batch_{batch_id}{suffix_part}_candidate.json"
    accepted_batch_path = BATCH_DIR / f"batch_{batch_id}.json"
    metadata_path = GENERATED_DIR / f"metadata_{batch_id}{suffix_part}.json"

    raw_response_path.write_text(text, encoding="utf-8")
    save_json(candidate_path, payload)
    save_json(accepted_batch_path, payload)
    save_json(
        metadata_path,
        metadata_payload(
            batch_id=batch_id,
            prompt_path=prompt_path,
            model=model,
            response=response,
            raw_response_path=raw_response_path,
            candidate_path=candidate_path,
            accepted_batch_path=accepted_batch_path,
            document=document,
        ),
    )
    return accepted_batch_path


def merge_accepted_batches() -> None:
    families: list[ActivityFamily] = []
    for batch_id, *_ in BATCHES:
        path = BATCH_DIR / f"batch_{batch_id}.json"
        document = ActivityFamiliesDocument.model_validate(load_json(path))
        families.extend(document.activity_families)
    payload = {
        "activity_families": [
            family.model_dump(mode="json", exclude_none=True) for family in families
        ]
    }
    save_json(DATA_DIR / "activity_families.json", payload)
    activities = flatten_activity_families(families)
    save_json(DATA_DIR / "action_plan.json", action_plan_payload(activities))
    save_json(
        GENERATED_DIR / "merge_summary.json",
        {
            "merged_at": datetime.now(timezone.utc).isoformat(),
            "batch_count": len(BATCHES),
            "family_count": len(families),
            "activity_count": len(activities),
            "primary_count": sum(1 for activity in activities if activity.is_primary),
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gpt-4.1")
    parser.add_argument("--suffix", default="regen")
    parser.add_argument("--max-output-tokens", type=int, default=24000)
    parser.add_argument("--request-timeout", type=float, default=240.0)
    parser.add_argument("--batch", action="append", dest="batches")
    parser.add_argument("--merge", action="store_true")
    args = parser.parse_args()

    load_env_file(PROJECT_ROOT / ".env")
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")

    client = OpenAI()
    for batch_id, *_ in selected_batches(args.batches):
        print(f"Generating {batch_id} with {args.model}...", flush=True)
        path = generate_batch(
            client,
            batch_id=batch_id,
            model=args.model,
            suffix=args.suffix,
            max_output_tokens=args.max_output_tokens,
            request_timeout=args.request_timeout,
        )
        print(f"Generated {batch_id}: {path.relative_to(PROJECT_ROOT)}")

    if args.merge:
        merge_accepted_batches()
        print("Merged accepted batches into data/activity_families.json and data/action_plan.json")


if __name__ == "__main__":
    main()
