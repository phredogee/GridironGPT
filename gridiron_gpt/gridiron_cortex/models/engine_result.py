from dataclasses import dataclass, field
from typing import Dict, List

from gridiron_cortex.evidence.evidence_analyzer import (
    EvidenceAssessment,
)
from gridiron_cortex.models.confidence_result import ConfidenceResult
from gridiron_cortex.models.entity import Entity
from gridiron_cortex.models.evidence_chain import EvidenceChain
from gridiron_cortex.models.evidence_graph import EvidenceGraph
from gridiron_cortex.models.impact import Impact
from gridiron_cortex.models.intelligence_context import (
    IntelligenceContext,
)
from gridiron_cortex.models.player_scorecard import PlayerScorecard
from gridiron_cortex.models.player_snapshot import PlayerSnapshot
from gridiron_cortex.models.prediction import Prediction
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.models.canonical_event import CanonicalEvent
from gridiron_cortex.models.recommendation import Recommendation
from gridiron_cortex.models.score_update import ScoreUpdate
from gridiron_cortex.models.signal import Signal


@dataclass
class EngineResult:
    """Final output of the Cortex Engine pipeline."""

    event: RawEvent

    entities: List[Entity] = field(default_factory=list)

    signal: Signal | None = None

    canonical_event: CanonicalEvent | None = None

    evidence_assessment: EvidenceAssessment | None = None

    confidence_result: ConfidenceResult | None = None

    impacts: List[Impact] = field(default_factory=list)

    score_updates: List[ScoreUpdate] = field(default_factory=list)

    player_scorecards: List[PlayerScorecard] = field(default_factory=list)

    player_snapshots: List[PlayerSnapshot] = field(default_factory=list)

    scorecard_history: Dict[str, List[PlayerScorecard]] = field(
        default_factory=dict
    )

    predictions: List[Prediction] = field(default_factory=list)

    intelligence: IntelligenceContext | None = None

    recommendations: List[Recommendation] = field(default_factory=list)

    evidence_chains: List[EvidenceChain] = field(default_factory=list)

    evidence_graphs: List[EvidenceGraph] = field(default_factory=list)

    explanation: str = ""
