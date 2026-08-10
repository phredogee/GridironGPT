import pandas as pd

from gridiron_gpt.ingestion.services.ingestion_service import IngestionService
from gridiron_gpt.ingestion.sources.nflverse_player_stats import (
    NFLVersePlayerStatsAdapter,
)


def make_stats_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "player_id": "00-0039849",
                "player_name": "B.Robinson",
                "player_display_name": "Bijan Robinson",
                "position": "RB",
                "position_group": "RB",
                "season": 2026,
                "week": 1,
                "season_type": "REG",
                "game_id": "2026_01_ATL_TB",
                "team": "ATL",
                "opponent_team": "TB",
                "carries": 18,
                "rushing_yards": 92,
                "targets": 6,
                "receptions": 5,
                "receiving_yards": 41,
            },
            {
                "player_id": "00-0033873",
                "player_name": "T.Hendrickson",
                "player_display_name": "Trey Hendrickson",
                "position": "DE",
                "position_group": "DL",
                "season": 2026,
                "week": 1,
                "season_type": "REG",
                "game_id": "2026_01_CIN_CLE",
                "team": "CIN",
                "opponent_team": "CLE",
                "sacks": 2.0,
            },
        ]
    )


def test_adapter_emits_source_neutral_stat_records():
    adapter = NFLVersePlayerStatsAdapter(
        2026,
        loader=lambda seasons, summary_level: make_stats_frame(),
    )

    records = adapter.fetch()

    assert len(records) == 2

    bijan = records[0]
    assert bijan.source == "nflverse player stats"
    assert bijan.player == "Bijan Robinson"
    assert bijan.team == "ATL"
    assert bijan.position == "RB"
    assert bijan.source_id == "player_stats:2026_01_ATL_TB:00-0039849"
    assert bijan.metadata["provider"] == "nflverse"
    assert bijan.metadata["dataset"] == "player_stats"
    assert bijan.metadata["stats"]["carries"] == 18
    assert bijan.metadata["stats"]["rushing_yards"] == 92


def test_adapter_can_filter_positions_without_changing_loader():
    adapter = NFLVersePlayerStatsAdapter(
        2026,
        positions={"QB", "RB", "WR", "TE"},
        loader=lambda seasons, summary_level: make_stats_frame(),
    )

    records = adapter.fetch()

    assert [record.player for record in records] == ["Bijan Robinson"]


def test_stat_records_normalize_into_raw_events_without_interpretation():
    adapter = NFLVersePlayerStatsAdapter(
        2026,
        positions={"RB"},
        loader=lambda seasons, summary_level: make_stats_frame(),
    )

    events = IngestionService().ingest(adapter)

    assert len(events) == 1

    event = events[0]
    assert event.player == "Bijan Robinson"
    assert event.team == "ATL"
    assert event.position == "RB"
    assert event.sentiment is None
    assert event.impact_score is None
    assert event.confidence is None
    assert event.evidence["source_id"] == (
        "player_stats:2026_01_ATL_TB:00-0039849"
    )
    assert event.evidence["source_metadata"]["stats"]["targets"] == 6


def test_same_player_week_has_stable_provider_identity():
    adapter = NFLVersePlayerStatsAdapter(
        2026,
        positions={"RB"},
        loader=lambda seasons, summary_level: make_stats_frame(),
    )

    first = IngestionService().ingest(adapter)[0]
    second = IngestionService().ingest(adapter)[0]

    assert first.fingerprint() == second.fingerprint()


def test_adapter_skips_rows_without_stable_player_identity():
    frame = make_stats_frame()
    frame.loc[0, "player_id"] = None

    adapter = NFLVersePlayerStatsAdapter(
        2026,
        loader=lambda seasons, summary_level: frame,
    )

    records = adapter.fetch()

    assert [record.player for record in records] == ["Trey Hendrickson"]
