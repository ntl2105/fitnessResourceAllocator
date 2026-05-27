from pathlib import Path

from fastapi.testclient import TestClient

from src.app import app
from src.generation.pipeline_story import build_pipeline_story


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_pipeline_story_explains_marcus_generation_stages():
    story = build_pipeline_story(PROJECT_ROOT / "data")

    assert story["member_name"] == "Marcus Tan"
    stage_ids = [stage["stage_id"] for stage in story["stages"]]
    assert stage_ids == [
        "01_member_profile",
        "02_resource_universe",
        "03_known_frictions",
        "04_availability",
        "05_activity_families",
        "06_validation",
        "07_scheduling_and_calendar",
    ]

    profile_stage = story["stages"][0]
    assert "Member: Marcus Tan (member_elyx_marcus_001)" in profile_stage["generated"]
    assert any("goal action" in item for item in profile_stage["generated"])
    assert any("source of truth" in item for item in profile_stage["meaning_for_member"])

    activity_stage = story["stages"][4]
    assert activity_stage["status"] in {"in_progress", "ready"}
    assert any("scheduler-facing activity draft" in item for item in activity_stage["generated"])
    assert any(
        "goal contributions" in item
        for item in activity_stage["meaning_for_member"]
        + activity_stage["validation_focus"]
    )
    assert activity_stage["source_files"] == ["data/generated/stage05_activity_families/batches"]

    validation_stage = story["stages"][5]
    assert any("Deterministic validation" in item for item in validation_stage["generated"])


def test_pipeline_story_points_to_empty_stage5_generation_folder_after_legacy_archive():
    story = build_pipeline_story(PROJECT_ROOT / "data")
    activity_stage = next(
        stage for stage in story["stages"] if stage["stage_id"] == "05_activity_families"
    )

    assert activity_stage["source_files"] == ["data/generated/stage05_activity_families/batches"]


def test_pipeline_page_and_api_render_marcus_story_without_final_calendar_run():
    client = TestClient(app)

    page_response = client.get("/pipeline")
    assert page_response.status_code == 200
    assert "Elyx Pipeline Story" in page_response.text
    assert "/static/pipeline.css" in page_response.text
    assert "Marcus Tan" in page_response.text
    assert "Meaning For Marcus Tan" in page_response.text
    assert "Activity Families" in page_response.text
    assert "Validation Focus" in page_response.text
    assert 'class="stage-rail"' in page_response.text
    assert 'class="fact-strip"' in page_response.text
    assert 'class="insight-panel"' in page_response.text
    assert 'class="source-chips"' in page_response.text

    api_response = client.get("/api/pipeline/story")
    assert api_response.status_code == 200
    payload = api_response.json()
    assert payload["member_name"] == "Marcus Tan"
    assert len(payload["stages"]) == 7

    css_response = client.get("/static/pipeline.css")
    assert css_response.status_code == 200
    assert ".stage-rail" in css_response.text
    assert ".fact-pill" in css_response.text
    assert ".insight-panel" in css_response.text
    assert ".source-chips" in css_response.text
