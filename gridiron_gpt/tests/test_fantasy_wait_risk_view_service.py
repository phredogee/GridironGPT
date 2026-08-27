from types import SimpleNamespace

from gridiron_gpt.draft.fantasy_wait_risk_view_service import FantasyWaitRiskViewService


def _player(player_id: str, score: float):
    return SimpleNamespace(
        player_id=player_id,
        player_name=player_id,
        ranking_score=score,
    )


def _market(adp: float | None):
    return SimpleNamespace(consensus_adp=adp)


def test_view_derives_current_and_next_pick_from_live_draft_count() -> None:
    service = FantasyWaitRiskViewService(league_size=12, draft_slot=8)
    player = _player("wr-1", 90.0)

    result = service.evaluate(player, _market(10.4), drafted_count=7)

    assert result.current_pick == 8
    assert result.next_pick == 17
    assert result.picks_until_next_turn == 9


def test_view_reports_high_wait_risk_for_early_adp() -> None:
    service = FantasyWaitRiskViewService(league_size=12, draft_slot=8)

    result = service.evaluate(_player("wr-1", 90.0), _market(10.4), drafted_count=7)

    assert result.risk_level == "high"
    assert result.recommendation == "unlikely_available"
    assert result.market_gap == 6.6


def test_view_reports_low_wait_risk_for_late_adp() -> None:
    service = FantasyWaitRiskViewService(league_size=12, draft_slot=8)

    result = service.evaluate(_player("wr-2", 87.0), _market(25.2), drafted_count=7)

    assert result.risk_level == "low"
    assert result.recommendation == "likely_available"
    assert result.market_gap == -8.2


def test_view_keeps_missing_adp_unknown() -> None:
    service = FantasyWaitRiskViewService(league_size=12, draft_slot=8)

    result = service.evaluate(_player("te-1", 84.0), _market(None), drafted_count=7)

    assert result.risk_level == "unknown"
    assert result.recommendation == "unknown"
    assert result.market_gap is None


def test_view_does_not_mutate_authoritative_ranking_score() -> None:
    service = FantasyWaitRiskViewService(league_size=12, draft_slot=8)
    player = _player("qb-1", 91.23)

    result = service.evaluate(player, _market(9.5), drafted_count=7)

    assert result.ranking_score == 91.23
    assert player.ranking_score == 91.23
