from dataclasses import dataclass, field
from typing import Any, List

from gridiron_cortex.models.entity import Entity


@dataclass
class Signal:
    """
    A fantasy-relevant interpretation of an event.
    """

    headline: str

    entities: List[Entity] = field(default_factory=list)

    sentiment: str = "neutral"

    impact_score: float = 0.0

    positive_hits: List[str] = field(default_factory=list)

    negative_hits: List[str] = field(default_factory=list)

    confidence: float = 1.0

    signal_type: str = "news"

    evidence: dict[str, Any] = field(default_factory=dict)
