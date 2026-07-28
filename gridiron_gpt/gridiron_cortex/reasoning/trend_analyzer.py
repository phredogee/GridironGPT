from gridiron_cortex.models.engine_context import EngineContext
from gridiron_cortex.models.trend_result import TrendResult


class TrendAnalyzer:
    """Analyze score movement across historical snapshots."""

    STABLE_THRESHOLD = 0.5
    MAX_STRENGTH_DELTA = 10.0
    MAX_CONFIDENCE_DELTA = 10.0

    def evaluate(
        self,
        context: EngineContext,
    ) -> TrendResult:
        history = sorted(
            context.history,
            key=lambda snapshot: snapshot.timestamp,
        )

        observations = len(history)

        if observations < 2:
            return TrendResult(
                observations=observations,
                explanation=(
                    "Insufficient history to determine a trend."
                    if observations == 1
                    else ""
                ),
            )

        starting_score = history[0].overall_score
        ending_score = history[-1].overall_score
        score_change = ending_score - starting_score

        direction = self._direction(score_change)
        strength = self._strength(score_change)
        confidence_delta = self._confidence_delta(
            direction=direction,
            strength=strength,
        )

        return TrendResult(
            direction=direction,
            strength=round(strength, 2),
            confidence_delta=round(confidence_delta, 2),
            observations=observations,
            explanation=self._explanation(
                direction=direction,
                score_change=score_change,
                observations=observations,
            ),
        )

    def _direction(
        self,
        score_change: float,
    ) -> str:
        if score_change >= self.STABLE_THRESHOLD:
            return "rising"

        if score_change <= -self.STABLE_THRESHOLD:
            return "falling"

        return "stable"

    def _strength(
        self,
        score_change: float,
    ) -> float:
        return min(
            abs(score_change) / self.MAX_STRENGTH_DELTA,
            1.0,
        )

    def _confidence_delta(
        self,
        *,
        direction: str,
        strength: float,
    ) -> float:
        adjustment = strength * self.MAX_CONFIDENCE_DELTA

        if direction == "rising":
            return adjustment

        if direction == "falling":
            return -adjustment

        return 0.0

    @staticmethod
    def _explanation(
        *,
        direction: str,
        score_change: float,
        observations: int,
    ) -> str:
        if direction == "rising":
            return (
                f"Overall score increased by {score_change:.2f} "
                f"across {observations} observations."
            )

        if direction == "falling":
            return (
                f"Overall score decreased by "
                f"{abs(score_change):.2f} across "
                f"{observations} observations."
            )

        return (
            f"Overall score remained stable across "
            f"{observations} observations."
        )
