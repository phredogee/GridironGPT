from __future__ import annotations

from collections import Counter, deque
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

        divisions: dict[str, int] = Counter(team.division for team in self.teams)
        if len(divisions) < 2:
            raise ValueError("at least two divisions are required")
        if len(set(divisions.values())) != 1:
            raise ValueError("divisions must contain the same number of teams")

        minimum = self.minimum_regular_season_weeks
        if self.regular_season_weeks < minimum:
            raise ValueError(
                f"regular season requires at least {minimum} weeks to play "
                "division opponents twice and all other teams once"
            )

    @property
    def division_size(self) -> int:
        return len(self.teams) // len({team.division for team in self.teams})

    @property
    def minimum_regular_season_weeks(self) -> int:
        return 2 * (self.division_size - 1) + (
            len(self.teams) - self.division_size
        )


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
            game
            for game in self.matchups
            if team_id in {game.home_team_id, game.away_team_id}
        )


class ScheduleGenerator:
    """Generate deterministic balanced schedules with divisional guarantees."""

    def generate(self, config: ScheduleConfig) -> GeneratedSchedule:
        required_pairs = self._required_pair_counts(config)
        extra_weeks = config.regular_season_weeks - config.minimum_regular_season_weeks
        if extra_weeks:
            self._add_balanced_extra_games(config, required_pairs, extra_weeks)

        weekly_pairs = self._factor_into_weeks(config, required_pairs)
        oriented = self._orient_home_away(config, weekly_pairs)

        home_games = Counter(game.home_team_id for game in oriented)
        away_games = Counter(game.away_team_id for game in oriented)
        for team in config.teams:
            home_games.setdefault(team.team_id, 0)
            away_games.setdefault(team.team_id, 0)

        return GeneratedSchedule(
            config=config,
            matchups=tuple(oriented),
            playoff_weeks=tuple(
                range(
                    config.playoff_start_week,
                    config.playoff_start_week + config.playoff_weeks,
                )
            ),
            home_games=dict(home_games),
            away_games=dict(away_games),
        )

    @staticmethod
    def _required_pair_counts(
        config: ScheduleConfig,
    ) -> dict[tuple[str, str], int]:
        division_by_team = {
            team.team_id: team.division for team in config.teams
        }
        counts: dict[tuple[str, str], int] = {}
        for left, right in combinations(sorted(division_by_team), 2):
            same_division = division_by_team[left] == division_by_team[right]
            counts[(left, right)] = 2 if same_division else 1
        return counts

    def _add_balanced_extra_games(
        self,
        config: ScheduleConfig,
        counts: dict[tuple[str, str], int],
        extra_weeks: int,
    ) -> None:
        team_ids = sorted(team.team_id for team in config.teams)
        rounds = self._round_robin_rounds(team_ids)
        for index in range(extra_weeks):
            for left, right in rounds[index % len(rounds)]:
                pair = tuple(sorted((left, right)))
                counts[pair] = counts.get(pair, 0) + 1

    def _factor_into_weeks(
        self,
        config: ScheduleConfig,
        pair_counts: dict[tuple[str, str], int],
    ) -> list[tuple[tuple[str, str], ...]]:
        team_ids = tuple(sorted(team.team_id for team in config.teams))
        all_matchings = tuple(self._perfect_matchings(team_ids))
        target_weeks = config.regular_season_weeks
        memo: set[tuple[tuple[tuple[str, str], int], ...]] = set()

        def search(
            remaining: dict[tuple[str, str], int],
            weeks: list[tuple[tuple[str, str], ...]],
        ) -> list[tuple[tuple[str, str], ...]] | None:
            if not remaining:
                return weeks if len(weeks) == target_weeks else None
            if len(weeks) >= target_weeks:
                return None

            state = tuple(sorted(remaining.items()))
            if state in memo:
                return None
            memo.add(state)

            edge = min(
                remaining,
                key=lambda pair: sum(
                    1
                    for matching in all_matchings
                    if pair in matching
                    and all(remaining.get(item, 0) > 0 for item in matching)
                ),
            )
            candidates = [
                matching
                for matching in all_matchings
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
    def _round_robin_rounds(
        team_ids: list[str],
    ) -> list[list[tuple[str, str]]]:
        rotating = list(team_ids)
        rounds: list[list[tuple[str, str]]] = []
        for _ in range(len(team_ids) - 1):
            rounds.append(
                [
                    tuple(sorted((rotating[index], rotating[-index - 1])))
                    for index in range(len(team_ids) // 2)
                ]
            )
            rotating = [rotating[0], rotating[-1], *rotating[1:-1]]
        return rounds

    def _orient_home_away(
        self,
        config: ScheduleConfig,
        weekly_pairs: list[tuple[tuple[str, str], ...]],
    ) -> list[ScheduledMatchup]:
        division_by_team = {
            team.team_id: team.division for team in config.teams
        }
        divisional_seen = Counter()
        games: list[ScheduledMatchup] = []

        for week, pairs in enumerate(weekly_pairs, start=1):
            for left, right in pairs:
                divisional = division_by_team[left] == division_by_team[right]
                pair = tuple(sorted((left, right)))
                if divisional:
                    if divisional_seen[pair] % 2 == 0:
                        home_team, away_team = pair
                    else:
                        away_team, home_team = pair
                    divisional_seen[pair] += 1
                else:
                    home_team, away_team = pair

                games.append(
                    ScheduledMatchup(
                        week=week,
                        home_team_id=home_team,
                        away_team_id=away_team,
                        divisional=divisional,
                    )
                )

        return self._rebalance_cross_division_games(config, games)

    @classmethod
    def _rebalance_cross_division_games(
        cls,
        config: ScheduleConfig,
        games: list[ScheduledMatchup],
    ) -> list[ScheduledMatchup]:
        """Orient cross-division games to the best feasible home totals."""
        adjusted = list(games)
        cross_indices = [
            index for index, game in enumerate(adjusted) if not game.divisional
        ]
        if not cross_indices:
            return adjusted

        team_ids = [team.team_id for team in config.teams]
        fixed_home = Counter(
            game.home_team_id for game in adjusted if game.divisional
        )
        cross_degree = Counter()
        for index in cross_indices:
            game = adjusted[index]
            cross_degree[game.home_team_id] += 1
            cross_degree[game.away_team_id] += 1

        total_games = config.regular_season_weeks
        low = total_games // 2
        high = total_games - low
        choices: dict[str, tuple[int, ...]] = {}
        for team_id in team_ids:
            feasible = []
            for total_home in sorted({low, high}):
                cross_home = total_home - fixed_home[team_id]
                if 0 <= cross_home <= cross_degree[team_id]:
                    feasible.append(cross_home)
            if not feasible:
                feasible = list(range(cross_degree[team_id] + 1))
            choices[team_id] = tuple(feasible)

        target_sum = len(cross_indices)
        targets = cls._target_assignments(team_ids, choices, target_sum)
        for target in targets:
            orientation = cls._flow_orientation(adjusted, cross_indices, target)
            if orientation is None:
                continue
            for index, home_team in orientation.items():
                game = adjusted[index]
                away_team = (
                    game.away_team_id
                    if home_team == game.home_team_id
                    else game.home_team_id
                )
                adjusted[index] = ScheduledMatchup(
                    week=game.week,
                    home_team_id=home_team,
                    away_team_id=away_team,
                    divisional=False,
                )
            return adjusted

        # A schedule should remain usable even when unusual extra-week rules
        # make the ideal floor/ceiling targets infeasible. Preserve the best
        # deterministic orientation rather than breaking exports entirely.
        return adjusted

    @staticmethod
    def _target_assignments(
        team_ids: list[str],
        choices: dict[str, tuple[int, ...]],
        target_sum: int,
    ) -> Iterable[dict[str, int]]:
        suffix_min = [0] * (len(team_ids) + 1)
        suffix_max = [0] * (len(team_ids) + 1)
        for index in range(len(team_ids) - 1, -1, -1):
            values = choices[team_ids[index]]
            suffix_min[index] = suffix_min[index + 1] + min(values)
            suffix_max[index] = suffix_max[index + 1] + max(values)

        def walk(index: int, remaining: int, current: dict[str, int]):
            if index == len(team_ids):
                if remaining == 0:
                    yield dict(current)
                return
            if remaining < suffix_min[index] or remaining > suffix_max[index]:
                return
            team_id = team_ids[index]
            for value in choices[team_id]:
                current[team_id] = value
                yield from walk(index + 1, remaining - value, current)
            current.pop(team_id, None)

        yield from walk(0, target_sum, {})

    @staticmethod
    def _flow_orientation(
        games: list[ScheduledMatchup],
        cross_indices: list[int],
        target: dict[str, int],
    ) -> dict[int, str] | None:
        source = "source"
        sink = "sink"
        capacity: dict[tuple[str, str], int] = {}
        adjacency: dict[str, list[str]] = {}

        def add_edge(left: str, right: str, cap: int) -> None:
            adjacency.setdefault(left, []).append(right)
            adjacency.setdefault(right, []).append(left)
            capacity[(left, right)] = cap
            capacity.setdefault((right, left), 0)

        edge_nodes: dict[int, str] = {}
        for position, index in enumerate(cross_indices):
            node = f"edge:{position}"
            edge_nodes[index] = node
            game = games[index]
            add_edge(source, node, 1)
            add_edge(node, game.home_team_id, 1)
            add_edge(node, game.away_team_id, 1)

        for team_id, required in target.items():
            add_edge(team_id, sink, required)

        flow = 0
        while True:
            parent: dict[str, str | None] = {source: None}
            queue = deque([source])
            while queue and sink not in parent:
                node = queue.popleft()
                for neighbor in adjacency.get(node, []):
                    if neighbor in parent:
                        continue
                    if capacity.get((node, neighbor), 0) <= 0:
                        continue
                    parent[neighbor] = node
                    queue.append(neighbor)
            if sink not in parent:
                break
            node = sink
            while parent[node] is not None:
                previous = parent[node]
                capacity[(previous, node)] -= 1
                capacity[(node, previous)] += 1
                node = previous
            flow += 1

        if flow != len(cross_indices):
            return None

        orientation: dict[int, str] = {}
        for index, node in edge_nodes.items():
            game = games[index]
            for team_id in (game.home_team_id, game.away_team_id):
                if capacity.get((team_id, node), 0) == 1:
                    orientation[index] = team_id
                    break
        return orientation if len(orientation) == len(cross_indices) else None
