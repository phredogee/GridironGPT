from dataclasses import dataclass
from typing import Optional


@dataclass
class ScoreUpdate:
    """
    Record of a score change caused by an impact.

    PlayerScorecard = current state.
    ScoreUpdate = change record.
    """

    entity_type: str
    entity_name: str

    score_delta: float

    team: Optional[str] = None

    previous_score: Optional[float] = None
    new_score: Optional[float] = None

    score_category: str = "overall"

    reason: str = ""
