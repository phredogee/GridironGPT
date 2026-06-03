# gridiron_gpt/draft/config.py

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class LeagueConfig:
    teams: int = 12
    rounds: int = 15
    scoring: str = "ppr"  # ppr | half_ppr | standard

    # Starting lineup slots
    lineup: Dict[str, int] = field(default_factory=lambda: {
        "QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1, "K": 1, "DEF": 1
    })

    # Full roster size by position
    roster: Dict[str, int] = field(default_factory=lambda: {
        "QB": 2, "RB": 6, "WR": 6, "TE": 2, "K": 1, "DEF": 1
    })

    @property
    def total_roster_spots(self) -> int:
        return sum(self.roster.values())

    @property
    def starting_spots(self) -> int:
        return sum(self.lineup.values())

    @property
    def bench_spots(self) -> int:
        return self.total_roster_spots - self.starting_spots
