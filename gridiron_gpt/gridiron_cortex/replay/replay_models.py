from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping

from gridiron_cortex.events.event_types import CortexEventType


class ReplayStage(StrEnum):
    INGESTED = "ingested"
    RESOLVED = "resolved"
    UNDERSTOOD = "understood"
    PROPAGATED = "propagated"
    SCORED = "scored"
    RECOMMENDED = "recommended"
    CONFIDENCE = "confidence"


@dataclass(frozen=True, slots=True)
class ReplayStep:
    event_id: str
    timestamp: datetime
    stage: ReplayStage
    event_type: CortexEventType
    title: str
    summary: str
    entity_id: str | None = None
    entity_name: str | None = None
    source: str | None = None
    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "details", MappingProxyType(dict(self.details)))


@dataclass(frozen=True, slots=True)
class ReplayDecision:
    decision_id: str
    correlation_id: str
    headline: str
    started_at: datetime
    completed_at: datetime
    steps: tuple[ReplayStep, ...]
    entity_name: str | None = None
    source: str | None = None
    recommendation: str | None = None
    confidence: float | None = None

    @property
    def stage_count(self) -> int:
        return len({step.stage for step in self.steps})

    @property
    def is_complete(self) -> bool:
        stages = {step.stage for step in self.steps}
        required = {
            ReplayStage.INGESTED,
            ReplayStage.RESOLVED,
            ReplayStage.UNDERSTOOD,
            ReplayStage.SCORED,
            ReplayStage.RECOMMENDED,
        }
        return required.issubset(stages)
