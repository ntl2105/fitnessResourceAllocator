from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.generation.flatten import write_action_plan  # noqa: E402


def main() -> None:
    data_dir = PROJECT_ROOT / "data"
    activities = write_action_plan(
        data_dir / "activity_families.json",
        data_dir / "action_plan.json",
    )
    print(f"Wrote {len(activities)} activities to {data_dir / 'action_plan.json'}")


if __name__ == "__main__":
    main()
