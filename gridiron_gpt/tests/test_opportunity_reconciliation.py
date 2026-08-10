import pytest

from gridiron_gpt.football_state.models.opportunity_change import (
    OpportunityChange,
    OpportunityDirection,
)
from gridiron_gpt.football_state.models.opportunity_reconciliation import OpportunityConfirmation
from gridiron_gpt.football_state.models.usage_state import CanonicalUsageState
from gridiron_gpt.football_state.models.usage_trend import UsageTrendDirection, UsageTrendResult
from gridiron_gpt.football_state.services.opportunity_reconciliation_service import OpportunityReconciliationService


def prediction(direction=OpportunityDirection.INCREASED, player_id="allgeier"):
    return OpportunityChange(
        source_player_id="bijan",
        source_player_name="Bijan Robinson",
        affected_player_id=player_id,
        affected_player_name="Tyler Allgeier",
        relationship_type="backs_up",
        direction=direction,
        magnitude=0.55,
        reason="Bijan Robinson --backs_up(-0.55)--> Tyler Allgeier",
    )


def observed(direction, player_id="allgeier", prior_games=3):
    current = CanonicalUsageState(
        player_id=player_id,
        player_name="Tyler Allgeier",
        season=2026,
        week=4,
        carries=15,
        targets=3,
    )
    return UsageTrendResult(
        player_id=player_id,
        player_name="Tyler Allgeier",
        direction=direction,
        current=current,
        prior_games=prior_games,
        reason=f"usage trend {direction.value}",
    )


def test_predicted_increase_confirmed_by_rising_usage():
    result = OpportunityReconciliationService().reconcile(
        prediction(), observed(UsageTrendDirection.RISING)
    )

    assert result.confirmation == OpportunityConfirmation.CONFIRMED
    assert "confirmed" in result.reason


def test_predicted_increase_contradicted_by_falling_usage():
    result = OpportunityReconciliationService().reconcile(
        prediction(), observed(UsageTrendDirection.FALLING)
    )

    assert result.confirmation == OpportunityConfirmation.CONTRADICTED


def test_predicted_decrease_confirmed_by_falling_usage():
    result = OpportunityReconciliationService().reconcile(
        prediction(OpportunityDirection.DECREASED),
        observed(UsageTrendDirection.FALLING),
    )

    assert result.confirmation == OpportunityConfirmation.CONFIRMED


def test_predicted_decrease_contradicted_by_rising_usage():
    result = OpportunityReconciliationService().reconcile(
        prediction(OpportunityDirection.DECREASED),
        observed(UsageTrendDirection.RISING),
    )

    assert result.confirmation == OpportunityConfirmation.CONTRADICTED


@pytest.mark.parametrize(
    "direction",
    [UsageTrendDirection.STABLE, UsageTrendDirection.MIXED, UsageTrendDirection.UNKNOWN],
)
def test_non_directional_usage_is_inconclusive(direction):
    result = OpportunityReconciliationService().reconcile(prediction(), observed(direction))

    assert result.confirmation == OpportunityConfirmation.INCONCLUSIVE


def test_more_history_produces_higher_confidence():
    service = OpportunityReconciliationService()

    shallow = service.reconcile(prediction(), observed(UsageTrendDirection.RISING, prior_games=1))
    mature = service.reconcile(prediction(), observed(UsageTrendDirection.RISING, prior_games=3))

    assert mature.confidence > shallow.confidence


def test_player_identity_must_match():
    with pytest.raises(ValueError, match="identities"):
        OpportunityReconciliationService().reconcile(
            prediction(), observed(UsageTrendDirection.RISING, player_id="other")
        )
