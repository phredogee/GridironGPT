from dataclasses import dataclass

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.understand.event_classifier import EventClassification


@dataclass(slots=True)
class Evidence:
    raw_event: RawEvent
    classification: EventClassification
    source: str
    confidence: float
