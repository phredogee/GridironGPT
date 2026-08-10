from dataclasses import dataclass, field
from typing import Any, List

from gridiron_cortex.models.entity import Entity


@dataclass
class Signal:
    """
    A fantasy-relevant interpretation of an event.
    """

    headline: str

    entities: List[Entity] = field(default_factory=list)

    sentiment: str = "neutral"

    impact_score: float = 0.0

    positive_hits: List[str] = field(default_factory=list)

    negative_hits: List[str] = field(default_factory=list)

    confidence: float = 1.0

    signal_type: str = "news"

    signal_category: str = "general"

    source_count: int = 1

    sources: list[str] | None = None

    corroboration_confidence: float | None = None

    evidence: dict[str, Any] = field(default_factory=dict)

def make_signal(
    impact_score: float,
    player_name: str = "CJ Stroud",
) -> Signal:
    return Signal(
        headline=f"Test signal for {player_name}",
        sentiment="positive" if impact_score > 0 else "negative",
        impact_score=impact_score,
        entities=[
            Entity(
                entity_type="player",
                name=player_name,
                team="HOU",
            )
        ],
    )
