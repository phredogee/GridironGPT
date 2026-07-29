from dataclasses import dataclass
from typing import Optional


@dataclass
class PlayerScorecard:
    """
    Persistent intelligence profile for a player.

    This represents Cortex's current view of a player's fantasy value.
    """

    player_id: str
    player_name: str
    team: Optional[str] = None
    position: Optional[str] = None

    overall_score: float = 50.0
    opportunity_score: float = 50.0
    health_score: float = 50.0
    hype_score: float = 50.0
    risk_score: float = 50.0
    momentum_score: float = 50.0

    last_updated: Optional[str] = None
