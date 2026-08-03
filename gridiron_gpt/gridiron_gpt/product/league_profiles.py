from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from gridiron_gpt.fantasy_decisions.models import LeagueContext, ScoringFormat


@dataclass(frozen=True)
class LeagueProfile:
    league_id: str
    name: str
    teams: int = 12
    roster_size: int = 16
    starting_slots: dict[str, int] = field(
        default_factory=lambda: {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1}
    )
    bench_slots: int = 6
    ir_slots: int = 1
    faab_budget: int = 100
    scoring_format: ScoringFormat = ScoringFormat.HALF_PPR

    def __post_init__(self) -> None:
        if not self.league_id.strip() or not self.name.strip():
            raise ValueError("league identity is required")
        if self.teams <= 1:
            raise ValueError("teams must be greater than one")
        if self.roster_size <= 0 or self.bench_slots < 0 or self.ir_slots < 0:
            raise ValueError("roster limits are invalid")
        if self.faab_budget < 0:
            raise ValueError("faab_budget must be non-negative")
        if any(count < 0 for count in self.starting_slots.values()):
            raise ValueError("starting slot counts must be non-negative")

    def to_context(self) -> LeagueContext:
        return LeagueContext(
            scoring_format=self.scoring_format,
            teams=self.teams,
            roster_size=self.roster_size,
            starting_slots=dict(self.starting_slots),
            faab_budget=self.faab_budget,
        )

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["scoring_format"] = self.scoring_format.value
        return payload

    @classmethod
    def from_dict(cls, payload: dict) -> "LeagueProfile":
        values = dict(payload)
        values["scoring_format"] = ScoringFormat(values.get("scoring_format", "half_ppr"))
        return cls(**values)


class JsonLeagueProfileRepository:
    def __init__(self, directory: str | Path):
        self.directory = Path(directory)

    def save(self, profile: LeagueProfile) -> Path:
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self.directory / f"{profile.league_id}.json"
        path.write_text(json.dumps(profile.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def load(self, league_id: str) -> LeagueProfile:
        path = self.directory / f"{league_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"league profile not found: {league_id}")
        return LeagueProfile.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def list(self) -> list[LeagueProfile]:
        if not self.directory.exists():
            return []
        return [
            LeagueProfile.from_dict(json.loads(path.read_text(encoding="utf-8")))
            for path in sorted(self.directory.glob("*.json"))
        ]

    def delete(self, league_id: str) -> bool:
        path = self.directory / f"{league_id}.json"
        if not path.exists():
            return False
        path.unlink()
        return True
