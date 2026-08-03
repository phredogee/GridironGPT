from __future__ import annotations

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_gpt.football_state.models.opportunity_reconciliation import (
    OpportunityConfirmation,
    OpportunityReconciliationResult,
)
from gridiron_gpt.football_state.models.usage_trend import (
    UsageTrendDirection,
    UsageTrendResult,
)


class UsageEventFactory:
    """Convert observed usage intelligence into normal Cortex evidence."""

    SOURCE = "canonical usage state"

    def build_trend_event(self, trend: UsageTrendResult) -> RawEvent:
        sentiment, impact = self._trend_intelligence(trend.direction)
        current = trend.current

        return RawEvent(
            source=self.SOURCE,
            headline=f"{trend.player_name} usage trend is {trend.direction.value}: {trend.reason}",
            player=trend.player_name,
            player_id=trend.player_id,
            team=current.team,
            published_at=current.observed_at.isoformat(),
            event_type="usage_trend",
            sentiment=sentiment,
            impact_score=impact,
            confidence=self._trend_confidence(trend),
            evidence={
                "source_id": self._trend_source_id(trend),
                "usage_trend": {
                    "direction": trend.direction.value,
                    "prior_games": trend.prior_games,
                    "reason": trend.reason,
                    "deltas": {
                        name: {
                            "baseline": delta.baseline,
                            "current": delta.current,
                            "delta": delta.delta,
                        }
                        for name, delta in trend.deltas.items()
                    },
                },
            },
        )

    def build_reconciliation_event(self, result: OpportunityReconciliationResult) -> RawEvent:
        sentiment, impact = self._reconciliation_intelligence(result)
        current = result.observed.current

        return RawEvent(
            source=self.SOURCE,
            headline=(
                f"{result.player_name} roster opportunity prediction is "
                f"{result.confirmation.value}: {result.reason}"
            ),
            player=result.player_name,
            player_id=result.player_id,
            team=current.team,
            published_at=current.observed_at.isoformat(),
            event_type="opportunity_confirmation",
            sentiment=sentiment,
            impact_score=impact,
            confidence=result.confidence,
            evidence={
                "source_id": self._reconciliation_source_id(result),
                "opportunity_confirmation": {
                    "confirmation": result.confirmation.value,
                    "predicted_direction": result.predicted.direction.value,
                    "observed_direction": result.observed.direction.value,
                    "source_player_id": result.predicted.source_player_id,
                    "source_player_name": result.predicted.source_player_name,
                    "relationship_type": result.predicted.relationship_type,
                    "reason": result.reason,
                },
            },
        )

    @staticmethod
    def _trend_intelligence(direction: UsageTrendDirection) -> tuple[str, float]:
        if direction == UsageTrendDirection.RISING:
            return "positive", 0.55
        if direction == UsageTrendDirection.FALLING:
            return "negative", -0.55
        return "neutral", 0.0

    @staticmethod
    def _trend_confidence(trend: UsageTrendResult) -> float:
        return round(min(0.95, 0.55 + (0.12 * min(3, trend.prior_games))), 4)

    @staticmethod
    def _reconciliation_intelligence(result: OpportunityReconciliationResult) -> tuple[str, float]:
        if result.confirmation == OpportunityConfirmation.INCONCLUSIVE:
            return "neutral", 0.0

        magnitude = min(0.7, 0.25 + (0.45 * result.confidence))
        predicted_increase = result.predicted.direction.value == "increased"
        confirmed = result.confirmation == OpportunityConfirmation.CONFIRMED
        positive = predicted_increase == confirmed
        return ("positive", magnitude) if positive else ("negative", -magnitude)

    @staticmethod
    def _trend_source_id(trend: UsageTrendResult) -> str:
        current = trend.current
        return ":".join([
            "usage_trend",
            trend.player_id,
            str(current.season),
            str(current.week),
            trend.direction.value,
        ])

    @staticmethod
    def _reconciliation_source_id(result: OpportunityReconciliationResult) -> str:
        current = result.observed.current
        return ":".join([
            "opportunity_confirmation",
            result.predicted.source_player_id,
            result.player_id,
            str(current.season),
            str(current.week),
            result.confirmation.value,
        ])
