from collections import Counter
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.io_utils import load_json, save_json  # noqa: E402
from src.calendar_audit import build_constraint_audit  # noqa: E402
from src.models.schedule import CalendarRow  # noqa: E402


RUN_DIR = PROJECT_ROOT / "data" / "runs" / "demo-run"
SCHEDULING_PLAN_PATH = RUN_DIR / "03_scheduling" / "personalized_plan.json"
CALENDAR_DIR = RUN_DIR / "04_calendar"


def load_calendar_rows(plan_path: str | Path) -> tuple[list[CalendarRow], dict]:
    plan = load_json(plan_path)
    raw_rows = plan.get("calendar_rows", [])
    rows = [CalendarRow.model_validate(row) for row in raw_rows]
    return rows, plan.get("metadata", {})


def _count_substitutions(rows: list[CalendarRow]) -> int:
    return sum(1 for row in rows if row.substitution_status != "primary")


def _count_remote_rows(rows: list[CalendarRow]) -> int:
    return sum(1 for row in rows if row.mode == "remote")


def _count_travel_hotel_rows(rows: list[CalendarRow]) -> int:
    return sum(1 for row in rows if row.location_id == "travel_hotel")


def build_summary(rows: list[CalendarRow], metadata: dict | None = None) -> str:
    metadata = metadata or {}
    activity_counts = Counter(str(row.activity_type) for row in rows)
    load_counts = Counter(row.load_level for row in rows)
    mode_counts = Counter(row.mode for row in rows)
    missing_trace_count = sum(1 for row in rows if not row.trace_id)
    compact_group_count = len({row.compact_group_key for row in rows if row.compact_group_key})

    if rows:
        first_date = min(row.date for row in rows).isoformat()
        last_date = max(row.date for row in rows).isoformat()
        date_range = f"{first_date} to {last_date}"
    else:
        date_range = "n/a"

    lines = [
        "# Calendar Summary",
        "",
        f"Total rows: {len(rows)}",
        f"Substitutions: {_count_substitutions(rows)}",
        f"Remote rows: {_count_remote_rows(rows)}",
        f"Travel hotel rows: {_count_travel_hotel_rows(rows)}",
        f"Date range: {date_range}",
        "",
        "## Activity Type Counts",
    ]
    if activity_counts:
        lines.extend(
            f"- {activity_type}: {count}"
            for activity_type, count in sorted(activity_counts.items())
        )
    else:
        lines.append("- none: 0")

    lines.extend(["", "## Audit Notes"])
    if metadata:
        scheduled_count = metadata.get("scheduled_count", "n/a")
        unscheduled_count = metadata.get("unscheduled_count", "n/a")
        scheduler = metadata.get("scheduler", "n/a")
        lines.extend(
            [
                f"- Scheduler: {scheduler}",
                f"- Scheduled tasks: {scheduled_count}",
                f"- Unscheduled tasks: {unscheduled_count}",
            ]
        )
    lines.extend(
        [
            f"- Calendar compact groups: {compact_group_count}",
            f"- Rows missing trace IDs: {missing_trace_count}",
            "- Mode counts: "
            + (
                ", ".join(f"{mode}={count}" for mode, count in sorted(mode_counts.items()))
                if mode_counts
                else "none"
            ),
            "- Load counts: "
            + (
                ", ".join(f"{load}={count}" for load, count in sorted(load_counts.items()))
                if load_counts
                else "none"
            ),
            "- Calendar rows are validated against src.models.schedule.CalendarRow before export.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_calendar_artifacts(
    plan_path: str | Path = SCHEDULING_PLAN_PATH,
    output_dir: str | Path = CALENDAR_DIR,
) -> list[CalendarRow]:
    rows, metadata = load_calendar_rows(plan_path)
    destination = Path(output_dir)
    save_json(
        destination / "calendar_rows.json",
        [row.model_dump(mode="json") for row in rows],
    )
    audit = build_constraint_audit(
        [row.model_dump(mode="json") for row in rows],
        load_json(RUN_DIR / "00_inputs" / "availability.json"),
        load_json(RUN_DIR / "00_inputs" / "resource_universe.json"),
    )
    save_json(destination / "constraint_violations.json", audit)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "summary_report.md").write_text(
        build_summary(rows, metadata), encoding="utf-8"
    )
    return rows


def main() -> None:
    rows = write_calendar_artifacts()
    print(f"Wrote {len(rows)} calendar rows to {CALENDAR_DIR}")


if __name__ == "__main__":
    main()
