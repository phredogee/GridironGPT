from __future__ import annotations

from dataclasses import dataclass

from gridiron_gpt.product.commissioner_suite import ScheduleAnalyticsService
from gridiron_gpt.product.schedule_generator import GeneratedSchedule, ScheduledMatchup


@dataclass(frozen=True)
class ScheduleConstraints:
    rivalry_week: int | None = None
    rivalry_pairs: tuple[tuple[str, str], ...] = ()
    max_home_streak: int = 3
    max_away_streak: int = 3
    prevent_consecutive_repeat_opponents: bool = True


@dataclass(frozen=True)
class RankedScheduleOption:
    option_number: int
    schedule: GeneratedSchedule
    quality_score: float
    violations: tuple[str, ...]


class ScheduleConstraintService:
    def validate(
        self,
        schedule: GeneratedSchedule,
        constraints: ScheduleConstraints,
    ) -> tuple[str, ...]:
        violations: list[str] = []
        analytics = ScheduleAnalyticsService().analyze(schedule)
        for team_id, streak in analytics.longest_home_streak.items():
            if streak > constraints.max_home_streak:
                violations.append(f"{team_id} has {streak} consecutive home games")
        for team_id, streak in analytics.longest_away_streak.items():
            if streak > constraints.max_away_streak:
                violations.append(f"{team_id} has {streak} consecutive away games")

        if constraints.rivalry_week is not None:
            week_pairs = {
                frozenset((game.home_team_id, game.away_team_id))
                for game in schedule.matchups
                if game.week == constraints.rivalry_week
            }
            for pair in constraints.rivalry_pairs:
                if frozenset(pair) not in week_pairs:
                    violations.append(
                        f"rivalry {pair[0]} vs {pair[1]} is not in Week {constraints.rivalry_week}"
                    )

        if constraints.prevent_consecutive_repeat_opponents:
            games_by_team: dict[str, list[tuple[int, str]]] = {}
            for game in schedule.matchups:
                games_by_team.setdefault(game.home_team_id, []).append((game.week, game.away_team_id))
                games_by_team.setdefault(game.away_team_id, []).append((game.week, game.home_team_id))
            for team_id, games in games_by_team.items():
                ordered = sorted(games)
                for previous, current in zip(ordered, ordered[1:]):
                    if previous[1] == current[1] and current[0] == previous[0] + 1:
                        violations.append(
                            f"{team_id} plays {current[1]} in consecutive weeks"
                        )
        return tuple(sorted(set(violations)))


class ScheduleOptionService:
    """Create valid home/away alternatives without changing opponents or weeks."""

    def generate_options(
        self,
        schedule: GeneratedSchedule,
        constraints: ScheduleConstraints,
        *,
        option_count: int = 3,
    ) -> list[RankedScheduleOption]:
        if option_count <= 0:
            raise ValueError("option_count must be positive")
        candidates = [schedule]
        cross_indexes = [index for index, game in enumerate(schedule.matchups) if not game.divisional]
        for offset in range(1, option_count * 2 + 1):
            adjusted = list(schedule.matchups)
            for position, index in enumerate(cross_indexes):
                if (position + offset) % 3 == 0:
                    game = adjusted[index]
                    adjusted[index] = ScheduledMatchup(
                        week=game.week,
                        home_team_id=game.away_team_id,
                        away_team_id=game.home_team_id,
                        divisional=False,
                    )
            candidates.append(self._rebuild(schedule, tuple(adjusted)))

        validator = ScheduleConstraintService()
        analytics = ScheduleAnalyticsService()
        ranked: list[RankedScheduleOption] = []
        seen: set[tuple[tuple[int, str, str], ...]] = set()
        for candidate in candidates:
            identity = tuple(
                (game.week, game.home_team_id, game.away_team_id)
                for game in candidate.matchups
            )
            if identity in seen:
                continue
            seen.add(identity)
            violations = validator.validate(candidate, constraints)
            quality = analytics.analyze(candidate).score - (15.0 * len(violations))
            ranked.append(
                RankedScheduleOption(
                    option_number=0,
                    schedule=candidate,
                    quality_score=round(quality, 2),
                    violations=violations,
                )
            )
        ranked.sort(key=lambda item: (len(item.violations), -item.quality_score))
        return [
            RankedScheduleOption(index, item.schedule, item.quality_score, item.violations)
            for index, item in enumerate(ranked[:option_count], start=1)
        ]

    @staticmethod
    def _rebuild(original: GeneratedSchedule, games: tuple[ScheduledMatchup, ...]) -> GeneratedSchedule:
        home = {team.team_id: 0 for team in original.config.teams}
        away = {team.team_id: 0 for team in original.config.teams}
        for game in games:
            home[game.home_team_id] += 1
            away[game.away_team_id] += 1
        return GeneratedSchedule(
            config=original.config,
            matchups=games,
            playoff_weeks=original.playoff_weeks,
            home_games=home,
            away_games=away,
        )
