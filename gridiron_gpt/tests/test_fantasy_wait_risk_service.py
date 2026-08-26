from types import SimpleNamespace

from gridiron_gpt.draft.fantasy_wait_risk_service import FantasyWaitRiskService


def _player(player_id: str, score: float):
    return SimpleNamespace(
        player_id=player_id,
        player_name=player_id,
        ranking_score=score,
    )


def test_high_risk_when_adp_is_well_before_next_pick() -> None:
    service = FantasyWaitRiskService()
    player = _player("wr-1", 90.0)

    result = service.evaluate(
        player,
        current_pick=8,
        next_pick=17,
        consensus_adp=10.4,
    )

    assert result.risk_level == "high"
    assert result.recommendation == "unlikely_available"
    assert result.picks_until_next_turn == 9
    assert result.market_gap == 6.6


def test_low_risk_when_adp_is_well_after_next_pick() -> None:
    service = FantasyWaitRiskService()
    player = _player("wr-2", 87.0)

    result = service.evaluate(
        player,
        current_pick=8,
        next_pick=17,
        consensus_adp=25.2,
    )

    assert result.risk_level == "low"
    assert result.recommendation == "likely_available"
    assert result.market_gap == -8.2


def test_medium_risk_when_adp_is_near_next_pick() -> None:
    service = FantasyWaitRiskService()
    player = _player("rb-1", 88.0)

    result = service.evaluate(
        player,
        current_pick=8,
        next_pick=17,
        consensus_adp=16.0,
    )

    assert result.risk_level == "medium"
    assert result.recommendation == "uncertain"
    assert result.market_gap == 1.0


def test_missing_adp_returns_unknown_without_guessing() -> None:
    service = FantasyWaitRiskService()
    player = _player("te-1", 84.0)

    result = service.evaluate(
        player,
        current_pick=8,
        next_pick=17,
        consensus_adp=None,
    )

    assert result.risk_level == "unknown"
    assert result.recommendation == "unknown"
    assert result.market_gap is None
    assert "adp" in result.reason.lower()


def test_wait_risk_does_not_mutate_authoritative_ranking_score() -> None:
    service = FantasyWaitRiskService()
    player = _player("qb-1", 91.23)

    result = service.evaluate(
        player,
        current_pick=8,
        next_pick=17,
        consensus_adp=9.5,
    )

    assert result.ranking_score == 91.23
    assert player.ranking_score == 91.23
