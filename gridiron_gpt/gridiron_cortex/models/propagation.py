from dataclasses import dataclass


@dataclass
class PropagationCandidate:
    entity_id: str
    entity_name: str
    entity_type: str
    team: str | None

    hop_count: int

    relationship_strength: float
    relationship_confidence: float

    propagation_weight: float

    reason: str
