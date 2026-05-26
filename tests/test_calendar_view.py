from src.io_utils import load_json
from src.calendar_view import build_summary, write_calendar_artifacts


def test_write_calendar_artifacts_validates_rows_and_summarizes(tmp_path):
    plan_path = tmp_path / "personalized_plan.json"
    output_dir = tmp_path / "04_calendar"
    plan_path.write_text(
        """
{
  "run_id": "demo-run",
  "metadata": {"scheduled_count": 3, "unscheduled_count": 1},
  "tasks": [],
  "calendar_rows": [
    {
      "calendar_row_id": "row_001",
      "date": "2026-06-04",
      "start_time": "07:00",
      "end_time": "07:45",
      "title": "Baseline lab panel",
      "activity_type": "consultation",
      "goal_tags": ["metabolic_health"],
      "load_level": "low",
      "location_id": "lab",
      "mode": "in_person",
      "substitution_status": "primary",
      "trace_id": "trace_001",
      "compact_group_key": "2026-06-04:consultation"
    },
    {
      "calendar_row_id": "row_002",
      "date": "2026-06-05",
      "start_time": "08:00",
      "end_time": "08:30",
      "title": "Remote coaching",
      "activity_type": "therapy",
      "goal_tags": ["travel_continuity"],
      "load_level": "low",
      "location_id": "remote",
      "mode": "remote",
      "substitution_status": "substitution",
      "trace_id": "trace_002",
      "compact_group_key": "2026-06-05:therapy"
    },
    {
      "calendar_row_id": "row_003",
      "date": "2026-06-06",
      "start_time": "09:00",
      "end_time": "09:20",
      "title": "Hotel mobility session",
      "activity_type": "fitness",
      "goal_tags": ["travel_continuity"],
      "load_level": "medium",
      "location_id": "travel_hotel",
      "mode": "in_person",
      "substitution_status": "primary",
      "trace_id": "trace_003",
      "compact_group_key": "2026-06-06:fitness"
    }
  ]
}
""",
        encoding="utf-8",
    )

    rows = write_calendar_artifacts(plan_path, output_dir)

    assert len(rows) == 3
    assert load_json(output_dir / "calendar_rows.json")[0]["calendar_row_id"] == "row_001"
    summary = (output_dir / "summary_report.md").read_text(encoding="utf-8")
    assert "Total rows: 3" in summary
    assert "Substitutions: 1" in summary
    assert "Remote rows: 1" in summary
    assert "Travel hotel rows: 1" in summary
    assert "Date range: 2026-06-04 to 2026-06-06" in summary
    assert "- consultation: 1" in summary
    assert "- fitness: 1" in summary
    assert "- therapy: 1" in summary


def test_build_summary_handles_empty_calendar():
    summary = build_summary([], {})

    assert "Total rows: 0" in summary
    assert "Date range: n/a" in summary
