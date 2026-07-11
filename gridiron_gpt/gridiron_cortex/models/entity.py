from dataclasses import dataclass
from typing import Optional


@dataclass
class Entity:
    """
    A resolved fantasy football entity.

    Examples:
        Player
        Team
        Coach
        Draft Pick (future)
    """

    entity_type: str
    name: str

    team: Optional[str] = None

    confidence: float = 1.0

    source: str = "unknown"
