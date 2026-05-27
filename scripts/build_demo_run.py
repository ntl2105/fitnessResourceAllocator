from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.generation.profile_brief import write_member_profile_brief  # noqa: E402


def main() -> None:
    commands = [
        [sys.executable, "scripts/flatten_action_plan.py"],
        [sys.executable, "scripts/validate_data.py"],
        [sys.executable, "scripts/run_scheduler.py"],
        [sys.executable, "src/calendar_view.py"],
    ]
    for command in commands:
        subprocess.run(command, cwd=PROJECT_ROOT, check=True)
    write_member_profile_brief(
        PROJECT_ROOT / "data" / "member_profile.json",
        PROJECT_ROOT / "data" / "runs" / "demo-run" / "00_inputs" / "member_profile_brief.md",
    )


if __name__ == "__main__":
    main()
