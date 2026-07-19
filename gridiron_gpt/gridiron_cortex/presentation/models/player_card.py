from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlayerCardModel:
    """Generic presentation model for a fantasy football player."""

    name: str
    team: str

    recommendation: str
    confidence: float
    score: float

    position: str | None = None
    bye_week: int | None = None

    trend: str | None = None
    injury_status: str | None = None
    subtitle: str | None = None
