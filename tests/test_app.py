from fastapi.testclient import TestClient

from src import app as app_module
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
    assert "<nav>" not in calendar_response.text
    assert 'class="calendar-tab active" data-tab-target="profile-panel"' in calendar_response.text
    assert calendar_response.text.index('data-tab-target="profile-panel"') < calendar_response.text.index('data-tab-target="activity-board-panel"')
    assert calendar_response.text.index('data-tab-target="activity-board-panel"') < calendar_response.text.index('data-tab-target="calendar-panel"')
    assert calendar_response.text.index('data-tab-target="calendar-panel"') < calendar_response.text.index('data-tab-target="recap-panel"')
    assert 'data-tab-target="calendar-panel"' in calendar_response.text
    assert 'data-tab-target="recap-panel"' in calendar_response.text
    assert 'data-tab-target="profile-panel"' in calendar_response.text
    assert "recap-root" in calendar_response.text
    assert "member-profile-root" in calendar_response.text
    assert "Profile content loads from the calendar interface model" in calendar_response.text

    profile_response = client.get("/profile")
    assert profile_response.status_code == 200
    assert "Member Profile Brief" in profile_response.text
    assert "Journey Timeline" in profile_response.text

    summary_response = client.get("/summary")
    assert summary_response.status_code == 200
    assert "Synthetic Data Quality" in summary_response.text
    assert "Calendar Summary" in summary_response.text
    assert "/profile" in summary_response.text

    audit_response = client.get("/audit")
    assert audit_response.status_code == 200
    assert "00_inputs" in audit_response.text
    assert "04_calendar" in audit_response.text
    assert "member_profile_brief.md" in audit_response.text


def test_trace_lookup_and_run_file_endpoint():
    rows = client.get("/api/runs/latest/files/04_calendar/calendar_rows.json").json()
    trace_id = rows[0]["trace_id"]
    constraint_audit = client.get(
        "/api/runs/latest/files/04_calendar/constraint_violations.json"
    ).json()
    assert constraint_audit["status"] == "pass"
    assert constraint_audit["violation_count"] == 0

    trace_response = client.get(f"/api/traces/{trace_id}")
    assert trace_response.status_code == 200
    assert trace_response.json()["trace_id"] == trace_id
    assert trace_response.json()["planning_rationale"]

    markdown_response = client.get(
        "/api/runs/latest/files/04_calendar/summary_report.md"
    )
    assert markdown_response.status_code == 200
    assert "Calendar Summary" in markdown_response.json()["content"]

    profile_brief_response = client.get(
        "/api/runs/latest/files/00_inputs/member_profile_brief.md"
    )
    assert profile_brief_response.status_code == 200
    assert "Member Profile Brief" in profile_brief_response.json()["content"]


def test_trace_endpoint_resolves_rejected_candidate_conflicts_for_humans():
    traces = client.get(
        "/api/runs/latest/files/03_scheduling/decision_traces.json"
    ).json()
    trace_id = next(
        trace["trace_id"]
        for trace in traces
        if any(
            any(reason.startswith("Overlaps ") for reason in candidate.get("reasons", []))
            for candidate in trace.get("rejected_candidates", [])
        )
    )

    response = client.get(f"/api/traces/{trace_id}")

    assert response.status_code == 200
    payload = response.json()
    overlap_candidate = next(
        candidate
        for candidate in payload["rejected_candidate_summaries"]
        if any(reason.startswith("Rejected because it overlaps") for reason in candidate["human_reasons"])
    )
    assert payload["activity_title"]
    assert payload["selected_slot_summary"]
    assert payload["planning_rationale"]
    assert "task_" not in " ".join(overlap_candidate["human_reasons"])


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
    assert 'id="recap-panel"' in response.text
    assert 'id="profile-panel"' in response.text
    assert 'id="calendar-panel"' in response.text
    assert 'class="calendar-tab active" data-tab-target="profile-panel"' in response.text
    assert response.text.index('data-tab-target="profile-panel"') < response.text.index('data-tab-target="activity-board-panel"')
    assert response.text.index('data-tab-target="activity-board-panel"') < response.text.index('data-tab-target="calendar-panel"')
    assert response.text.index('data-tab-target="calendar-panel"') < response.text.index('data-tab-target="recap-panel"')
    assert "<nav>" not in response.text


def test_calendar_renderer_uses_day_agenda_without_absolute_time_grid():
    js_response = client.get("/static/calendar.js")
    css_response = client.get("/static/calendar.css")

    assert js_response.status_code == 200
    assert css_response.status_code == 200
    assert "renderAgendaDay" in js_response.text
    assert "time-column" not in js_response.text
    assert "hour-line" not in js_response.text
    assert "position: absolute" not in css_response.text


