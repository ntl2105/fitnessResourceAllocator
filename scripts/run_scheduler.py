from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.io_utils import load_json, save_json
from src.models.availability import AvailabilityData
from src.models.resources import ResourceUniverse
from src.scheduler.engine import schedule_tasks
from src.scheduler.task_instances import expand_primary_activities, expansion_report

DATA_DIR = PROJECT_ROOT / "data"
RUN_DIR = DATA_DIR / "runs" / "demo-run"
EXPANSION_DIR = RUN_DIR / "02_task_expansion"
SCHEDULING_DIR = RUN_DIR / "03_scheduling"


def main() -> None:
    action_plan = load_json(DATA_DIR / "action_plan.json")
    member_profile = load_json(DATA_DIR / "member_profile.json")
    availability = AvailabilityData.model_validate(load_json(DATA_DIR / "availability.json"))
    resource_universe = ResourceUniverse.model_validate(load_json(DATA_DIR / "resource_universe.json"))

    tasks = expand_primary_activities(action_plan, availability)
    activities_by_id = {
        activity["activity_id"]: activity for activity in action_plan.get("activities", [])
    }
    result = schedule_tasks(
        tasks,
        activities_by_id,
        availability,
        run_id="demo-run",
        travel_time_rules=resource_universe.travel_time_rules,
        goal_actions=member_profile.get("goal_actions", []),
        weekly_goal_actions=member_profile.get("weekly_goal_actions", []),
        source_artifact_paths=[
            "data/action_plan.json",
            "data/member_profile.json",
            "data/availability.json",
            "data/resource_universe.json",
        ],
    )

    save_json(
        EXPANSION_DIR / "task_instances.json",
        [task.model_dump(mode="json") for task in tasks],
    )
    (EXPANSION_DIR / "expansion_report.md").parent.mkdir(parents=True, exist_ok=True)
    (EXPANSION_DIR / "expansion_report.md").write_text(
        expansion_report(tasks), encoding="utf-8"
    )
    plan_payload = result.plan.model_dump(mode="json")
    plan_payload["calendar_rows"] = [row.model_dump(mode="json") for row in result.calendar_rows]
    save_json(SCHEDULING_DIR / "personalized_plan.json", plan_payload)
    save_json(
        SCHEDULING_DIR / "decision_traces.json",
        [trace.model_dump(mode="json") for trace in result.traces],
    )
    save_json(SCHEDULING_DIR / "rejection_summary.json", result.rejection_summary)

    print(
        "Scheduler run complete: "
        f"{len(tasks)} expanded, {len(result.plan.tasks)} scheduled, "
        f"{len(tasks) - len(result.plan.tasks)} unscheduled."
    )


if __name__ == "__main__":
    main()
