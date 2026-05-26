from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.generation.validate import write_validation_artifacts  # noqa: E402


def main() -> int:
    report = write_validation_artifacts(PROJECT_ROOT / "data")
    print(
        "Validation "
        f"{report['status']}: {report['activity_count']} activities, "
        f"{report['primary_activity_count']} primary"
    )
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
