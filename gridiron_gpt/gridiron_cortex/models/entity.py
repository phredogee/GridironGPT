from dataclasses import dataclass
from typing import Optional


@dataclass
class Entity:
    """
    A resolved canonical football entity.

    This is the authoritative metadata produced by the
    Entity Resolver and passed through Cortex.
    """

    entity_type: str

    name: str

    player_id: Optional[str] = None

    team: Optional[str] = None

    position: Optional[str] = None

    confidence: float = 1.0

    source: str = "unknown"
