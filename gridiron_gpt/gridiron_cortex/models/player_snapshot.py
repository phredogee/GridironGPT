from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlayerSnapshot:
    """Generic player presentation model."""

    name: str
    team: str
    score: float
    confidence: float
    recommendation: str

    position: str | None = None
    bye_week: int | None = None
    trend: str | None = None
    injury_status: str | None = None
    subtitle: str | None = None
