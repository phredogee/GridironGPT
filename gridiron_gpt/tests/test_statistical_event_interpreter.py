from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.understand.signal_processor import SignalProcessor
from gridiron_cortex.understand.statistical_event_interpreter import (
    StatisticalEventInterpreter,
)


def stats_event(position="RB", stats=None):
    return RawEvent(
        headline="Bijan Robinson (ATL) 2026 Week 1 statistical line",
        source="nflverse player stats",
        player="Bijan Robinson",
        team="ATL",
        position=position,
        evidence={
            "source_metadata": {
                "provider": "nflverse",
                "dataset": "player_stats",
                "season": 2026,
                "week": 1,
                "stats": stats or {},
            }
        },
    )


def test_interpreter_detects_nflverse_player_stats():
    interpreter = StatisticalEventInterpreter()
    assert interpreter.can_interpret(stats_event()) is True


def test_skill_player_usage_produces_structured_indicators():
    interpreter = StatisticalEventInterpreter()
    result = interpreter.interpret(
        stats_event(
            stats={
                "carries": 18,
                "targets": 6,
                "receptions": 5,
                "rushing_yards": 91,
                "receiving_yards": 38,
                "rushing_tds": 1,
            }
        )
    )

    assert result.indicators["touches"] == 23
    assert result.indicators["targets"] == 6
    assert result.indicators["touchdowns"] == 1
    assert result.sentiment == "positive"
    assert result.impact_score > 0


def test_qb_turnovers_reduce_statistical_impact():
    interpreter = StatisticalEventInterpreter()
    clean = interpreter.interpret(
        stats_event(
            position="QB",
            stats={"passing_yards": 280, "passing_tds": 3},
        )
    )
    turnover_heavy = interpreter.interpret(
        stats_event(
            position="QB",
            stats={
                "passing_yards": 280,
                "passing_tds": 3,
                "interceptions": 3,
            },
        )
    )

    assert turnover_heavy.impact_score < clean.impact_score


def test_signal_processor_bypasses_headline_keyword_interpretation():
    event = stats_event(
        stats={
            "carries": 20,
            "receptions": 4,
            "targets": 5,
            "rushing_yards": 110,
            "receiving_yards": 30,
            "rushing_tds": 1,
        }
    )
    event.headline = "Bijan Robinson limited statistical line"

    signal = SignalProcessor().process(event, entities=[])

    assert signal.signal_type == "statistics"
    assert signal.signal_category == "performance"
    assert signal.sentiment == "positive"
    assert signal.negative_hits == []
    assert signal.evidence["statistical_interpretation"]["method"] == "structured_player_stats"


def test_non_statistical_news_keeps_existing_path():
    event = RawEvent(
        headline="Bijan Robinson limited in practice",
        source="ESPN NFL",
        player="Bijan Robinson",
        team="ATL",
    )

    signal = SignalProcessor().process(event, entities=[])

    assert signal.signal_type == "news"
    assert "limited" in signal.negative_hits
