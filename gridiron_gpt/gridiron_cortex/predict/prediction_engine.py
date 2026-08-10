from gridiron_cortex.models.player_scorecard import PlayerScorecard
from gridiron_cortex.models.prediction import Prediction


class PredictionEngine:
    """Generate short-term forecasts from persistent scorecard intelligence."""

    def __init__(self, horizon_days: int = 14) -> None:
        if horizon_days <= 0:
            raise ValueError("horizon_days must be greater than zero")

        self.horizon_days = horizon_days

    def predict(self, scorecard: PlayerScorecard) -> Prediction:
        """Forecast the entity's short-term score direction.

        This initial implementation is deterministic and rule-based. It uses
        the scorecard's opportunity, health, hype, risk, and momentum values.
        """

        directional_signal = (
            self._center(scorecard.momentum_score) * 0.35
            + self._center(scorecard.opportunity_score) * 0.30
            + self._center(scorecard.health_score) * 0.20
            + self._center(scorecard.hype_score) * 0.10
            - self._center(scorecard.risk_score) * 0.25
        )

        score_delta = self._clamp(
            directional_signal / 5.0,
            minimum=-10.0,
            maximum=10.0,
        )

        projected_score = self._clamp(
            scorecard.overall_score + score_delta,
            minimum=0.0,
            maximum=100.0,
        )

        projected_trend = self._classify_trend(score_delta)
        confidence = self._calculate_confidence(score_delta)
        reasons = self._build_reasons(scorecard, projected_trend)

        return Prediction(
            entity_id=scorecard.player_id,
            entity_name=scorecard.player_name,
            horizon_days=self.horizon_days,
            projected_trend=projected_trend,
            current_score=round(scorecard.overall_score, 2),
            projected_score=round(projected_score, 2),
            score_delta=round(score_delta, 2),
            confidence=round(confidence, 2),
            reasons=reasons,
        )

    @staticmethod
    def _center(score: float) -> float:
        """Convert a 0-100 score into a value centered around zero."""

        return score - 50.0

    @staticmethod
    def _clamp(value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(value, maximum))

    @staticmethod
    def _classify_trend(score_delta: float) -> str:
        if score_delta >= 1.5:
            return "RISING"

        if score_delta <= -1.5:
            return "FALLING"

        return "STABLE"

    @staticmethod
    def _calculate_confidence(score_delta: float) -> float:
        """Return confidence between 0.55 and 0.90.

        Larger directional movements produce higher confidence. This is not
        yet a statistically calibrated probability.
        """

        return min(0.90, 0.55 + abs(score_delta) * 0.035)

    @staticmethod
    def _build_reasons(
        scorecard: PlayerScorecard,
        projected_trend: str,
    ) -> list[str]:
        reasons: list[str] = []

        if scorecard.momentum_score >= 60:
            reasons.append("Positive recent momentum")
        elif scorecard.momentum_score <= 40:
            reasons.append("Negative recent momentum")

        if scorecard.opportunity_score >= 60:
            reasons.append("Strong projected opportunity")
        elif scorecard.opportunity_score <= 40:
            reasons.append("Limited projected opportunity")

        if scorecard.health_score <= 40:
            reasons.append("Health outlook creates downside risk")
        elif scorecard.health_score >= 60:
            reasons.append("Health outlook supports availability")

        if scorecard.risk_score >= 60:
            reasons.append("Elevated risk limits the forecast")
        elif scorecard.risk_score <= 40:
            reasons.append("Low current risk supports the forecast")

        if not reasons:
            reasons.append(
                f"Scorecard indicators support a {projected_trend.lower()} outlook"
            )

        return reasons
