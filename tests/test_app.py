from fastapi.testclient import TestClient

from src.app import KNOWN_STAGES, app


client = TestClient(app)


def test_core_pages_and_api_artifacts_are_available():
    root_response = client.get("/", follow_redirects=False)
    assert root_response.status_code == 307
    assert root_response.headers["location"] == "/calendar"

    member_response = client.get("/api/member")
    assert member_response.status_code == 200
    assert "member_id" in member_response.json()

    action_plan_response = client.get("/api/action-plan")
    assert action_plan_response.status_code == 200
    assert "activities" in action_plan_response.json()

    availability_response = client.get("/api/availability")
    assert availability_response.status_code == 200
    assert "availability_blocks" in availability_response.json()

    plan_response = client.get("/api/plan")
    assert plan_response.status_code == 200
    assert "calendar_rows" in plan_response.json()

    calendar_response = client.get("/calendar")
    assert calendar_response.status_code == 200
    assert "Elyx Weekly Calendar" in calendar_response.text
    assert "/api/calendar/interface" in calendar_response.text

    summary_response = client.get("/summary")
    assert summary_response.status_code == 200
    assert "Synthetic Data Quality" in summary_response.text
    assert "Calendar Summary" in summary_response.text

    audit_response = client.get("/audit")
    assert audit_response.status_code == 200
    assert "00_inputs" in audit_response.text
    assert "04_calendar" in audit_response.text


def test_trace_lookup_and_run_file_endpoint():
    rows = client.get("/api/runs/latest/files/04_calendar/calendar_rows.json").json()
    trace_id = rows[0]["trace_id"]

    trace_response = client.get(f"/api/traces/{trace_id}")
    assert trace_response.status_code == 200
    assert trace_response.json()["trace_id"] == trace_id

    markdown_response = client.get(
        "/api/runs/latest/files/04_calendar/summary_report.md"
    )
    assert markdown_response.status_code == 200
    assert "Calendar Summary" in markdown_response.json()["content"]


def test_trace_endpoint_resolves_rejected_candidate_conflicts_for_humans():
    response = client.get("/api/traces/trace_task_act_019_20260604_002")

    assert response.status_code == 200
    payload = response.json()
    assert payload["activity_title"] == "Zone 2 stationary bike session"
    assert payload["selected_slot_summary"] == (
        "Scheduled for Fri Jun 5, 06:30-07:10 at gym because all selected-slot "
        "policy and resource checks passed."
    )
    first_candidate = payload["rejected_candidate_summaries"][0]
    assert first_candidate["slot_summary"] == "Thu Jun 4, 06:30-07:10 at gym"
    assert first_candidate["human_reasons"] == [
        "Rejected because it overlaps Baseline fasting metabolic lab panel, "
        "07:00-07:45 at lab."
    ]


def test_run_file_endpoint_rejects_unknown_stages_and_path_traversal():
    assert "04_calendar" in KNOWN_STAGES

    unknown_stage_response = client.get(
        "/api/runs/latest/files/unknown/calendar_rows.json"
    )
    assert unknown_stage_response.status_code == 404

    traversal_response = client.get(
        "/api/runs/latest/files/04_calendar/..%2F..%2Fmember_profile.json"
    )
    assert traversal_response.status_code == 404


def test_calendar_interface_api_returns_weeks_and_scenarios():
    response = client.get("/api/calendar/interface")

    assert response.status_code == 200
    payload = response.json()
    assert payload["weeks"]
    assert "remote" in payload["scenario_counts"]
    assert "substitution" in payload["scenario_counts"]
    assert payload["display_hours"] == {"start": 6, "end": 22}
    first_week = payload["weeks"][0]
    assert len(first_week["days"]) == 7
    assert "activities" in first_week
    assert "unavailable_blocks" in first_week


def test_calendar_page_bootstraps_weekly_interface_assets():
    response = client.get("/calendar")

    assert response.status_code == 200
    assert 'id="calendar-root"' in response.text
    assert 'data-display-mode="agenda"' in response.text
    assert "/static/calendar.css" in response.text
    assert "/static/calendar.js" in response.text
    assert "/api/calendar/interface" in response.text


def test_calendar_renderer_uses_day_agenda_without_absolute_time_grid():
    js_response = client.get("/static/calendar.js")
    css_response = client.get("/static/calendar.css")

    assert js_response.status_code == 200
    assert css_response.status_code == 200
    assert "renderAgendaDay" in js_response.text
    assert "time-column" not in js_response.text
    assert "hour-line" not in js_response.text
    assert "position: absolute" not in css_response.text


def test_trace_drawer_renders_human_decision_explanations():
    js_response = client.get("/static/calendar.js")

    assert js_response.status_code == 200
    assert "Scheduled Slot" in js_response.text
    assert "Earlier Rejected Attempts" in js_response.text
    assert "rejected_candidate_summaries" in js_response.text
    assert "JSON.stringify((trace.rejected_candidates" not in js_response.text


def test_calendar_renderer_has_review_debugging_sections():
    js_response = client.get("/static/calendar.js")
    css_response = client.get("/static/calendar.css")

    assert js_response.status_code == 200
    assert css_response.status_code == 200
    assert "renderGoalCoverage" in js_response.text
    assert "renderUnscheduledItems" in js_response.text
    assert "renderLocationBands" in js_response.text
    assert "weekScenarioCounts" in js_response.text
    assert "provider_summary" in js_response.text
    assert ".goal-panel" in css_response.text
    assert ".location-band" in css_response.text
