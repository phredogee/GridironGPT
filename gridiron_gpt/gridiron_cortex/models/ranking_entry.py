from dataclasses import dataclass


@dataclass
class RankingEntry:
    rank: int

    player_id: str
    player_name: str

    team: str | None
    position: str | None

    overall_score: float

    confidence: float = 1.0
