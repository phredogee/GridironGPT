from dataclasses import dataclass, field
from typing import Any

from gridiron_cortex.evidence.evidence_analyzer import (
    EvidenceAssessment,
)
from gridiron_cortex.models.canonical_event import CanonicalEvent
from gridiron_cortex.models.confidence_result import ConfidenceResult
from gridiron_cortex.models.contradiction_result import (
    ContradictionResult,
)
from gridiron_cortex.models.entity import Entity
from gridiron_cortex.models.impact import Impact
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.models.recommendation import Recommendation
from gridiron_cortex.models.score_update import ScoreUpdate
from gridiron_cortex.models.signal import Signal
from gridiron_cortex.models.trend_result import TrendResult


@dataclass
class EngineContext:
    """
    Carries the working state of one event through the Cortex pipeline.

    Each processing stage can read existing results and add its own
    output without continually expanding method signatures.
    """

    raw_event: RawEvent

    canonical_event: CanonicalEvent | None = None
    confidence_result: ConfidenceResult | None = None
    evidence_assessment: EvidenceAssessment | None = None

    contradiction: ContradictionResult | None = None
    trend: TrendResult | None = None

    history: list["HistoricalSnapshot"] = field(default_factory=list)

    entities: list[Entity] = field(default_factory=list)
    football_context: dict[str, Any] = field(default_factory=dict)
    signals: list[Signal] = field(default_factory=list)
    impacts: list[Impact] = field(default_factory=list)
    score_updates: list[ScoreUpdate] = field(default_factory=list)

    recommendation: Recommendation | None = None
