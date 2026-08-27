from types import SimpleNamespace

import pytest

from gridiron_gpt.draft.fantasy_wait_risk_service import FantasyWaitRiskService


def _player(score: float = 88.5):
    return SimpleNamespace(player_id="player-1", ranking_score=score)


def test_exact_positive_three_pick_gap_is_high_risk() -> None:
    result = FantasyWaitRiskService().evaluate(
        _player(), current_pick=8, next_pick=17, consensus_adp=14.0
    )

    assert result.market_gap == 3.0
    assert result.risk_level == "high"
    assert result.recommendation == "unlikely_available"


def test_exact_negative_three_pick_gap_is_low_risk() -> None:
    result = FantasyWaitRiskService().evaluate(
        _player(), current_pick=8, next_pick=17, consensus_adp=20.0
    )

    assert result.market_gap == -3.0
    assert result.risk_level == "low"
    assert result.recommendation == "likely_available"


def test_fractional_market_gap_is_rounded_once_for_output() -> None:
    result = FantasyWaitRiskService().evaluate(
        _player(), current_pick=8, next_pick=17, consensus_adp=15.26
    )

    assert result.market_gap == 1.7
    assert result.risk_level == "medium"


def test_same_current_and_next_pick_has_zero_wait() -> None:
    result = FantasyWaitRiskService().evaluate(
        _player(), current_pick=8, next_pick=8, consensus_adp=8.0
    )

    assert result.picks_until_next_turn == 0
    assert result.market_gap == 0.0
    assert result.risk_level == "medium"


def test_next_pick_before_current_pick_is_rejected() -> None:
    with pytest.raises(ValueError, match="next_pick"):
        FantasyWaitRiskService().evaluate(
            _player(), current_pick=17, next_pick=8, consensus_adp=12.0
        )


def test_extreme_early_adp_remains_high_risk() -> None:
    result = FantasyWaitRiskService().evaluate(
        _player(), current_pick=50, next_pick=61, consensus_adp=2.0
    )

    assert result.risk_level == "high"
    assert result.recommendation == "unlikely_available"


def test_extreme_late_adp_remains_low_risk() -> None:
    result = FantasyWaitRiskService().evaluate(
        _player(), current_pick=2, next_pick=11, consensus_adp=150.0
    )

    assert result.risk_level == "low"
    assert result.recommendation == "likely_available"


def test_repeated_evaluations_are_deterministic() -> None:
    service = FantasyWaitRiskService()
    player = _player(91.23)
    kwargs = dict(current_pick=8, next_pick=17, consensus_adp=10.4)

    first = service.evaluate(player, **kwargs)
    second = service.evaluate(player, **kwargs)

    assert first == second
    assert player.ranking_score == 91.23
