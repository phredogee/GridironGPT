from dataclasses import dataclass
from gridiron_cortex.models.prediction import Prediction

@dataclass(slots=True)
class PlayerSnapshot:
    # Identity
    player_id: str
    name: str

    # NFL metadata
    team: str
    position: str
    bye_week: int | None = None

    # Engine scores
    overall_score: float = 50.0
    opportunity_score: float = 50.0
    health_score: float = 50.0
    momentum_score: float = 50.0
    risk_score: float = 50.0

    # Recommendation
    recommendation: str = "WATCH"
    confidence: float = 50.0

    # Runtime intelligence
    prediction: Prediction | None = None

    active_signal_count: int = 0
    strongest_signal: str | None = None
    latest_event: str | None = None

    # Status
    injury_status: str | None = None
    trend: str | None = None

    # Audit
    last_updated: str | None = None
