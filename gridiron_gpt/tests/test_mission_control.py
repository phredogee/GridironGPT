from apps.streamlit.pages.mission_control import build_mission_control_status


def test_mission_control_status_preserves_operational_counts():
    status = build_mission_control_status(
        event_count=12,
        relationship_count=44,
        player_count=562,
        scored_player_count=36,
        passing_tests=655,
    )

    assert status.event_count == 12
    assert status.relationship_count == 44
    assert status.player_count == 562
    assert status.scored_player_count == 36
    assert status.passing_tests == 655


def test_mission_control_status_clamps_negative_counts():
    status = build_mission_control_status(
        event_count=-1,
        relationship_count=-2,
        player_count=-3,
        scored_player_count=-4,
        passing_tests=-5,
    )

    assert status.event_count == 0
    assert status.relationship_count == 0
    assert status.player_count == 0
    assert status.scored_player_count == 0
    assert status.passing_tests == 0


def test_mission_control_status_is_immutable():
    status = build_mission_control_status(
        event_count=1,
        relationship_count=2,
        player_count=3,
        scored_player_count=4,
        passing_tests=5,
    )

    try:
        status.event_count = 99
    except Exception as error:
        assert error.__class__.__name__ == "FrozenInstanceError"
    else:
        raise AssertionError("MissionControlStatus should be immutable")
