from gridiron_cortex.models.prediction import Prediction
from gridiron_cortex.models.recommendation import Recommendation


class RecommendationEngine:
    """Convert evaluated score changes and forecasts into recommendations."""

    def generate(
        self,
        score_updates,
        predictions: list[Prediction] | None = None,
    ):
        predictions_by_name = {
            prediction.entity_name.strip().casefold(): prediction
            for prediction in predictions or []
        }

        recommendations = []

        for update in score_updates:
            action, confidence = self._base_recommendation(
                update.score_delta
            )

            reasons = [update.reason] if update.reason else []

            prediction = predictions_by_name.get(
                update.entity_name.strip().casefold()
            )

            if prediction is not None:
                action, confidence = self._apply_prediction(
                    action=action,
                    confidence=confidence,
                    score_delta=update.score_delta,
                    prediction=prediction,
                )

                reasons.extend(
                    self._prediction_reasons(prediction)
                )

            recommendations.append(
                Recommendation(
                    entity_type=update.entity_type,
                    entity_name=update.entity_name,
                    team=update.team,
                    action=action,
                    confidence=round(confidence, 2),
                    score_delta=update.score_delta,
                    reasons=self._deduplicate(reasons),
                    recommendation_type="redraft",
                    timeframe="current",
                )
            )

        return recommendations

    @staticmethod
    def _base_recommendation(
        score_delta: float,
    ) -> tuple[str, float]:
        if score_delta >= 1.0:
            return "BUY", 75.0

        if score_delta > 0:
            return "WATCH", 60.0

        if score_delta <= -1.0:
            return "SELL", 75.0

        if score_delta < 0:
            return "MONITOR", 60.0

        return "HOLD", 50.0

    def _apply_prediction(
        self,
        *,
        action: str,
        confidence: float,
        score_delta: float,
        prediction: Prediction,
    ) -> tuple[str, float]:
        """Adjust a recommendation using forecast direction.

        The first implementation is intentionally conservative:

        - Supporting forecasts increase confidence.
        - Conflicting forecasts decrease confidence.
        - Neutral evaluations may move from HOLD to WATCH or MONITOR.
        - Strong current BUY or SELL actions are not reversed solely by a
          heuristic forecast.
        """

        prediction_weight = self._prediction_weight(
            prediction.confidence
        )

        trend = prediction.projected_trend.upper()

        if trend == "RISING":
            if score_delta > 0:
                confidence += prediction_weight
            elif score_delta < 0:
                confidence -= prediction_weight
            elif action == "HOLD":
                action = "WATCH"
                confidence += prediction_weight / 2

        elif trend == "FALLING":
            if score_delta < 0:
                confidence += prediction_weight
            elif score_delta > 0:
                confidence -= prediction_weight
            elif action == "HOLD":
                action = "MONITOR"
                confidence += prediction_weight / 2

        elif trend == "STABLE":
            confidence += 2.0 if action == "HOLD" else 0.0

        confidence = max(40.0, min(confidence, 95.0))

        return action, confidence

    @staticmethod
    def _prediction_weight(
        prediction_confidence: float,
    ) -> float:
        """Convert Predict's 0-1 confidence into a modest 0-10 adjustment."""

        bounded_confidence = max(
            0.0,
            min(prediction_confidence, 1.0),
        )

        return bounded_confidence * 10.0

    @staticmethod
    def _prediction_reasons(
        prediction: Prediction,
    ) -> list[str]:
        reasons = [
            (
                f"{prediction.horizon_days}-day forecast: "
                f"{prediction.projected_trend.lower()}"
            ),
            (
                "Projected score change: "
                f"{prediction.score_delta:+.2f}"
            ),
        ]

        reasons.extend(prediction.reasons)

        return reasons

    @staticmethod
    def _deduplicate(reasons: list[str]) -> list[str]:
        return list(dict.fromkeys(reason for reason in reasons if reason))
