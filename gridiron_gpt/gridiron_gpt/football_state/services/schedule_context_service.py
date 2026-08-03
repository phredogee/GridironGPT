from __future__ import annotations

from gridiron_gpt.football_state.models.game_context import (
    CanonicalGameContext,
    GameStatus,
)
from gridiron_gpt.football_state.models.schedule_context import UpcomingScheduleContext


class ScheduleContextService:
    """Resolve a team's next game, bye state, and rest window from schedule facts."""

    def resolve(
        self,
        team: str,
        season: int,
        as_of_week: int,
        games: list[CanonicalGameContext],
    ) -> UpcomingScheduleContext:
        if not team.strip():
            raise ValueError("team is required")
        if season <= 0:
            raise ValueError("season must be positive")
        if as_of_week <= 0:
            raise ValueError("as_of_week must be positive")

        team_games = sorted(
            (
                game
                for game in games
                if game.season == season and game.includes_team(team)
            ),
            key=lambda game: (game.week, game.kickoff_at),
        )

        previous = self._previous_game(team_games, as_of_week)
        next_game = self._next_game(team_games, as_of_week)

        # A missing game in the requested week is a bye only when later schedule
        # evidence exists. This prevents the end of a partial schedule from being
        # mislabeled as a bye.
        current_week_game = next((game for game in team_games if game.week == as_of_week), None)
        later_game_exists = any(game.week > as_of_week for game in team_games)
        bye_week = current_week_game is None and later_game_exists

        days_rest = None
        if previous is not None and next_game is not None:
            days_rest = (next_game.kickoff_at - previous.kickoff_at).total_seconds() / 86400.0

        return UpcomingScheduleContext(
            team=team,
            season=season,
            as_of_week=as_of_week,
            next_game=next_game,
            opponent=next_game.opponent_for(team) if next_game else None,
            venue_side=next_game.venue_side_for(team) if next_game else None,
            bye_week=bye_week,
            days_rest=days_rest,
            previous_game_id=previous.game_id if previous else None,
        )

    @staticmethod
    def _previous_game(
        games: list[CanonicalGameContext],
        as_of_week: int,
    ) -> CanonicalGameContext | None:
        prior = [
            game
            for game in games
            if game.week < as_of_week and game.status == GameStatus.FINAL
        ]
        return prior[-1] if prior else None

    @staticmethod
    def _next_game(
        games: list[CanonicalGameContext],
        as_of_week: int,
    ) -> CanonicalGameContext | None:
        candidates = [
            game
            for game in games
            if game.week >= as_of_week
            and game.status not in {GameStatus.FINAL, GameStatus.CANCELED}
        ]
        return candidates[0] if candidates else None
