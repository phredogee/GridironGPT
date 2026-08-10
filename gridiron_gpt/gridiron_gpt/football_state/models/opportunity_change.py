from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OpportunityDirection(str, Enum):
    INCREASED = "increased"
    DECREASED = "decreased"


@dataclass(frozen=True)
class OpportunityChange:
    """Derived football consequence for a teammate after roster movement."""

    source_player_id: str
    source_player_name: str
    affected_player_id: str
    affected_player_name: str
    relationship_type: str
    direction: OpportunityDirection
    magnitude: float
    reason: str
