import pandas as pd

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.understand.signal_processor import SignalProcessor
from gridiron_gpt.ingestion.sources.nflverse_player_stats import (
    NFLVersePlayerStatsAdapter,
)


def loader(_seasons, _summary_level):
    return pd.DataFrame(
        [
            {
                "player_id": "00-001",
                "player_display_name": "Bijan Robinson",
                "position": "RB",
                "team": "ATL",
                "season": 2026,
                "week": 1,
                "season_type": "REG",
                "carries": 12,
                "targets": 3,
                "receptions": 2,
                "rushing_yards": 55,
                "receiving_yards": 14,
            },
            {
                "player_id": "00-001",
                "player_display_name": "Bijan Robinson",
                "position": "RB",
                "team": "ATL",
                "season": 2026,
                "week": 2,
                "season_type": "REG",
                "carries": 14,
                "targets": 4,
                "receptions": 3,
                "rushing_yards": 61,
                "receiving_yards": 21,
            },
            {
                "player_id": "00-001",
                "player_display_name": "Bijan Robinson",
                "position": "RB",
                "team": "ATL",
                "season": 2026,
                "week": 3,
                "season_type": "REG",
                "carries": 21,
                "targets": 7,
                "receptions": 6,
                "rushing_yards": 105,
                "receiving_yards": 48,
                "rushing_tds": 1,
            },
        ]
    )


def test_adapter_attaches_prior_week_baseline_and_deltas():
    records = NFLVersePlayerStatsAdapter(
        2026,
        loader=loader,
    ).fetch()

    week_three = records[2].metadata["stat_context"]

    assert week_three["prior_games"] == 2
    assert week_three["baseline"]["touches"] == 15.5
    assert week_three["current"]["touches"] == 27.0
    assert week_three["deltas"]["touches"] == 11.5
    assert week_three["baseline"]["targets"] == 3.5
    assert week_three["deltas"]["targets"] == 3.5


def test_first_week_has_no_prior_baseline():
    records = NFLVersePlayerStatsAdapter(
        2026,
        loader=loader,
    ).fetch()

    context = records[0].metadata["stat_context"]

    assert context["prior_games"] == 0
    assert context["baseline"] == {}
    assert context["deltas"] == {}


def _event_from_record(record):
    return RawEvent(
        headline=record.headline,
        source=record.source,
        player=record.player,
        team=record.team,
        position=record.position,
        evidence={
            "source_id": record.source_id,
            "source_metadata": record.metadata,
        },
    )


def test_usage_growth_increases_contextual_impact():
    records = NFLVersePlayerStatsAdapter(
        2026,
        loader=loader,
    ).fetch()

    contextual_signal = SignalProcessor().process(
        _event_from_record(records[2]),
        entities=[],
    )

    no_context_event = _event_from_record(records[2])
    no_context_event.evidence["source_metadata"] = dict(
        no_context_event.evidence["source_metadata"]
    )
    no_context_event.evidence["source_metadata"]["stat_context"] = None

    no_context_signal = SignalProcessor().process(
        no_context_event,
        entities=[],
    )

    assert contextual_signal.impact_score > no_context_signal.impact_score
    context = contextual_signal.evidence["statistical_interpretation"]["context"]
    assert context["trend_adjustment"] > 0
    assert any(
        "Touches" in reason
        for reason in contextual_signal.evidence["statistical_interpretation"]["reasons"]
    )


def test_declining_usage_can_reduce_contextual_impact():
    event = RawEvent(
        headline="Example RB 2026 Week 4 statistical line",
        source="nflverse player stats",
        player="Example RB",
        team="ATL",
        position="RB",
        evidence={
            "source_metadata": {
                "provider": "nflverse",
                "dataset": "player_stats",
                "stats": {
                    "carries": 8,
                    "targets": 2,
                    "receptions": 1,
                    "rushing_yards": 35,
                    "receiving_yards": 8,
                },
                "stat_context": {
                    "prior_games": 3,
                    "baseline": {
                        "touches": 20.0,
                        "targets": 6.0,
                        "scrimmage_yards": 105.0,
                    },
                    "current": {
                        "touches": 9.0,
                        "targets": 2.0,
                        "scrimmage_yards": 43.0,
                    },
                    "deltas": {
                        "touches": -11.0,
                        "targets": -4.0,
                        "scrimmage_yards": -62.0,
                    },
                },
            }
        },
    )

    signal = SignalProcessor().process(event, entities=[])
    context = signal.evidence["statistical_interpretation"]["context"]

    assert context["trend_adjustment"] < 0
    assert any(
        "below prior-week average" in reason
        for reason in signal.evidence["statistical_interpretation"]["reasons"]
    )
