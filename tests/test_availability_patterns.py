from src.generation.availability_patterns import expand_availability_patterns


def test_expand_availability_patterns_creates_concrete_weekly_blocks():
    payload = {
        "planning_start_date": "2026-06-01",
        "planning_months": 3,
        "patterns": [
            {
                "pattern_id": "member_work",
                "type": "weekly",
                "resource_id": "member_001",
                "resource_type": "member_blocked",
                "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                "start_time": "08:30",
                "end_time": "18:30",
                "timezone": "Asia/Singapore",
                "location_id": "office",
                "remote_supported": True,
                "travel_compatible": False,
                "skip_date_ranges": [{"start": "2026-06-19", "end": "2026-06-25"}],
                "notes": "Work block.",
            },
            {
                "pattern_id": "travel",
                "type": "date_range",
                "resource_id": "travel_hk_2026_06",
                "resource_type": "member_travel",
                "start": "2026-06-19T10:00:00+08:00",
                "end": "2026-06-25T20:00:00+08:00",
                "timezone": "Asia/Singapore",
                "location_id": "travel_hotel",
                "remote_supported": True,
                "travel_compatible": True,
                "notes": "Travel window.",
            },
        ],
    }

    expanded = expand_availability_patterns(payload)

    blocks = expanded["availability_blocks"]
    work_blocks = [block for block in blocks if block["resource_id"] == "member_001"]
    assert len(work_blocks) >= 50
    assert not any("2026-06-19T08:30" in block["start"] for block in work_blocks)
    assert blocks[-1]["start"] < "2026-09-01"
    assert any(block["resource_type"] == "member_travel" for block in blocks)
