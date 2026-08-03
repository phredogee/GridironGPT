from __future__ import annotations

from gridiron_gpt.football_state.models.opportunity_change import OpportunityDirection
from gridiron_gpt.football_state.models.opportunity_reconciliation import (
    OpportunityConfirmation,
    OpportunityReconciliationResult,
)
from gridiron_gpt.football_state.models.usage_trend import UsageTrendDirection, UsageTrendResult
from gridiron_gpt.football_state.models.opportunity_change import OpportunityChange


class OpportunityReconciliationService:
    """Compare roster-derived opportunity predictions with observed player usage."""

    def reconcile(
        self,
        predicted: OpportunityChange,
        observed: UsageTrendResult,
    ) -> OpportunityReconciliationResult:
        if predicted.affected_player_id != observed.player_id:
            raise ValueError("predicted and observed player identities must match")

        expected_rising = predicted.direction == OpportunityDirection.INCREASED
        trend = observed.direction

        if trend in {UsageTrendDirection.UNKNOWN, UsageTrendDirection.MIXED}:
            confirmation = OpportunityConfirmation.INCONCLUSIVE
        elif trend == UsageTrendDirection.STABLE:
            confirmation = OpportunityConfirmation.INCONCLUSIVE
        elif expected_rising and trend == UsageTrendDirection.RISING:
            confirmation = OpportunityConfirmation.CONFIRMED
        elif not expected_rising and trend == UsageTrendDirection.FALLING:
            confirmation = OpportunityConfirmation.CONFIRMED
        else:
            confirmation = OpportunityConfirmation.CONTRADICTED

        confidence = self._confidence(predicted, observed, confirmation)
        return OpportunityReconciliationResult(
            player_id=observed.player_id,
            player_name=observed.player_name,
            confirmation=confirmation,
            predicted=predicted,
            observed=observed,
            confidence=confidence,
            reason=self._reason(predicted, observed, confirmation),
        )

    @staticmethod
    def _confidence(
        predicted: OpportunityChange,
        observed: UsageTrendResult,
        confirmation: OpportunityConfirmation,
    ) -> float:
        history_factor = min(1.0, observed.prior_games / 3.0)
        magnitude_factor = min(1.0, max(0.0, predicted.magnitude))
        base = 0.45 + (0.30 * history_factor) + (0.20 * magnitude_factor)
        if confirmation == OpportunityConfirmation.INCONCLUSIVE:
            base -= 0.15
        return round(max(0.0, min(0.95, base)), 4)

    @staticmethod
    def _reason(
        predicted: OpportunityChange,
        observed: UsageTrendResult,
        confirmation: OpportunityConfirmation,
    ) -> str:
        return (
            f"predicted opportunity {predicted.direction.value}; "
            f"observed usage {observed.direction.value}; "
            f"prediction {confirmation.value}"
        )
