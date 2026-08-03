import pytest

from gridiron_cortex.understand.signal_processor import SignalProcessor
from gridiron_gpt.football_state.models.draft_context import CanonicalDraftContext, DraftCapitalTier
from gridiron_gpt.football_state.services.draft_event_factory import DraftEventFactory


def context(**overrides):
    values = {
        "player_id": "rookie-rb",
        "player_name": "Rookie Runner",
        "draft_year": 2026,
        "draft_round": 1,
        "draft_pick": 18,
        "college": "Example State",
        "drafted_team": "ATL",
        "evidence": {"provider": "nflverse"},
    }
    values.update(overrides)
    return CanonicalDraftContext(**values)


def test_first_rounder_is_premium_capital():
    assert context().capital_tier == DraftCapitalTier.PREMIUM


def test_round_two_or_three_is_early_capital():
    assert context(draft_round=3, draft_pick=80).capital_tier == DraftCapitalTier.EARLY


def test_late_rounder_is_late_capital():
    assert context(draft_round=7, draft_pick=220).capital_tier == DraftCapitalTier.LATE


def test_undrafted_player_is_explicit():
    assert context(draft_round=None, draft_pick=None).capital_tier == DraftCapitalTier.UNDRAFTED


def test_rookie_status_is_season_relative():
    draft = context()
    assert draft.is_rookie(2026) is True
    assert draft.is_rookie(2027) is False


def test_premium_rookie_capital_is_small_positive_prior():
    event = DraftEventFactory().build(context(), season=2026)
    assert event.sentiment == "positive"
    assert 0 < event.impact_score <= 0.2


def test_veteran_draft_capital_does_not_keep_boosting_score():
    event = DraftEventFactory().build(context(draft_year=2023), season=2026)
    assert event.sentiment == "neutral"
    assert event.impact_score == 0


def test_draft_event_passes_through_normal_signal_processing():
    event = DraftEventFactory().build(context(), season=2026)
    signal = SignalProcessor().process(event, entities=[])
    assert signal.signal_type == "draft_context"
    assert signal.impact_score > 0


def test_invalid_round_is_rejected():
    with pytest.raises(ValueError, match="draft_round"):
        context(draft_round=8)
