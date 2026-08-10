from gridiron_cortex.models.player_scorecard import PlayerScorecard
from gridiron_cortex.models.player_snapshot import PlayerSnapshot
from gridiron_cortex.models.prediction import Prediction
from gridiron_cortex.models.player_intelligence import (
    PlayerIntelligence,
)

class PlayerSnapshotFactory:

    @staticmethod
    def from_scorecard(
        scorecard: PlayerScorecard,
        *,
        prediction: Prediction | None = None,
        position: str | None = None,
        bye_week: int | None = None,
        recommendation: str = "WATCH",
        confidence: float = 50.0,
        injury_status: str | None = None,
        trend: str | None = None,
    ) -> PlayerSnapshot:
        return PlayerSnapshot(
            player_id=scorecard.player_id,
            name=scorecard.player_name,
            team=scorecard.team or "",

            position=position,
            bye_week=bye_week,

            overall_score=scorecard.overall_score,
            opportunity_score=scorecard.opportunity_score,
            health_score=scorecard.health_score,
            momentum_score=scorecard.momentum_score,
            risk_score=scorecard.risk_score,
            prediction=prediction,

            recommendation=recommendation,
            confidence=confidence,

            injury_status=injury_status,
            trend=trend,

            last_updated=scorecard.last_updated,
        )

    @staticmethod
    def from_intelligence(
        intelligence: PlayerIntelligence,
    ) -> PlayerSnapshot:

        return PlayerSnapshotFactory.from_scorecard(
            intelligence.scorecard,
            prediction=intelligence.prediction,
            recommendation=(
                intelligence.recommendation.action
                if intelligence.recommendation
                else "WATCH"
            ),
            confidence=(
                intelligence.recommendation.confidence
                if intelligence.recommendation
                else 50.0
            ),
        )
