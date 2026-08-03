from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import Iterable


@dataclass(frozen=True)
class ScheduleTeam:
    team_id: str
    name: str
    division: str

    def __post_init__(self) -> None:
        if not self.team_id.strip() or not self.name.strip() or not self.division.strip():
            raise ValueError("team identity and division are required")


@dataclass(frozen=True)
class ScheduleConfig:
    teams: tuple[ScheduleTeam, ...]
    regular_season_weeks: int
    playoff_start_week: int
    playoff_weeks: int

    def __post_init__(self) -> None:
        if len(self.teams) < 4 or len(self.teams) % 2:
            raise ValueError("schedule requires an even number of at least four teams")
        if len({team.team_id for team in self.teams}) != len(self.teams):
            raise ValueError("team_id values must be unique")
        if self.regular_season_weeks <= 0:
            raise ValueError("regular_season_weeks must be positive")
        if self.playoff_start_week != self.regular_season_weeks + 1:
            raise ValueError("playoff_start_week must immediately follow the regular season")
        if self.playoff_weeks <= 0:
            raise ValueError("playoff_weeks must be positive")

        divisions = Counter(team.division for team in self.teams)
        if len(divisions) < 2:
            raise ValueError("at least two divisions are required")
        if len(set(divisions.values())) != 1:
            raise ValueError("divisions must contain the same number of teams")
        if self.regular_season_weeks < self.minimum_regular_season_weeks:
            raise ValueError(
                f"regular season requires at least {self.minimum_regular_season_weeks} weeks "
                "to play division opponents twice and all other teams once"
            )

    @property
    def division_size(self) -> int:
        return len(self.teams) // len({team.division for team in self.teams})

    @property
    def minimum_regular_season_weeks(self) -> int:
        return 2 * (self.division_size - 1) + (len(self.teams) - self.division_size)


@dataclass(frozen=True)
class ScheduledMatchup:
    week: int
    home_team_id: str
    away_team_id: str
    divisional: bool


@dataclass(frozen=True)
class GeneratedSchedule:
    config: ScheduleConfig
    matchups: tuple[ScheduledMatchup, ...]
    playoff_weeks: tuple[int, ...]
    home_games: dict[str, int]
    away_games: dict[str, int]

    def games_for(self, team_id: str) -> tuple[ScheduledMatchup, ...]:
        return tuple(
            game for game in self.matchups
            if team_id in {game.home_team_id, game.away_team_id}
        )


