from dataclasses import dataclass, field


@dataclass(frozen=True)
class Prediction:
    """A forecast produced by the Cortex Predict faculty."""

    entity_id: str
    entity_name: str
    horizon_days: int
    projected_trend: str
    current_score: float
    projected_score: float
    score_delta: float
    confidence: float
    reasons: list[str] = field(default_factory=list)
