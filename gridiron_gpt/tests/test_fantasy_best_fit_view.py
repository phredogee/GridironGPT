from types import SimpleNamespace

from gridiron_gpt.draft.fantasy_best_fit_view import build_best_fit_views


def _player(
    player_id: str,
    name: str,
    position: str,
    ranking_score: float,
    tier: int | None = None,
):
    return SimpleNamespace(
        player_id=player_id,
        player_name=name,
        position=position,
        ranking_score=ranking_score,
        tier=tier,
    )


def _market(draft_value: float | None, tier: int | None = None):
    return SimpleNamespace(draft_value=draft_value, tier=tier)


def test_best_fit_view_explains_roster_need_and_value():
    roster = [_player("rb1", "RB One", "RB", 80), _player("rb2", "RB Two", "RB", 79)]
    candidate = _player("wr", "Needed WR", "WR", 78)

    views = build_best_fit_views([candidate], roster, {"wr": _market(6)})

    assert len(views) == 1
    assert views[0].score is candidate
    assert views[0].roster_need is True
    assert views[0].reason == "fills active roster need · positive draft value"


def test_best_fit_view_uses_board_position_as_neutral_reason():
    roster = []
    candidate = _player("qb", "Quarterback", "QB", 90)

    views = build_best_fit_views([candidate], roster, {"qb": _market(-2)})

    assert views[0].reason == "fills active roster need"


def test_best_fit_view_respects_limit():
    candidates = [
        _player("a", "A", "QB", 90),
        _player("b", "B", "RB", 89),
        _player("c", "C", "WR", 88),
    ]

    views = build_best_fit_views(candidates, [], {}, limit=2)

    assert len(views) == 2


def test_best_fit_view_calculates_high_scarcity_from_candidate_pool():
    candidates = [
        _player("rb-1", "Top RB", "RB", 90.0, 1),
        _player("rb-2", "Next RB", "RB", 80.5, 2),
        _player("wr-1", "Wide Receiver", "WR", 89.5, 1),
    ]

    views = build_best_fit_views(
        candidates,
        [],
        {player.player_id: _market(0) for player in candidates},
    )
    by_id = {view.score.player_id: view for view in views}

    assert by_id["rb-1"].scarcity_level == "high"
    assert by_id["rb-1"].scarcity_bonus > 0
    assert "high position scarcity" in by_id["rb-1"].reason
    assert "9.5-point drop" in by_id["rb-1"].reason
    assert "tier boundary" in by_id["rb-1"].reason


def test_best_fit_view_keeps_low_scarcity_quiet():
    candidates = [
        _player("rb-1", "RB One", "RB", 88.0, 2),
        _player("rb-2", "RB Two", "RB", 87.5, 2),
        _player("rb-3", "RB Three", "RB", 87.0, 2),
    ]

    views = build_best_fit_views(candidates, [], {})
    by_id = {view.score.player_id: view for view in views}

    assert by_id["rb-1"].scarcity_level == "low"
    assert by_id["rb-1"].scarcity_bonus == 0.0
    assert "scarcity" not in by_id["rb-1"].reason.lower()


def test_best_fit_view_scarcity_reacts_to_thinner_available_pool():
    rb1 = _player("rb-1", "RB One", "RB", 90.0, 1)
    rb2 = _player("rb-2", "RB Two", "RB", 89.0, 1)
    rb3 = _player("rb-3", "RB Three", "RB", 88.5, 1)
    rb4 = _player("rb-4", "RB Four", "RB", 79.0, 2)

    before = build_best_fit_views([rb1, rb2, rb3, rb4], [], {})
    after = build_best_fit_views([rb3, rb4], [], {})
    before_by_id = {view.score.player_id: view for view in before}
    after_by_id = {view.score.player_id: view for view in after}

    assert before_by_id["rb-1"].scarcity_level == "low"
    assert after_by_id["rb-3"].scarcity_level == "high"
    assert "9.5-point drop" in after_by_id["rb-3"].reason


def test_best_fit_view_exposes_take_now_timing_for_tier_cliff():
    candidates = [
        _player("rb-1", "Top RB", "RB", 91.0, 1),
        _player("rb-2", "Next RB", "RB", 82.0, 2),
    ]

    views = build_best_fit_views(candidates, [], {})
    by_id = {view.score.player_id: view for view in views}

    assert by_id["rb-1"].timing_decision == "take_now"
    assert by_id["rb-1"].timing_urgency == "high"
    assert "9.0" in by_id["rb-1"].timing_reason


def test_best_fit_view_exposes_can_wait_for_deep_same_tier_pool():
    candidates = [
        _player("wr-1", "WR One", "WR", 88.0, 2),
        _player("wr-2", "WR Two", "WR", 87.5, 2),
        _player("wr-3", "WR Three", "WR", 87.0, 2),
    ]

    views = build_best_fit_views(candidates, [], {})
    by_id = {view.score.player_id: view for view in views}

    assert by_id["wr-1"].timing_decision == "can_wait"
    assert by_id["wr-1"].timing_urgency == "low"
    assert "comparable" in by_id["wr-1"].timing_reason.lower()


def test_best_fit_view_pick_timing_preserves_ranking_score():
    candidates = [
        _player("te-1", "TE One", "TE", 87.75, 1),
        _player("te-2", "TE Two", "TE", 75.0, 2),
    ]

    views = build_best_fit_views(candidates, [], {})
    by_id = {view.score.player_id: view for view in views}

    assert by_id["te-1"].score.ranking_score == 87.75
    assert by_id["te-1"].timing_decision == "take_now"


def test_best_fit_view_uses_market_tier_when_score_has_no_tier():
    rb1 = _player("rb-1", "Top RB", "RB", 91.0)
    rb2 = _player("rb-2", "Next RB", "RB", 82.0)
    market_views = {
        "rb-1": _market(2.0, tier=1),
        "rb-2": _market(0.0, tier=2),
    }

    views = build_best_fit_views([rb1, rb2], [], market_views)
    by_id = {view.score.player_id: view for view in views}

    assert by_id["rb-1"].timing_decision == "take_now"
    assert by_id["rb-1"].timing_urgency == "high"
    assert "tier boundary" in by_id["rb-1"].reason
    assert rb1.ranking_score == 91.0
