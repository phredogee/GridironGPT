from dataclasses import dataclass, field
from typing import Any


@dataclass
class EventClassification:
    category: str
    subtype: str
    polarity: str

    impact: float

    confidence: float

    matched_rules: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
