from unittest.mock import Mock, patch

from gridiron_gpt.data_ingest.nflreadpy_adapter import (
    fetch_nflverse_snapshot,
    load_players,
    load_rosters,
    load_weekly_player_stats,
)


def make_frame(records):
    frame = Mock()
    frame.to_dicts.return_value = records
    return frame


@patch(
    "gridiron_gpt.data_ingest.nflreadpy_adapter.nfl.load_players"
)
def test_load_players(mock_load_players):
    mock_load_players.return_value = make_frame(
        [
            {
                "gsis_id": "00-0033873",
                "display_name": "Patrick Mahomes",
                "position": "QB",
            }
        ]
    )

    records = load_players()

    assert len(records) == 1
    assert records[0]["display_name"] == "Patrick Mahomes"


@patch(
    "gridiron_gpt.data_ingest.nflreadpy_adapter.nfl.load_rosters"
)
def test_load_rosters(mock_load_rosters):
    mock_load_rosters.return_value = make_frame(
        [
            {
                "player_name": "Patrick Mahomes",
                "team": "KC",
                "position": "QB",
            }
        ]
    )

    records = load_rosters(2025)

    mock_load_rosters.assert_called_once_with([2025])
    assert records[0]["team"] == "KC"


@patch(
    "gridiron_gpt.data_ingest.nflreadpy_adapter."
    "nfl.load_player_stats"
)
def test_load_weekly_player_stats(mock_load_stats):
    mock_load_stats.return_value = make_frame(
        [
            {
                "player_name": "Patrick Mahomes",
                "season": 2025,
                "week": 1,
            }
        ]
    )

    records = load_weekly_player_stats(2025)

    mock_load_stats.assert_called_once_with([2025])
    assert records[0]["week"] == 1


@patch(
    "gridiron_gpt.data_ingest.nflreadpy_adapter."
    "load_weekly_player_stats"
)
@patch(
    "gridiron_gpt.data_ingest.nflreadpy_adapter.load_rosters"
)
@patch(
    "gridiron_gpt.data_ingest.nflreadpy_adapter.load_players"
)
def test_fetch_nflverse_snapshot(
    mock_players,
    mock_rosters,
    mock_stats,
):
    mock_players.return_value = [{"name": "Player A"}]
    mock_rosters.return_value = [{"name": "Player A"}]
    mock_stats.return_value = [
        {"name": "Player A", "week": 1},
        {"name": "Player A", "week": 2},
    ]

    result = fetch_nflverse_snapshot(2025)

    assert result["source"] == "nflverse"
    assert result["season"] == 2025
    assert result["counts"] == {
        "players": 1,
        "rosters": 1,
        "weekly_player_stats": 2,
    }