class ScheduleGenerator:
    """Generate deterministic schedules with divisional and balance guarantees."""

    def generate(self, config: ScheduleConfig) -> GeneratedSchedule:
        pair_counts = self._required_pair_counts(config)
        extra_weeks = config.regular_season_weeks - config.minimum_regular_season_weeks
        self._add_balanced_extra_games(config, pair_counts, extra_weeks)
        weekly_pairs = self._factor_into_weeks(config, pair_counts)
        games = self._orient_home_away(config, weekly_pairs)
        home = Counter(game.home_team_id for game in games)
        away = Counter(game.away_team_id for game in games)
        return GeneratedSchedule(
            config=config,
            matchups=tuple(games),
            playoff_weeks=tuple(
                range(config.playoff_start_week, config.playoff_start_week + config.playoff_weeks)
            ),
            home_games={team.team_id: home[team.team_id] for team in config.teams},
            away_games={team.team_id: away[team.team_id] for team in config.teams},
        )

    @staticmethod
    def _required_pair_counts(config: ScheduleConfig) -> dict[tuple[str, str], int]:
        divisions = {team.team_id: team.division for team in config.teams}
        return {
            (left, right): 2 if divisions[left] == divisions[right] else 1
            for left, right in combinations(sorted(divisions), 2)
        }

    def _add_balanced_extra_games(
        self,
        config: ScheduleConfig,
        counts: dict[tuple[str, str], int],
        extra_weeks: int,
    ) -> None:
        if extra_weeks <= 0:
            return
        rounds = self._round_robin_rounds(sorted(team.team_id for team in config.teams))
        for index in range(extra_weeks):
            for pair in rounds[index % len(rounds)]:
                counts[pair] = counts.get(pair, 0) + 1

    def _factor_into_weeks(
        self,
        config: ScheduleConfig,
        pair_counts: dict[tuple[str, str], int],
    ) -> list[tuple[tuple[str, str], ...]]:
        team_ids = tuple(sorted(team.team_id for team in config.teams))
        matchings = tuple(self._perfect_matchings(team_ids))
        memo: set[tuple[tuple[tuple[str, str], int], ...]] = set()

        def search(remaining, weeks):
            if not remaining:
                return weeks if len(weeks) == config.regular_season_weeks else None
            if len(weeks) >= config.regular_season_weeks:
                return None
            state = tuple(sorted(remaining.items()))
            if state in memo:
                return None
            memo.add(state)

            edge = min(
                remaining,
                key=lambda pair: sum(
                    1 for matching in matchings
                    if pair in matching
                    and all(remaining.get(item, 0) > 0 for item in matching)
                ),
            )
            candidates = [
                matching for matching in matchings
                if edge in matching
                and all(remaining.get(item, 0) > 0 for item in matching)
            ]
            candidates.sort(
                key=lambda matching: sum(remaining[item] for item in matching),
                reverse=True,
            )
            for matching in candidates:
                updated = dict(remaining)
                for pair in matching:
                    updated[pair] -= 1
                    if updated[pair] == 0:
                        del updated[pair]
                result = search(updated, [*weeks, matching])
                if result is not None:
                    return result
            return None

        result = search(dict(pair_counts), [])
        if result is None:
            raise ValueError("unable to construct a conflict-free weekly schedule")
        return result

    @classmethod
    def _perfect_matchings(
        cls,
        teams: tuple[str, ...],
    ) -> Iterable[tuple[tuple[str, str], ...]]:
        if not teams:
            yield ()
            return
        first = teams[0]
        for index in range(1, len(teams)):
            second = teams[index]
            rest = teams[1:index] + teams[index + 1 :]
            pair = tuple(sorted((first, second)))
            for matching in cls._perfect_matchings(rest):
                yield tuple(sorted((pair, *matching)))

    @staticmethod
    def _round_robin_rounds(team_ids: list[str]) -> list[list[tuple[str, str]]]:
        rotating = list(team_ids)
        rounds = []
        for _ in range(len(team_ids) - 1):
            rounds.append([
                tuple(sorted((rotating[index], rotating[-index - 1])))
                for index in range(len(team_ids) // 2)
            ])
            rotating = [rotating[0], rotating[-1], *rotating[1:-1]]
        return rounds

    def _orient_home_away(
        self,
        config: ScheduleConfig,
        weekly_pairs: list[tuple[tuple[str, str], ...]],
    ) -> list[ScheduledMatchup]:
        divisions = {team.team_id: team.division for team in config.teams}
        home = Counter()
        away = Counter()
        divisional_seen = Counter()
        games = []

        for week, pairs in enumerate(weekly_pairs, start=1):
            for left, right in pairs:
                pair = tuple(sorted((left, right)))
                divisional = divisions[left] == divisions[right]
                if divisional:
                    home_team, away_team = (
                        pair if divisional_seen[pair] % 2 == 0 else (pair[1], pair[0])
                    )
                    divisional_seen[pair] += 1
                else:
                    left_balance = home[left] - away[left]
                    right_balance = home[right] - away[right]
                    if left_balance < right_balance:
                        home_team, away_team = left, right
                    elif right_balance < left_balance:
                        home_team, away_team = right, left
                    elif (week + sum(map(ord, left))) % 2 == 0:
                        home_team, away_team = left, right
                    else:
                        home_team, away_team = right, left
                home[home_team] += 1
                away[away_team] += 1
                games.append(ScheduledMatchup(week, home_team, away_team, divisional))

        return self._rebalance_cross_division_games(config, games)

    @staticmethod
    def _rebalance_cross_division_games(
        config: ScheduleConfig,
        games: list[ScheduledMatchup],
    ) -> list[ScheduledMatchup]:
        """Flip cross-division games until total home/away imbalance is minimal."""
        adjusted = list(games)
        team_ids = [team.team_id for team in config.teams]

        def balances(candidate_games):
            home = Counter(game.home_team_id for game in candidate_games)
            away = Counter(game.away_team_id for game in candidate_games)
            return {team_id: home[team_id] - away[team_id] for team_id in team_ids}

        def penalty(values):
            return sum(abs(value) for value in values.values())

        while True:
            current = balances(adjusted)
            current_penalty = penalty(current)
            best_index = None
            best_penalty = current_penalty

            for index, game in enumerate(adjusted):
                if game.divisional:
                    continue
                proposed = dict(current)
                proposed[game.home_team_id] -= 2
                proposed[game.away_team_id] += 2
                proposed_penalty = penalty(proposed)
                if proposed_penalty < best_penalty:
                    best_penalty = proposed_penalty
                    best_index = index

            if best_index is None:
                break
            game = adjusted[best_index]
            adjusted[best_index] = ScheduledMatchup(
                week=game.week,
                home_team_id=game.away_team_id,
                away_team_id=game.home_team_id,
                divisional=False,
            )

        final = balances(adjusted)
        if any(abs(value) > 1 for value in final.values()):
            raise ValueError("unable to balance home and away games within one game")
        return adjusted
