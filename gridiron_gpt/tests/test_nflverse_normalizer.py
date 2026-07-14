from gridiron_gpt.data_ingest.nflverse_normalizer import (
    normalize_roster_record,
    normalize_snapshot,
    normalize_weekly_stat_record,
)


def test_normalize_roster_record():
    result = normalize_roster_record(
        {
            "gsis_id": "00-0033873",
            "full_name": "Patrick Mahomes",
            "team": "KC",
            "position": "QB",
            "season": 2025,
            "status": "ACT",
        }
    )

    assert result["event_type"] == "roster_snapshot"
    assert result["player_id"] == "00-0033873"
    assert result["player_name"] == "Patrick Mahomes"
    assert result["team"] == "KC"


def test_normalize_weekly_stat_record():
    result = normalize_weekly_stat_record(
        {
            "player_id": "00-0033873",
            "player_display_name": "Patrick Mahomes",
            "recent_team": "KC",
            "position_group": "QB",
            "season": 2025,
            "week": 1,
            "passing_yards": 310,
        }
    )

    assert result["event_type"] == "weekly_player_stats"
    assert result["player_name"] == "Patrick Mahomes"
    assert result["statistics"]["passing_yards"] == 310


def test_normalize_snapshot():
    result = normalize_snapshot(
        {
            "season": 2025,
            "rosters": [{"player_name": "Player A"}],
            "weekly_player_stats": [
                {"player_name": "Player A", "week": 1}
            ],
        }
    )

    assert result["counts"]["rosters"] == 1
    assert result["counts"]["weekly_player_stats"] == 1
