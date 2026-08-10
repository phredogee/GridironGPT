from dataclasses import dataclass


@dataclass
class HistoricalSnapshot:
    timestamp: str

    overall_score: float

    confidence: float

    event_type: str = ""

    summary: str = ""
