from gridiron_cortex.models.impact import Impact
from gridiron_cortex.models.player_intelligence import PlayerIntelligence
from gridiron_cortex.models.player_scorecard import PlayerScorecard
from gridiron_cortex.models.prediction import Prediction
from gridiron_cortex.models.recommendation import Recommendation
from gridiron_cortex.models.signal import Signal


class PlayerIntelligenceBuilder:

    @staticmethod
    def build(
        *,
        scorecard: PlayerScorecard,
        prediction: Prediction | None = None,
        recommendation: Recommendation | None = None,
        signals: list[Signal] | None = None,
        impacts: list[Impact] | None = None,
        explanation: str = "",
    ) -> PlayerIntelligence:

        return PlayerIntelligence(
            scorecard=scorecard,
            prediction=prediction,
            recommendation=recommendation,
            signals=signals or [],
            impacts=impacts or [],
            explanation=explanation,
        )
