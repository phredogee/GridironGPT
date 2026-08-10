from dataclasses import dataclass


@dataclass
class TrendResult:
    direction: str = "stable"

    strength: float = 0.0

    confidence_delta: float = 0.0

    observations: int = 0

    explanation: str = ""
