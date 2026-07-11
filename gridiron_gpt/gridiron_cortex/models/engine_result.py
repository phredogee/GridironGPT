from dataclasses import dataclass, field
from typing import List
from typing import Dict

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.models.entity import Entity
from gridiron_cortex.models.signal import Signal
from gridiron_cortex.models.impact import Impact
from gridiron_cortex.models.score_update import ScoreUpdate
from gridiron_cortex.models.recommendation import Recommendation
from gridiron_cortex.models.player_scorecard import PlayerScorecard


@dataclass
class EngineResult:
    """
    Final output of the Cortex engine pipeline.
    """

    event: RawEvent

    entities: List[Entity] = field(default_factory=list)

    signal: Signal | None = None

    impacts: List[Impact] = field(default_factory=list)

    score_updates: List[ScoreUpdate] = field(default_factory=list)

    player_scorecards: List[PlayerScorecard] = field(default_factory=list)

    scorecard_history: Dict[str, List[PlayerScorecard]] = field(
        default_factory=dict
    )

    recommendations: List[Recommendation] = field(default_factory=list)

    explanation: str = ""
