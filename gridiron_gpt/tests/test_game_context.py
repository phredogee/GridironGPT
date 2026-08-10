from datetime import datetime, timezone

import pytest

from gridiron_gpt.football_state.models.game_context import (
    CanonicalGameContext,
    GameStatus,
    VenueSide,
)


KICKOFF = datetime(2026, 9, 20, 17, 0, tzinfo=timezone.utc)


def game(**overrides):
    values = {
        "game_id": "2026_03_ATL_TB",
        "season": 2026,
        "week": 3,
        "season_type": "REG",
        "home_team": "ATL",
        "away_team": "TB",
        "kickoff_at": KICKOFF,
    }
    values.update(overrides)
    return CanonicalGameContext(**values)


def test_game_context_identifies_opponent_for_either_team():
    context = game()

    assert context.opponent_for("ATL") == "TB"
    assert context.opponent_for("TB") == "ATL"


def test_game_context_identifies_home_and_away_side():
    context = game()

    assert context.venue_side_for("ATL") == VenueSide.HOME
    assert context.venue_side_for("TB") == VenueSide.AWAY


def test_neutral_site_overrides_home_away_label():
    context = game(neutral_site=True)

    assert context.venue_side_for("ATL") == VenueSide.NEUTRAL
    assert context.venue_side_for("TB") == VenueSide.NEUTRAL


def test_final_game_is_completed():
    assert game(status=GameStatus.FINAL).completed is True
    assert game().completed is False


def test_unknown_team_is_rejected_for_opponent_lookup():
    with pytest.raises(ValueError, match="not part"):
        game().opponent_for("NO")


def test_same_team_cannot_be_home_and_away():
    with pytest.raises(ValueError, match="must differ"):
        game(away_team="ATL")


def test_kickoff_must_be_timezone_aware():
    with pytest.raises(ValueError, match="timezone-aware"):
        game(kickoff_at=datetime(2026, 9, 20, 12, 0))


def test_game_context_round_trips():
    original = game(
        status=GameStatus.FINAL,
        evidence={"provider": "nflverse", "schedule_version": 1},
    )

    restored = CanonicalGameContext.from_dict(original.to_dict())

    assert restored == original
    assert restored.status == GameStatus.FINAL
    assert restored.kickoff_at == KICKOFF
