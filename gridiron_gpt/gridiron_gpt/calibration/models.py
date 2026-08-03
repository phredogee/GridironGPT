from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class OutcomeDirection(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


@dataclass(frozen=True)
class PredictionRecord:
    prediction_id: str
    player_id: str
    player_name: str
    predicted_at: datetime
    horizon: str
    direction: OutcomeDirection
    confidence: float
    signal_type: str
    sources: tuple[str, ...] = ()
    relationship_types: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.prediction_id.strip():
            raise ValueError("prediction_id is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.predicted_at.tzinfo is None:
            raise ValueError("predicted_at must be timezone-aware")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["predicted_at"] = self.predicted_at.isoformat()
        payload["direction"] = self.direction.value
        payload["sources"] = list(self.sources)
        payload["relationship_types"] = list(self.relationship_types)
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PredictionRecord":
        values = dict(payload)
        values["predicted_at"] = datetime.fromisoformat(values["predicted_at"])
        values["direction"] = OutcomeDirection(values["direction"])
        values["sources"] = tuple(values.get("sources", ()))
        values["relationship_types"] = tuple(values.get("relationship_types", ()))
        return cls(**values)


@dataclass(frozen=True)
class OutcomeRecord:
    prediction_id: str
    observed_at: datetime
    direction: OutcomeDirection
    value: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["observed_at"] = self.observed_at.isoformat()
        payload["direction"] = self.direction.value
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "OutcomeRecord":
        values = dict(payload)
        values["observed_at"] = datetime.fromisoformat(values["observed_at"])
        values["direction"] = OutcomeDirection(values["direction"])
        return cls(**values)


@dataclass(frozen=True)
class EvaluationRecord:
    prediction: PredictionRecord
    outcome: OutcomeRecord
    correct: bool
    brier_score: float


@dataclass(frozen=True)
class CalibrationBin:
    lower: float
    upper: float
    count: int
    mean_confidence: float
    accuracy: float
    calibration_error: float


@dataclass(frozen=True)
class QualityReport:
    count: int
    accuracy: float
    mean_brier_score: float
    bins: tuple[CalibrationBin, ...]
    by_signal_type: dict[str, dict[str, float]]
    by_source: dict[str, dict[str, float]]
    by_relationship_type: dict[str, dict[str, float]]
