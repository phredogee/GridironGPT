from dataclasses import dataclass
from typing import Optional


@dataclass
class Impact:
    """
    A fantasy-relevant impact created from a signal.

    Impacts may be direct or propagated.
    """

    entity_type: str
    entity_name: str

    impact_score: float

    team: Optional[str] = None

    impact_type: str = "direct"

    reason: str = ""
