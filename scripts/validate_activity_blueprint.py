from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.generation.activity_blueprint import validate_activity_blueprint  # noqa: E402
from src.io_utils import load_json, save_json  # noqa: E402


def main() -> int:
    data_dir = PROJECT_ROOT / "data"
    blueprint_path = data_dir / "activity_family_blueprint.json"
    report = validate_activity_blueprint(
        blueprint_payload=load_json(blueprint_path),
        budget_payload=load_json(data_dir / "goal_action_budget.json"),
        member_payload=load_json(data_dir / "member_profile.json"),
    )
    report_path = data_dir / "runs" / "demo-run" / "01_validation" / "activity_blueprint_report.json"
    save_json(report_path, report)
    print(
        "Activity blueprint validation "
        f"{report['status']}: {report['family_count']} families"
    )
    if report["errors"]:
        for error in report["errors"]:
            print(f"- {error}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