def test_calendar_renderer_supports_profile_tab_on_same_page():
    js_response = client.get("/static/calendar.js")
    css_response = client.get("/static/calendar.css")

    assert js_response.status_code == 200
    assert css_response.status_code == 200
    assert "setupCalendarTabs" in js_response.text
    assert "calendar-tab active" in js_response.text
    assert "renderThreeMonthRecap" in js_response.text
    assert "three_month_recap" in js_response.text
    assert "Final Scheduler Tally" in js_response.text
    assert "Weekly Targets Met" in js_response.text
    assert "Not Fully Met" in js_response.text
    assert "Constraint Violations" in js_response.text
    assert "Final Calendar Audit" in js_response.text
    assert "counted target" in js_response.text
    assert "extra instances do not cover missed periods" in js_response.text
    assert "displayStatus" in js_response.text
    assert "renderValidationRecap" in js_response.text
    assert "renderRecapExplainer" in js_response.text
    assert "Recap Field Guide" in js_response.text
    assert "loadCalendarInterface" in js_response.text
    assert 'cache: "no-store"' in js_response.text
    assert "setInterval(() => loadCalendarInterface({silent: true}), 10000)" in js_response.text
    assert ".recap-explainer" in css_response.text
    assert "renderMemberProfile" in js_response.text
    assert "renderProviderUniverse" in js_response.text
    assert "member_profile" in js_response.text
    assert "Operating Context" in js_response.text
    assert "Resources and Timeline" in js_response.text
    assert "profile-goal-grid" in js_response.text
    assert ".calendar-tabs" in css_response.text
    assert ".recap-grid" in css_response.text
    assert ".member-profile-grid" in css_response.text
    assert ".profile-band" in css_response.text
    assert ".profile-context-grid" in css_response.text
    assert ".profile-resource-grid" in css_response.text
    assert ".profile-provider-grid" in css_response.text
    assert ".profile-timeline" in css_response.text
    assert ".tab-panel[hidden]" in css_response.text


def test_trace_drawer_renders_human_decision_explanations():
    js_response = client.get("/static/calendar.js")

    assert js_response.status_code == 200
    assert "Scheduled Slot" in js_response.text
    assert "Why This Activity Exists" in js_response.text
    assert "planning_rationale" in js_response.text
    assert "Earlier Rejected Attempts" in js_response.text
    assert "rejected_candidate_summaries" in js_response.text
    assert "JSON.stringify((trace.rejected_candidates" not in js_response.text


def test_trace_explanation_inherits_primary_goal_and_describes_self_led_substitution():
    primary = {
        "activity_id": "act_strength_primary",
        "activity_family_id": "strength_family",
        "is_primary": True,
        "title": "Home strength",
        "goal_contributions": [
            {
                "weekly_goal_action_id": "ga_strength_sessions_weekly",
                "counts_toward_weekly_target": True,
            }
        ],
    }
    substitution = {
        "activity_id": "act_strength_travel",
        "activity_family_id": "strength_family",
        "is_primary": False,
        "title": "Travel strength",
        "facilitator_type": "member",
        "substitution_for_activity_id": "act_strength_primary",
        "substitution_reason_codes": ["equipment_unavailable"],
        "frequency": {"preferred_time_windows": ["19:50-20:30"]},
    }
    trace = {
        "final_status": "scheduled",
        "activity_id": "act_strength_travel",
        "task_instance_id": "task_strength",
        "selected_slot": {
            "start": "2026-06-24T19:50:00+08:00",
            "end": "2026-06-24T20:25:00+08:00",
            "location_id": "travel_hotel",
        },
    }
    activities = {
        "act_strength_primary": primary,
        "act_strength_travel": substitution,
    }
    weekly_actions = {
        "ga_strength_sessions_weekly": {
            "label": "Strength sessions",
            "target_per_week": 2,
        }
    }

    goal = app_module._goal_explanation(trace, substitution, {}, {}, activities, weekly_actions)
    reason = app_module._selected_slot_reason(trace, substitution, {}, goal)
    rationale = app_module._planning_rationale(substitution, goal, activities)

    assert goal["label"] == "Strength sessions"
    assert any(item.startswith("Goal mapping: contributes to Strength sessions.") for item in rationale)
    assert "member-led; no provider required" in reason
    assert "travel hotel was an allowed location" in reason


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


def test_calendar_renderer_uses_week_scoped_review_panels():
    js_response = client.get("/static/calendar.js")

    assert js_response.status_code == 200
    assert "renderGoalCoverage(week)" in js_response.text
    assert "renderUnscheduledItems(week)" in js_response.text
    assert "state.model.goal_coverage?.week" not in js_response.text
    assert "state.model.unscheduled_items || []" not in js_response.text


def test_calendar_review_panels_render_around_agenda_with_clear_goal_math():
    js_response = client.get("/static/calendar.js")

    assert js_response.status_code == 200
    js = js_response.text
    assert js.index("${renderCategoryTime(week)}") < js.index('<div class="agenda-grid">')
    assert js.index('<div class="agenda-grid">') < js.index("${renderGoalCoverage(week)}")
    assert "Target coverage: ${goal.scheduled} of ${target}" in js
    assert "substitutions: ${goal.substitutions}" in js
    assert "Support-only actions are tracked separately" in js


def test_calendar_renderer_exposes_data_quality_warnings():
    js_response = client.get("/static/calendar.js")
    css_response = client.get("/static/calendar.css")

    assert "renderDataQualityWarnings" in js_response.text
    assert "data_quality_warnings" in js_response.text
    assert ".warning-panel" in css_response.text
