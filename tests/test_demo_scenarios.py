import re
from datetime import datetime
from pathlib import Path

from src.io_utils import load_json


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEMO_RUN_DIR = PROJECT_ROOT / "data" / "runs" / "demo-run"


def _demo_json(relative_path: str):
    return load_json(DEMO_RUN_DIR / relative_path)


def _reason_text(trace: dict) -> str:
    rejected_reasons = [
        reason
        for candidate in trace.get("rejected_candidates", [])
        for reason in candidate.get("reasons", [])
    ]
    check_reasons = [check.get("reason", "") for check in trace.get("constraint_checks", [])]
    return " ".join(rejected_reasons + check_reasons).lower()


def test_calendar_contains_remote_and_travel_adapted_rows_in_travel_windows():
    calendar_rows = _demo_json("04_calendar/calendar_rows.json")
    availability = _demo_json("00_inputs/availability.json")

    remote_rows = [row for row in calendar_rows if row.get("mode") == "remote"]
    travel_hotel_rows = [
        row for row in calendar_rows if row.get("location_id") == "travel_hotel"
    ]
    assert remote_rows
    assert travel_hotel_rows

    travel_windows = [
        (
            datetime.fromisoformat(block["start"]).date(),
            datetime.fromisoformat(block["end"]).date(),
        )
        for block in availability["availability_blocks"]
        if block.get("resource_type") == "member_travel"
    ]
    assert travel_windows
    assert any(
        row.get("location_id") == "travel_hotel"
        and any(start <= datetime.fromisoformat(row["date"]).date() <= end for start, end in travel_windows)
        for row in calendar_rows
    )


def test_decision_traces_explain_rejections_and_include_handoff_summaries():
    traces = _demo_json("03_scheduling/decision_traces.json")

    traces_with_rejections = [
        trace for trace in traces if trace.get("rejected_candidates")
    ]
    assert traces_with_rejections
    assert any(
        any(check.get("passed") is False and check.get("reason") for check in trace["constraint_checks"])
        for trace in traces_with_rejections
    )
    assert all(
        candidate.get("reasons")
        for trace in traces_with_rejections
        for candidate in trace["rejected_candidates"]
    )

    handoff_traces = [
        trace for trace in traces if trace.get("provider_handoff_summary")
    ]
    assert handoff_traces
    assert any(trace.get("final_status") == "scheduled" for trace in handoff_traces)
    assert any(trace.get("final_status") == "unscheduled" for trace in handoff_traces)
    assert all("Share care context" in trace["provider_handoff_summary"] for trace in handoff_traces)


def test_synthetic_quality_report_contains_expected_sections_and_counts():
    report_path = DEMO_RUN_DIR / "00_inputs" / "synthetic_data_quality_report.md"
    report = report_path.read_text(encoding="utf-8")
    action_plan = _demo_json("00_inputs/action_plan.json")

    activity_count = len(action_plan["activities"])
    primary_count = sum(1 for activity in action_plan["activities"] if activity["is_primary"])

    assert report.startswith("# Synthetic Data Quality Report")
    assert "Status: pass" in report
    assert "## Validation Checks" in report
    assert f"Activities: {activity_count}" in report
    assert f"Primary activities: {primary_count}" in report
    assert "Modalities: consultation, fitness, food, medication, therapy" in report
    assert len(re.findall(r"^- PASS:", report, flags=re.MULTILINE)) >= 10


def test_traces_capture_member_travel_and_travel_time_buffer_rejections():
    traces = _demo_json("03_scheduling/decision_traces.json")

    assert any(
        any(
            candidate.get("location_id") != "travel_hotel"
            and "member travel" in " ".join(candidate.get("reasons", [])).lower()
            for candidate in trace.get("rejected_candidates", [])
        )
        for trace in traces
    )
    assert any(
        check.get("name") == "travel_time_buffer"
        and check.get("passed") is False
        and "requires" in check.get("reason", "")
        and "minutes" in check.get("reason", "")
        for trace in traces
        for check in trace.get("constraint_checks", [])
    )


def test_calendar_contains_scheduled_substitutions():
    calendar_rows = _demo_json("04_calendar/calendar_rows.json")

    assert any(row.get("substitution_status") == "substitution" for row in calendar_rows)


def test_rejection_summary_aggregates_unscheduled_and_rejected_candidate_counts():
    traces = _demo_json("03_scheduling/decision_traces.json")
    rejection_summary = _demo_json("03_scheduling/rejection_summary.json")

    expected = {}
    for trace in traces:
        if trace.get("final_status") != "unscheduled":
            continue
        activity_summary = expected.setdefault(
            trace["activity_id"],
            {"unscheduled_count": 0, "rejected_candidate_count": 0},
        )
        activity_summary["unscheduled_count"] += 1
        activity_summary["rejected_candidate_count"] += len(trace.get("rejected_candidates", []))

    assert expected
    assert rejection_summary == expected
