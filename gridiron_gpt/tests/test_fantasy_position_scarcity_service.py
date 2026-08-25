from types import SimpleNamespace

from gridiron_gpt.draft.fantasy_position_scarcity_service import (
    FantasyPositionScarcityService,
)


def _player(
    player_id: str,
    position: str,
    ranking_score: float,
    tier: int | None,
):
    return SimpleNamespace(
        player_id=player_id,
        player_name=player_id,
        position=position,
        ranking_score=ranking_score,
        tier=tier,
    )


def test_large_same_position_drop_is_high_scarcity() -> None:
    service = FantasyPositionScarcityService()
    players = [
        _player("rb-1", "RB", 92.0, 1),
        _player("rb-2", "RB", 82.0, 2),
        _player("wr-1", "WR", 91.0, 1),
    ]

    result = service.evaluate(players[0], players)

    assert result.player_id == "rb-1"
    assert result.position == "RB"
    assert result.current_score == 92.0
    assert result.next_score == 82.0
    assert result.score_drop == 10.0
    assert result.scarcity_level == "high"


def test_crossing_tier_boundary_is_reported_as_tier_cliff() -> None:
    service = FantasyPositionScarcityService()
    players = [
        _player("wr-1", "WR", 88.0, 2),
        _player("wr-2", "WR", 84.0, 3),
        _player("wr-3", "WR", 83.0, 3),
    ]

    result = service.evaluate(players[0], players)

    assert result.current_tier == 2
    assert result.next_tier == 3
    assert result.tier_cliff is True


def test_comparable_same_position_depth_is_low_scarcity() -> None:
    service = FantasyPositionScarcityService()
    players = [
        _player("wr-1", "WR", 88.0, 2),
        _player("wr-2", "WR", 87.0, 2),
        _player("wr-3", "WR", 86.5, 2),
    ]

    result = service.evaluate(players[0], players)

    assert result.score_drop == 1.0
    assert result.tier_cliff is False
    assert result.remaining_same_position == 2
    assert result.scarcity_level == "low"


def test_other_positions_do_not_affect_same_position_scarcity() -> None:
    service = FantasyPositionScarcityService()
    players = [
        _player("te-1", "TE", 90.0, 1),
        _player("rb-1", "RB", 89.5, 1),
        _player("wr-1", "WR", 89.0, 1),
        _player("te-2", "TE", 78.0, 2),
    ]

    result = service.evaluate(players[0], players)

    assert result.next_score == 78.0
    assert result.score_drop == 12.0
    assert result.remaining_same_position == 1


def test_service_does_not_mutate_production_ranking_score() -> None:
    service = FantasyPositionScarcityService()
    candidate = _player("rb-1", "RB", 91.5, 1)
    alternative = _player("rb-2", "RB", 84.0, 2)

    service.evaluate(candidate, [candidate, alternative])

    assert candidate.ranking_score == 91.5
    assert alternative.ranking_score == 84.0


def test_last_available_player_at_position_is_high_scarcity() -> None:
    service = FantasyPositionScarcityService()
    candidate = _player("te-1", "TE", 84.0, 2)

    result = service.evaluate(
        candidate,
        [candidate, _player("wr-1", "WR", 83.0, 3)],
    )

    assert result.next_score is None
    assert result.next_tier is None
    assert result.remaining_same_position == 0
    assert result.scarcity_level == "high"


def test_same_player_id_is_excluded_even_when_object_is_reconstructed() -> None:
    service = FantasyPositionScarcityService()
    candidate = _player("rb-1", "RB", 92.0, 1)
    reconstructed_candidate = _player("rb-1", "RB", 92.0, 1)
    next_rb = _player("rb-2", "RB", 84.0, 2)

    result = service.evaluate(
        candidate,
        [reconstructed_candidate, next_rb],
    )

    assert result.next_score == 84.0
    assert result.remaining_same_position == 1


def test_position_matching_is_case_insensitive() -> None:
    service = FantasyPositionScarcityService()
    candidate = _player("wr-1", "wr", 88.0, 2)
    next_wr = _player("wr-2", "WR", 86.0, 2)

    result = service.evaluate(candidate, [candidate, next_wr])

    assert result.position == "WR"
    assert result.next_score == 86.0
    assert result.remaining_same_position == 1


def test_tier_cliff_with_modest_drop_is_meaningful_scarcity() -> None:
    service = FantasyPositionScarcityService()
    candidate = _player("qb-1", "QB", 90.0, 1)
    next_qb = _player("qb-2", "QB", 88.0, 2)

    result = service.evaluate(candidate, [candidate, next_qb])

    assert result.score_drop == 2.0
    assert result.tier_cliff is True
    assert result.scarcity_level == "medium"


def test_higher_ranked_alternative_never_creates_negative_score_drop() -> None:
    service = FantasyPositionScarcityService()
    candidate = _player("wr-2", "WR", 87.0, 2)
    higher_wr = _player("wr-1", "WR", 90.0, 1)

    result = service.evaluate(candidate, [candidate, higher_wr])

    assert result.next_score == 90.0
    assert result.score_drop == 0.0


def test_missing_tier_information_does_not_create_false_tier_cliff() -> None:
    service = FantasyPositionScarcityService()
    candidate = _player("rb-1", "RB", 88.0, None)
    next_rb = _player("rb-2", "RB", 86.0, None)

    result = service.evaluate(candidate, [candidate, next_rb])

    assert result.current_tier is None
    assert result.next_tier is None
    assert result.tier_cliff is False
    assert result.scarcity_level == "low"
