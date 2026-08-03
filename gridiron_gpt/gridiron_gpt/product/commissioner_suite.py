from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from statistics import pstdev
from typing import Any

from gridiron_gpt.product.schedule_generator import GeneratedSchedule, ScheduledMatchup


@dataclass(frozen=True)
class ScheduleAnalytics:
    home_away_spread: int
    longest_home_streak: dict[str, int]
    longest_away_streak: dict[str, int]
    repeat_opponents: dict[str, int]
    divisional_games_by_week: dict[int, int]
    score: float


class ScheduleAnalyticsService:
    def analyze(self, schedule: GeneratedSchedule) -> ScheduleAnalytics:
        team_ids = sorted(schedule.home_games)
        longest_home = {team_id: self._streak(schedule.matchups, team_id, home=True) for team_id in team_ids}
        longest_away = {team_id: self._streak(schedule.matchups, team_id, home=False) for team_id in team_ids}
        repeats = {team_id: self._repeat_count(schedule.matchups, team_id) for team_id in team_ids}
        divisional = {
            week: sum(1 for game in schedule.matchups if game.week == week and game.divisional)
            for week in range(1, schedule.config.regular_season_weeks + 1)
        }
        balances = [schedule.home_games[team_id] - schedule.away_games[team_id] for team_id in team_ids]
        spread = max(balances) - min(balances) if balances else 0
        penalty = spread + sum(max(0, value - 2) for value in longest_home.values())
        penalty += sum(max(0, value - 2) for value in longest_away.values())
        penalty += pstdev(list(divisional.values())) if len(divisional) > 1 else 0.0
        return ScheduleAnalytics(
            home_away_spread=spread,
            longest_home_streak=longest_home,
            longest_away_streak=longest_away,
            repeat_opponents=repeats,
            divisional_games_by_week=divisional,
            score=round(max(0.0, 100.0 - 10.0 * penalty), 2),
        )

    @staticmethod
    def _streak(games: tuple[ScheduledMatchup, ...], team_id: str, *, home: bool) -> int:
        result = 0
        current = 0
        for game in sorted((g for g in games if team_id in {g.home_team_id, g.away_team_id}), key=lambda g: g.week):
            matched = game.home_team_id == team_id if home else game.away_team_id == team_id
            current = current + 1 if matched else 0
            result = max(result, current)
        return result

    @staticmethod
    def _repeat_count(games: tuple[ScheduledMatchup, ...], team_id: str) -> int:
        opponents: dict[str, int] = {}
        for game in games:
            if team_id == game.home_team_id:
                opponent = game.away_team_id
            elif team_id == game.away_team_id:
                opponent = game.home_team_id
            else:
                continue
            opponents[opponent] = opponents.get(opponent, 0) + 1
        return sum(max(0, count - 1) for count in opponents.values())


@dataclass(frozen=True)
class PlayoffMatchup:
    round_number: int
    seed_a: int | None
    seed_b: int | None
    label: str
    bye_seed: int | None = None


@dataclass(frozen=True)
class PlayoffBracket:
    playoff_teams: int
    rounds: int
    matchups: tuple[PlayoffMatchup, ...]


class PlayoffBracketGenerator:
    SUPPORTED = {4: 2, 6: 3, 8: 3}

    def generate(self, playoff_teams: int) -> PlayoffBracket:
        if playoff_teams not in self.SUPPORTED:
            raise ValueError("playoff_teams must be one of 4, 6, or 8")
        if playoff_teams == 4:
            games = (
                PlayoffMatchup(1, 1, 4, "Semifinal 1"),
                PlayoffMatchup(1, 2, 3, "Semifinal 2"),
                PlayoffMatchup(2, None, None, "Championship"),
            )
        elif playoff_teams == 6:
            games = (
                PlayoffMatchup(1, 3, 6, "Wild Card 1", bye_seed=1),
                PlayoffMatchup(1, 4, 5, "Wild Card 2", bye_seed=2),
                PlayoffMatchup(2, None, 1, "Semifinal 1"),
                PlayoffMatchup(2, None, 2, "Semifinal 2"),
                PlayoffMatchup(3, None, None, "Championship"),
            )
        else:
            games = (
                PlayoffMatchup(1, 1, 8, "Quarterfinal 1"),
                PlayoffMatchup(1, 4, 5, "Quarterfinal 2"),
                PlayoffMatchup(1, 2, 7, "Quarterfinal 3"),
                PlayoffMatchup(1, 3, 6, "Quarterfinal 4"),
                PlayoffMatchup(2, None, None, "Semifinal 1"),
                PlayoffMatchup(2, None, None, "Semifinal 2"),
                PlayoffMatchup(3, None, None, "Championship"),
            )
        return PlayoffBracket(playoff_teams, self.SUPPORTED[playoff_teams], games)


@dataclass(frozen=True)
class LeagueSeasonArchive:
    league_id: str
    season: int
    champion: str | None = None
    runner_up: str | None = None
    standings: tuple[dict[str, Any], ...] = ()
    schedule: tuple[dict[str, Any], ...] = ()
    draft: tuple[dict[str, Any], ...] = ()
    transactions: tuple[dict[str, Any], ...] = ()
    awards: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class JsonLeagueHistoryRepository:
    def __init__(self, directory: str | Path):
        self.directory = Path(directory)

    def save(self, archive: LeagueSeasonArchive) -> Path:
        path = self.directory / archive.league_id / f"{archive.season}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(archive.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def load(self, league_id: str, season: int) -> LeagueSeasonArchive:
        path = self.directory / league_id / f"{season}.json"
        if not path.exists():
            raise FileNotFoundError(f"league season not found: {league_id}/{season}")
        return LeagueSeasonArchive(**json.loads(path.read_text(encoding="utf-8")))

    def seasons(self, league_id: str) -> list[int]:
        directory = self.directory / league_id
        if not directory.exists():
            return []
        return sorted(int(path.stem) for path in directory.glob("*.json"))


class CommissionerInsightService:
    def summarize(self, *, standings: list[dict[str, Any]]) -> list[str]:
        if not standings:
            return ["No standings data is available yet."]
        insights: list[str] = []
        by_points = sorted(standings, key=lambda row: float(row.get("points_for", 0)), reverse=True)
        by_wins = sorted(standings, key=lambda row: int(row.get("wins", 0)), reverse=True)
        if by_points:
            insights.append(f"{by_points[0]['team']} leads the league in points scored.")
        if by_wins:
            insights.append(f"{by_wins[0]['team']} currently owns the best record.")
        luck = []
        for row in standings:
            expected = float(row.get("expected_wins", row.get("wins", 0)))
            actual = float(row.get("wins", 0))
            luck.append((actual - expected, row["team"]))
        luck.sort(reverse=True)
        if luck and luck[0][0] > 0:
            insights.append(f"{luck[0][1]} has outperformed expected wins by {luck[0][0]:.1f}.")
        return insights
