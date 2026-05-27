from pathlib import Path

from src.generation.profile_brief import build_member_profile_brief, write_member_profile_brief
from src.io_utils import load_json


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_member_profile_brief_maps_profile_json_to_reviewer_markdown(tmp_path):
    profile = load_json(PROJECT_ROOT / "data" / "member_profile.json")

    brief = build_member_profile_brief(profile)

    assert brief.startswith(f"# Member Profile Brief: {profile['name']}")
    assert profile["occupation"] in brief
    assert "## Goals" in brief
    assert "Improve metabolic health" in brief
    assert "## Preferences" in brief
    assert "06:30-08:00" in brief
    assert "## Constraints" in brief
    assert "knee" in brief.lower()
    assert "## Baseline Snapshot" in brief
    assert "recent sleep score" in brief.lower()
    assert "## Journey Timeline" in brief
    assert profile["journey_phases"][0]["phase_id"] in brief
    assert "## Travel Windows" in brief
    assert profile["travel_windows"][0]["travel_window_id"] in brief
    assert "## Scheduling Implications" in brief
    assert "Prefer morning exercise" in brief
    assert brief.endswith("\n")

    output_path = tmp_path / "member_profile_brief.md"
    written = write_member_profile_brief(
        PROJECT_ROOT / "data" / "member_profile.json",
        output_path,
    )

    assert written == brief
    assert output_path.read_text(encoding="utf-8") == brief
