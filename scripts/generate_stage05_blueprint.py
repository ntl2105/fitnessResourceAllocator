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

from scripts.generate_stage05_activity_batches import (  # noqa: E402
    load_env_file,
    parse_json_response,
    response_text,
)
from src.generation.activity_blueprint import validate_activity_blueprint  # noqa: E402
from src.io_utils import load_json, save_json  # noqa: E402


PROMPT_PATH = PROJECT_ROOT / "prompts" / "assembled" / "05A_activity_family_blueprint.prompt.md"
GENERATED_DIR = PROJECT_ROOT / "data" / "generated" / "stage05_activity_blueprint"
DATA_DIR = PROJECT_ROOT / "data"


def metadata_payload(
    *,
    model: str,
    response: Any,
    raw_response_path: Path,
    candidate_path: Path,
    accepted_path: Path | None,
    report_path: Path,
    report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "stage": "05A_activity_family_blueprint",
        "prompt": str(PROMPT_PATH.relative_to(PROJECT_ROOT)),
        "model": model,
        "response_id": getattr(response, "id", None),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "raw_response_path": str(raw_response_path.relative_to(PROJECT_ROOT)),
        "candidate_path": str(candidate_path.relative_to(PROJECT_ROOT)),
        "accepted_path": str(accepted_path.relative_to(PROJECT_ROOT))
        if accepted_path
        else None,
        "report_path": str(report_path.relative_to(PROJECT_ROOT)),
        "validation": report,
        "passed": report["status"] == "pass",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gpt-4.1")
    parser.add_argument("--suffix", default="regen")
    parser.add_argument("--max-output-tokens", type=int, default=20000)
    parser.add_argument("--request-timeout", type=float, default=240.0)
    parser.add_argument("--accept-valid", action="store_true")
    args = parser.parse_args()

    load_env_file(PROJECT_ROOT / ".env")
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")

    prompt_text = PROMPT_PATH.read_text(encoding="utf-8")
    client = OpenAI()
    response = client.responses.create(
        model=args.model,
        input=prompt_text,
        temperature=0.2,
        max_output_tokens=args.max_output_tokens,
        timeout=args.request_timeout,
    )
    text = response_text(response)
    payload = parse_json_response(text)
    report = validate_activity_blueprint(
        blueprint_payload=payload,
        budget_payload=load_json(DATA_DIR / "goal_action_budget.json"),
        member_payload=load_json(DATA_DIR / "member_profile.json"),
    )

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    suffix_part = f"_{args.suffix}" if args.suffix else ""
    raw_response_path = GENERATED_DIR / f"raw_response{suffix_part}.txt"
    candidate_path = GENERATED_DIR / f"activity_family_blueprint{suffix_part}_candidate.json"
    report_path = GENERATED_DIR / f"activity_family_blueprint_report{suffix_part}.json"
    metadata_path = GENERATED_DIR / f"metadata{suffix_part}.json"
    accepted_path = DATA_DIR / "activity_family_blueprint.json" if args.accept_valid and report["status"] == "pass" else None

    raw_response_path.write_text(text, encoding="utf-8")
    save_json(candidate_path, payload)
    save_json(report_path, report)
    if accepted_path:
        save_json(accepted_path, payload)

    save_json(
        metadata_path,
        metadata_payload(
            model=args.model,
            response=response,
            raw_response_path=raw_response_path,
            candidate_path=candidate_path,
            accepted_path=accepted_path,
            report_path=report_path,
            report=report,
        ),
    )
    print(
        "Generated Stage 05A blueprint "
        f"{report['status']}: {report['family_count']} families"
    )
    if report["errors"]:
        for error in report["errors"]:
            print(f"- {error}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
