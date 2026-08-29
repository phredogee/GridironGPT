from types import SimpleNamespace

from gridiron_gpt.draft.draft_board_state import DraftBoardState, DraftOwnership
from gridiron_gpt.draft.fantasy_position_run_draft_state import build_position_run_from_draft_state


def _player(player_id: str, position: str, ranking_score: float = 80.0):
    return SimpleNamespace(
        player_id=player_id,
        position=position,
        ranking_score=ranking_score,
    )


def test_ordered_draft_state_drives_recent_position_run() -> None:
    state = DraftBoardState()
    players = {
        "rb-1": _player("rb-1", "RB"),
        "wr-1": _player("wr-1", "WR"),
        "wr-2": _player("wr-2", "WR"),
        "qb-1": _player("qb-1", "QB"),
        "wr-3": _player("wr-3", "WR"),
    }
    for player_id in ["rb-1", "wr-1", "wr-2", "qb-1", "wr-3"]:
        state.mark_drafted(player_id)

    result = build_position_run_from_draft_state(state, players)

    assert result.level == "developing"
    assert result.position == "WR"
    assert result.position_count == 3
    assert result.window_size == 5


def test_my_team_and_other_team_picks_both_count_toward_market_momentum() -> None:
    state = DraftBoardState()
    players = {
        "wr-1": _player("wr-1", "WR"),
        "wr-2": _player("wr-2", "WR"),
        "wr-3": _player("wr-3", "WR"),
        "rb-1": _player("rb-1", "RB"),
        "qb-1": _player("qb-1", "QB"),
    }
    state.mark_drafted("wr-1", DraftOwnership.OTHER_TEAM)
    state.mark_drafted("wr-2", DraftOwnership.MY_TEAM)
    state.mark_drafted("rb-1", DraftOwnership.OTHER_TEAM)
    state.mark_drafted("wr-3", DraftOwnership.OTHER_TEAM)
    state.mark_drafted("qb-1", DraftOwnership.MY_TEAM)

    result = build_position_run_from_draft_state(state, players)

    assert result.level == "developing"
    assert result.position == "WR"


def test_missing_player_lookup_is_ignored_without_losing_pick_order() -> None:
    state = DraftBoardState()
    players = {
        "wr-1": _player("wr-1", "WR"),
        "wr-2": _player("wr-2", "WR"),
        "wr-3": _player("wr-3", "WR"),
        "rb-1": _player("rb-1", "RB"),
    }
    for player_id in ["wr-1", "missing", "wr-2", "rb-1", "wr-3"]:
        state.mark_drafted(player_id)

    result = build_position_run_from_draft_state(state, players)

    assert result.level == "developing"
    assert result.position == "WR"
    assert result.window_size == 5


def test_position_run_adapter_does_not_mutate_authoritative_scores() -> None:
    state = DraftBoardState()
    players = {
        "wr-1": _player("wr-1", "WR", 91.25),
        "wr-2": _player("wr-2", "WR", 86.86),
        "wr-3": _player("wr-3", "WR", 84.28),
        "rb-1": _player("rb-1", "RB", 86.51),
        "qb-1": _player("qb-1", "QB", 78.27),
    }
    for player_id in players:
        state.mark_drafted(player_id)
    before = {player_id: player.ranking_score for player_id, player in players.items()}

    build_position_run_from_draft_state(state, players)

    after = {player_id: player.ranking_score for player_id, player in players.items()}
    assert after == before
