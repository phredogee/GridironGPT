import pandas as pd
import pytest

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.understand.signal_processor import SignalProcessor
from gridiron_gpt.ingestion.sources.nflverse_player_stats import NFLVersePlayerStatsAdapter


def loader(_seasons, _summary_level):
    rows = []
    for week, bijan_carries, allgeier_carries, bijan_targets, london_targets in [
        (1, 10, 10, 4, 8),
        (2, 12, 8, 5, 7),
        (3, 18, 4, 8, 6),
    ]:
        rows.extend([
            {"player_id": "bijan", "player_display_name": "Bijan Robinson", "position": "RB", "team": "ATL", "season": 2026, "week": week, "season_type": "REG", "carries": bijan_carries, "targets": bijan_targets, "receptions": max(bijan_targets - 1, 0), "rushing_yards": bijan_carries * 5, "receiving_yards": 30},
            {"player_id": "allgeier", "player_display_name": "Tyler Allgeier", "position": "RB", "team": "ATL", "season": 2026, "week": week, "season_type": "REG", "carries": allgeier_carries, "targets": 0, "receptions": 0, "rushing_yards": allgeier_carries * 4},
            {"player_id": "london", "player_display_name": "Drake London", "position": "WR", "team": "ATL", "season": 2026, "week": week, "season_type": "REG", "carries": 0, "targets": london_targets, "receptions": 5, "receiving_yards": 70},
        ])
    return pd.DataFrame(rows)


def _event(record):
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


def test_adapter_calculates_team_carry_and_target_share():
    records = NFLVersePlayerStatsAdapter(2026, loader=loader).fetch()
    week_three_bijan = next(
        r for r in records
        if r.player == "Bijan Robinson" and r.metadata["week"] == 3
    )
    share = week_three_bijan.metadata["team_share_context"]

    assert share["current"]["carry_share"] == pytest.approx(18 / 22, abs=1e-4)
    assert share["current"]["target_share"] == pytest.approx(8 / 14, abs=1e-4)
    assert share["prior_games"] == 2
    assert share["deltas"]["carry_share"] > 0
    assert share["deltas"]["target_share"] > 0


def test_rising_team_share_adds_positive_share_adjustment():
    records = NFLVersePlayerStatsAdapter(2026, loader=loader).fetch()
    record = next(
        r for r in records
        if r.player == "Bijan Robinson" and r.metadata["week"] == 3
    )

    with_share = SignalProcessor().process(_event(record), entities=[])
    without_share_event = _event(record)
    without_share_event.evidence["source_metadata"] = dict(
        without_share_event.evidence["source_metadata"]
    )
    without_share_event.evidence["source_metadata"]["team_share_context"] = None
    without_share = SignalProcessor().process(without_share_event, entities=[])

    with_context = with_share.evidence["statistical_interpretation"]["context"]
    without_context = without_share.evidence["statistical_interpretation"]["context"]

    assert with_context["share_adjustment"] > 0
    assert without_context["share_adjustment"] == 0.0
    assert with_share.impact_score >= without_share.impact_score
    assert any(
        "Carry share up" in reason
        for reason in with_share.evidence["statistical_interpretation"]["reasons"]
    )


def test_first_week_has_no_share_trend_adjustment():
    records = NFLVersePlayerStatsAdapter(2026, loader=loader).fetch()
    record = next(
        r for r in records
        if r.player == "Bijan Robinson" and r.metadata["week"] == 1
    )
    signal = SignalProcessor().process(_event(record), entities=[])
    context = signal.evidence["statistical_interpretation"]["context"]

    assert context["team_share"]["prior_games"] == 0
    assert context["share_adjustment"] == 0.0


def test_team_share_is_preserved_as_explainable_evidence():
    records = NFLVersePlayerStatsAdapter(2026, loader=loader).fetch()
    record = next(
        r for r in records
        if r.player == "Bijan Robinson" and r.metadata["week"] == 3
    )
    signal = SignalProcessor().process(_event(record), entities=[])
    share = signal.evidence["statistical_interpretation"]["context"]["team_share"]

    assert "baseline" in share
    assert "current" in share
    assert "deltas" in share
    assert share["current"]["carry_share"] > share["baseline"]["carry_share"]
