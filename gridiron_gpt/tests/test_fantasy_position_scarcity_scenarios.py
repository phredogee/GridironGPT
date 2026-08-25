from types import SimpleNamespace

from gridiron_gpt.draft.fantasy_best_fit_service import FantasyBestFitService
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


def _market():
    return SimpleNamespace(draft_value=0.0)


def _scarcity_views(players):
    service = FantasyPositionScarcityService()
    return {
        player.player_id: service.evaluate(player, players)
        for player in players
    }


def test_rb_cliff_can_move_rb_ahead_of_close_wr() -> None:
    players = [
        _player("wr-1", "WR", 90.0, 1),
        _player("rb-1", "RB", 89.0, 1),
        _player("wr-2", "WR", 89.0, 1),
        _player("wr-3", "WR", 88.0, 1),
        _player("rb-2", "RB", 80.0, 2),
    ]
    views = _scarcity_views(players)

    result = FantasyBestFitService().recommend(
        players,
        [],
        {player.player_id: _market() for player in players},
        scarcity_views=views,
    )

    assert views["rb-1"].scarcity_level == "high"
    assert result[0].score.player_id == "rb-1"


def test_scarce_te_does_not_jump_elite_wr() -> None:
    players = [
        _player("wr-elite", "WR", 96.0, 1),
        _player("te-1", "TE", 82.0, 1),
        _player("te-2", "TE", 73.0, 2),
    ]
    views = _scarcity_views(players)

    result = FantasyBestFitService().recommend(
        players,
        [],
        {player.player_id: _market() for player in players},
        scarcity_views=views,
    )

    assert views["te-1"].scarcity_level == "high"
    assert result[0].score.player_id == "wr-elite"


def test_deep_same_tier_rb_pool_does_not_create_false_urgency() -> None:
    players = [
        _player("rb-1", "RB", 88.0, 2),
        _player("rb-2", "RB", 87.5, 2),
        _player("rb-3", "RB", 87.0, 2),
        _player("rb-4", "RB", 86.5, 2),
    ]

    view = FantasyPositionScarcityService().evaluate(players[0], players)

    assert view.remaining_same_position == 3
    assert view.score_drop == 0.5
    assert view.tier_cliff is False
    assert view.scarcity_level == "low"


def test_position_run_changes_scarcity_as_pool_thins() -> None:
    service = FantasyPositionScarcityService()
    rb1 = _player("rb-1", "RB", 90.0, 1)
    rb2 = _player("rb-2", "RB", 89.0, 1)
    rb3 = _player("rb-3", "RB", 88.5, 1)
    rb4 = _player("rb-4", "RB", 79.0, 2)

    before_run = service.evaluate(rb1, [rb1, rb2, rb3, rb4])
    after_run = service.evaluate(rb3, [rb3, rb4])

    assert before_run.scarcity_level == "low"
    assert before_run.tier_cliff is False
    assert after_run.scarcity_level == "high"
    assert after_run.tier_cliff is True
    assert after_run.score_drop == 9.5


def test_passing_on_last_top_tier_option_exposes_next_round_cost() -> None:
    service = FantasyPositionScarcityService()
    wr1 = _player("wr-1", "WR", 91.0, 1)
    wr2 = _player("wr-2", "WR", 83.0, 2)
    wr3 = _player("wr-3", "WR", 82.0, 2)

    view = service.evaluate(wr1, [wr1, wr2, wr3])

    assert view.next_score == 83.0
    assert view.score_drop == 8.0
    assert view.tier_cliff is True
    assert view.scarcity_level == "high"
    assert "score drop is 8.0" in view.reason
