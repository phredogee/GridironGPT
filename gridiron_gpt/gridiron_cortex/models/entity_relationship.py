from dataclasses import dataclass
from typing import Optional


@dataclass
class EntityRelationship:
    """
    Persistent relationship between two football entities.

    Examples:
    - quarterback -> wide receiver
    - wide receiver -> target competitor
    - coach -> player
    - team -> player
    """

    source_entity_id: str
    source_entity_name: str
    source_entity_type: str

    target_entity_id: str
    target_entity_name: str
    target_entity_type: str

    relationship_type: str

    strength: float
    confidence: float

    reason: str = ""

    source_team: Optional[str] = None
    target_team: Optional[str] = None

    first_seen: Optional[str] = None
    last_updated: Optional[str] = None

    active: bool = True
