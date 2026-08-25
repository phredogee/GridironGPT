from types import SimpleNamespace

from gridiron_gpt.draft.fantasy_pick_timing_service import FantasyPickTimingService
from gridiron_gpt.draft.fantasy_position_scarcity_service import (
    FantasyPositionScarcityService,
)


def _player(player_id: str, position: str, score: float, tier: int):
    return SimpleNamespace(
        player_id=player_id,
        player_name=player_id,
        position=position,
        ranking_score=score,
        tier=tier,
    )


def _scarcity(candidate, players):
    return FantasyPositionScarcityService().evaluate(candidate, players)


def test_take_now_when_waiting_crosses_large_tier_cliff() -> None:
    service = FantasyPickTimingService()
    rb1 = _player("rb-1", "RB", 91.0, 1)
    rb2 = _player("rb-2", "RB", 82.0, 2)
    players = [rb1, rb2]

    result = service.evaluate(
        rb1,
        scarcity=_scarcity(rb1, players),
        roster_need=True,
    )

    assert result.decision == "take_now"
    assert result.urgency == "high"
    assert "tier" in result.reason.lower()
    assert "9.0" in result.reason


def test_can_wait_when_comparable_same_tier_options_remain() -> None:
    service = FantasyPickTimingService()
    wr1 = _player("wr-1", "WR", 88.0, 2)
    wr2 = _player("wr-2", "WR", 87.5, 2)
    wr3 = _player("wr-3", "WR", 87.0, 2)
    players = [wr1, wr2, wr3]

    result = service.evaluate(
        wr1,
        scarcity=_scarcity(wr1, players),
        roster_need=False,
    )

    assert result.decision == "can_wait"
    assert result.urgency == "low"
    assert "comparable" in result.reason.lower()


def test_neutral_when_scarcity_is_medium_without_roster_need() -> None:
    service = FantasyPickTimingService()
    te1 = _player("te-1", "TE", 85.0, 2)
    te2 = _player("te-2", "TE", 81.5, 2)
    players = [te1, te2]

    result = service.evaluate(
        te1,
        scarcity=_scarcity(te1, players),
        roster_need=False,
    )

    assert result.decision == "neutral"
    assert result.urgency == "medium"


def test_roster_need_can_promote_medium_scarcity_to_take_now() -> None:
    service = FantasyPickTimingService()
    te1 = _player("te-1", "TE", 85.0, 2)
    te2 = _player("te-2", "TE", 81.5, 2)
    players = [te1, te2]

    result = service.evaluate(
        te1,
        scarcity=_scarcity(te1, players),
        roster_need=True,
    )

    assert result.decision == "take_now"
    assert result.urgency == "medium"
    assert "roster need" in result.reason.lower()


def test_pick_timing_never_mutates_ranking_score() -> None:
    service = FantasyPickTimingService()
    rb1 = _player("rb-1", "RB", 91.25, 1)
    rb2 = _player("rb-2", "RB", 80.0, 2)
    players = [rb1, rb2]

    service.evaluate(
        rb1,
        scarcity=_scarcity(rb1, players),
        roster_need=True,
    )

    assert rb1.ranking_score == 91.25
