from dataclasses import dataclass, field
from datetime import datetime

from gridiron_cortex.rankings.ranking_service import RankingEntry


@dataclass
class LeagueSnapshot:
    generated_at: datetime

    overall: list[RankingEntry] = field(default_factory=list)
    quarterbacks: list[RankingEntry] = field(default_factory=list)
    running_backs: list[RankingEntry] = field(default_factory=list)
    wide_receivers: list[RankingEntry] = field(default_factory=list)
    tight_ends: list[RankingEntry] = field(default_factory=list)
