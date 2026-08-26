import pytest

from gridiron_gpt.draft.fantasy_draft_settings import FantasyDraftSettings


def test_default_settings_are_twelve_team_slot_one() -> None:
    settings = FantasyDraftSettings()

    assert settings.league_size == 12
    assert settings.draft_slot == 1


def test_settings_accept_valid_league_size_and_slot() -> None:
    settings = FantasyDraftSettings(league_size=10, draft_slot=7)

    assert settings.league_size == 10
    assert settings.draft_slot == 7


def test_league_size_must_support_a_real_draft() -> None:
    with pytest.raises(ValueError, match="league_size"):
        FantasyDraftSettings(league_size=1, draft_slot=1)


def test_draft_slot_cannot_exceed_league_size() -> None:
    with pytest.raises(ValueError, match="draft_slot"):
        FantasyDraftSettings(league_size=10, draft_slot=11)


def test_draft_slot_must_be_positive() -> None:
    with pytest.raises(ValueError, match="draft_slot"):
        FantasyDraftSettings(league_size=12, draft_slot=0)
