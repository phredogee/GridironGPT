from gridiron_cortex.models.recommendation import Recommendation


class RecommendationEngine:
    """
    Converts score updates into fantasy recommendations.
    """

    def generate(self, score_updates):
        recommendations = []

        for update in score_updates:
            score_delta = update.score_delta

            if score_delta >= 1.0:
                action = "BUY"
                confidence = 75
            elif score_delta > 0:
                action = "WATCH"
                confidence = 60
            elif score_delta <= -1.0:
                action = "SELL"
                confidence = 75
            elif score_delta < 0:
                action = "MONITOR"
                confidence = 60
            else:
                action = "HOLD"
                confidence = 50

            recommendations.append(
                Recommendation(
                    entity_type=update.entity_type,
                    entity_name=update.entity_name,
                    team=update.team,
                    action=action,
                    confidence=confidence,
                    score_delta=score_delta,
                    reasons=[update.reason] if update.reason else [],
                    recommendation_type="redraft",
                    timeframe="current",
                )
            )

        return recommendations
