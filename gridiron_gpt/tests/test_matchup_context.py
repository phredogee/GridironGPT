import pytest

from gridiron_gpt.football_state.models.matchup_context import MatchupTendency, OpponentMetric
from gridiron_gpt.football_state.services.matchup_context_service import MatchupContextService


def classify(metrics):
    return MatchupContextService().classify(
        team="ATL",
        opponent="TB",
        position="RB",
        season=2026,
        week=4,
        metrics=metrics,
        source="nflverse team defense",
        evidence={"provider": "nflverse"},
    )


def metric(name, value, average, higher_is_favorable=True, sample_games=4):
    return OpponentMetric(
        name=name,
        value=value,
        league_average=average,
        higher_is_favorable=higher_is_favorable,
        sample_games=sample_games,
    )


def test_favorable_matchup_from_above_average_allowed_production():
    result = classify([
        metric("rb_rushing_yards_allowed", 130, 100),
        metric("rb_targets_allowed", 8, 6),
    ])

    assert result.tendency == MatchupTendency.FAVORABLE
    assert result.score > 0
    assert result.confidence > 0


def test_unfavorable_matchup_from_suppressed_allowed_production():
    result = classify([
        metric("rb_rushing_yards_allowed", 70, 100),
        metric("rb_targets_allowed", 4, 6),
    ])

    assert result.tendency == MatchupTendency.UNFAVORABLE
    assert result.score < 0


def test_lower_is_better_metric_can_reverse_semantics():
    result = classify([
        metric("opponent_stuff_rate", 0.12, 0.20, higher_is_favorable=False),
    ])

    assert result.tendency == MatchupTendency.FAVORABLE


def test_small_deviation_is_neutral():
    result = classify([
        metric("rb_rushing_yards_allowed", 105, 100),
        metric("rb_targets_allowed", 6.2, 6),
    ])

    assert result.tendency == MatchupTendency.NEUTRAL


def test_no_sample_returns_unknown_instead_of_guessing():
    result = classify([
        metric("rb_rushing_yards_allowed", 140, 100, sample_games=0),
    ])

    assert result.tendency == MatchupTendency.UNKNOWN
    assert result.confidence == 0
    assert result.metrics == ()


def test_zero_league_average_does_not_divide_by_zero():
    result = classify([metric("rare_metric", 1, 0)])

    assert result.tendency == MatchupTendency.NEUTRAL
    assert result.score == 0


def test_confidence_increases_with_sample_size():
    shallow = classify([metric("rb_targets_allowed", 8, 6, sample_games=1)])
    mature = classify([metric("rb_targets_allowed", 8, 6, sample_games=6)])

    assert mature.confidence > shallow.confidence


def test_provenance_is_preserved():
    result = classify([metric("rb_targets_allowed", 8, 6)])

    assert result.source == "nflverse team defense"
    assert result.evidence["provider"] == "nflverse"


def test_reason_exposes_observable_metric_basis():
    result = classify([metric("rb_targets_allowed", 8, 6)])

    assert "rb_targets_allowed" in result.reason
    assert "league average" in result.reason


def test_invalid_team_pair_is_rejected():
    with pytest.raises(ValueError, match="must differ"):
        MatchupContextService().classify(
            team="ATL",
            opponent="ATL",
            position="RB",
            season=2026,
            week=4,
            metrics=[],
        )
