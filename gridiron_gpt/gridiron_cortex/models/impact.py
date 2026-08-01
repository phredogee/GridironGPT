from dataclasses import dataclass
from typing import Optional


@dataclass
class Impact:
    """
    A fantasy-relevant impact created from a signal.

    Impacts may be direct or propagated. Propagated impacts retain
    relationship metadata so Cortex can explain how an effect traveled
    through the knowledge graph.
    """

    entity_type: str
    entity_name: str

    impact_score: float

    team: Optional[str] = None

    impact_type: str = "direct"

    reason: str = ""

    # Propagation metadata
    hop_count: Optional[int] = None
    relationship_strength: Optional[float] = None
    relationship_confidence: Optional[float] = None
    propagation_weight: Optional[float] = None
