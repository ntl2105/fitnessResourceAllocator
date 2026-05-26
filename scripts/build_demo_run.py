from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    commands = [
        [sys.executable, "scripts/flatten_action_plan.py"],
        [sys.executable, "scripts/validate_data.py"],
        [sys.executable, "scripts/run_scheduler.py"],
        [sys.executable, "src/calendar_view.py"],
    ]
    for command in commands:
        subprocess.run(command, cwd=PROJECT_ROOT, check=True)


if __name__ == "__main__":
    main()
