from dataclasses import dataclass, field

from gridiron_cortex.models.impact import Impact
from gridiron_cortex.models.player_scorecard import PlayerScorecard
from gridiron_cortex.models.prediction import Prediction
from gridiron_cortex.models.recommendation import Recommendation
from gridiron_cortex.models.signal import Signal


@dataclass(slots=True)
class PlayerIntelligence:
    """
    Runtime intelligence assembled for one player.

    This model combines persistent scoring data with predictions,
    recommendations, signals, impacts, and explanation data.
    """

    scorecard: PlayerScorecard

    prediction: Prediction | None = None
    recommendation: Recommendation | None = None

    signals: list[Signal] = field(default_factory=list)
    impacts: list[Impact] = field(default_factory=list)

    explanation: str = ""
