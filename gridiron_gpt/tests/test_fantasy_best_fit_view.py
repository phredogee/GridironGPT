from types import SimpleNamespace

from gridiron_gpt.draft.fantasy_best_fit_view import build_best_fit_views


def _player(player_id: str, name: str, position: str, ranking_score: float):
    return SimpleNamespace(player_id=player_id, player_name=name, position=position, ranking_score=ranking_score)


def _market(draft_value: float | None):
    return SimpleNamespace(draft_value=draft_value)


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
