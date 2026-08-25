from types import SimpleNamespace

from gridiron_gpt.draft.fantasy_best_fit_service import FantasyBestFitService


def _player(player_id: str, name: str, position: str, ranking_score: float):
    return SimpleNamespace(
        player_id=player_id,
        player_name=name,
        position=position,
        ranking_score=ranking_score,
    )


def _market(draft_value: float | None):
    return SimpleNamespace(draft_value=draft_value)


def _scarcity(level: str):
    return SimpleNamespace(scarcity_level=level)


def test_active_roster_need_can_break_close_ranking_gap():
    service = FantasyBestFitService()
    roster = [_player("my-rb-1", "RB One", "RB", 80), _player("my-rb-2", "RB Two", "RB", 79)]
    candidates = [
        _player("rb", "Higher RB", "RB", 82),
        _player("wr", "Needed WR", "WR", 78),
    ]

    result = service.recommend(candidates, roster, {"rb": _market(0), "wr": _market(0)})

    assert result[0].score.player_id == "wr"
    assert result[0].roster_need is True
    assert result[1].roster_need is False


def test_large_ranking_gap_is_not_overridden_by_roster_need():
    service = FantasyBestFitService()
    roster = [_player("my-rb-1", "RB One", "RB", 80), _player("my-rb-2", "RB Two", "RB", 79)]
    candidates = [
        _player("rb", "Elite RB", "RB", 95),
        _player("wr", "Needed WR", "WR", 75),
    ]

    result = service.recommend(candidates, roster, {"rb": _market(0), "wr": _market(0)})

    assert result[0].score.player_id == "rb"


def test_positive_draft_value_provides_modest_fit_bonus():
    service = FantasyBestFitService()
    roster = []
    candidates = [
        _player("a", "Player A", "WR", 80),
        _player("b", "Player B", "WR", 79),
    ]

    result = service.recommend(candidates, roster, {"a": _market(0), "b": _market(8)})

    assert result[0].score.player_id == "b"
    assert result[0].draft_value == 8


def test_service_does_not_mutate_production_ranking_score():
    service = FantasyBestFitService()
    candidate = _player("wr", "Wide Receiver", "WR", 77.5)

    service.recommend([candidate], [], {"wr": _market(12)})

    assert candidate.ranking_score == 77.5


def test_missing_market_view_is_neutral():
    service = FantasyBestFitService()
    candidate = _player("wr", "Wide Receiver", "WR", 77.5)

    result = service.recommend([candidate], [], {})

    assert result[0].draft_value == 0.0
    assert result[0].fit_score == 85.5


def test_limit_and_zero_limit_are_respected():
    service = FantasyBestFitService()
    candidates = [
        _player("a", "A", "QB", 90),
        _player("b", "B", "RB", 89),
        _player("c", "C", "WR", 88),
    ]

    assert len(service.recommend(candidates, [], {}, limit=2)) == 2
    assert service.recommend(candidates, [], {}, limit=0) == []


def test_high_scarcity_can_break_close_best_fit_gap():
    service = FantasyBestFitService()
    candidates = [
        _player("wr", "Wide Receiver", "WR", 80),
        _player("te", "Tight End", "TE", 79),
    ]

    result = service.recommend(
        candidates,
        [],
        {"wr": _market(0), "te": _market(0)},
        scarcity_views={
            "wr": _scarcity("low"),
            "te": _scarcity("high"),
        },
    )

    assert result[0].score.player_id == "te"
    assert result[0].scarcity_level == "high"
    assert result[0].scarcity_bonus > 0


def test_high_scarcity_cannot_overcome_large_production_ranking_gap():
    service = FantasyBestFitService()
    candidates = [
        _player("wr", "Elite Wide Receiver", "WR", 95),
        _player("te", "Scarce Tight End", "TE", 75),
    ]

    result = service.recommend(
        candidates,
        [],
        {"wr": _market(0), "te": _market(0)},
        scarcity_views={
            "wr": _scarcity("low"),
            "te": _scarcity("high"),
        },
    )

    assert result[0].score.player_id == "wr"


def test_scarcity_adjustment_does_not_mutate_production_ranking_score():
    service = FantasyBestFitService()
    candidate = _player("te", "Tight End", "TE", 81.25)

    result = service.recommend(
        [candidate],
        [],
        {"te": _market(0)},
        scarcity_views={"te": _scarcity("high")},
    )

    assert candidate.ranking_score == 81.25
    assert result[0].scarcity_level == "high"
    assert result[0].scarcity_bonus > 0
