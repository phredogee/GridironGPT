from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import date, datetime, time, timezone
from typing import Any
from zoneinfo import ZoneInfo

import nflreadpy as nfl

from gridiron_gpt.football_state.models.game_state import CanonicalGameState
from gridiron_gpt.football_state.repositories.game_state_repository import GameStateRepository


class ScheduleStateService:
    """Promote nflverse schedule rows into canonical queryable game state."""

    MEANINGFUL_FIELDS = (
        "season",
        "week",
        "season_type",
        "home_team",
        "away_team",
        "kickoff_at",
        "game_status",
        "venue",
    )

    def __init__(
        self,
        repository: GameStateRepository,
        *,
        season: int | None = None,
        schedule_loader: Callable[[], Any] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.season = season if season is not None else self.clock().year
        self.schedule_loader = schedule_loader or self._load_schedule

    def _load_schedule(self):
        return nfl.load_schedules(self.season)

    def refresh(self) -> list[CanonicalGameState]:
        effective_at = self.clock()
        states: list[CanonicalGameState] = []

        for row in self._iter_rows(self.schedule_loader()):
            state = self._build_state(row, effective_at)
            if state is None:
                continue

            previous = self.repository.get(state.game_id)
            if self.has_meaningful_change(previous, state):
                self.repository.save(state)

            states.append(state)

        return states

    def get(self, game_id: str) -> CanonicalGameState | None:
        return self.repository.get(game_id)

    def games_for_team(self, team: str) -> list[CanonicalGameState]:
        return [game for game in self.repository.games_for_team(team) if game.season == self.season]

    def next_game_for_team(
        self,
        team: str,
        *,
        as_of: datetime | None = None,
    ) -> CanonicalGameState | None:
        reference = as_of or self.clock()
        candidates = [
            game
            for game in self.games_for_team(team)
            if game.game_status != "final"
            and game.kickoff_at is not None
            and game.kickoff_at >= reference
        ]
        return candidates[0] if candidates else None

    def game_for_team_week(self, team: str, week: int) -> CanonicalGameState | None:
        matches = [
            game
            for game in self.games_for_team(team)
            if game.season_type == "REG" and game.week == week
        ]
        return matches[0] if matches else None

    def is_bye_week(self, team: str, week: int) -> bool:
        if not 1 <= week <= 18:
            raise ValueError("regular-season week must be between 1 and 18")
        return self.game_for_team_week(team, week) is None

    @classmethod
    def has_meaningful_change(
        cls,
        previous: CanonicalGameState | None,
        current: CanonicalGameState,
    ) -> bool:
        if previous is None:
            return True
        return any(
            getattr(previous, field_name) != getattr(current, field_name)
            for field_name in cls.MEANINGFUL_FIELDS
        )

    def _build_state(
        self,
        row: dict[str, Any],
        effective_at: datetime,
    ) -> CanonicalGameState | None:
        game_id = self._text(row.get("game_id"))
        season = self._integer(row.get("season"))
        week = self._integer(row.get("week"))
        season_type = self._text(row.get("game_type"))
        home_team = self._text(row.get("home_team"))
        away_team = self._text(row.get("away_team"))

        if not all((game_id, season is not None, week is not None, season_type, home_team, away_team)):
            return None

        return CanonicalGameState(
            game_id=game_id,
            season=season,
            week=week,
            season_type=season_type,
            home_team=home_team,
            away_team=away_team,
            kickoff_at=self._kickoff_at(row.get("gameday"), row.get("gametime")),
            game_status=self._game_status(row),
            venue=self._optional_text(row.get("stadium")),
            effective_at=effective_at,
            source="nflverse schedule",
        )

    @staticmethod
    def _iter_rows(data: Any) -> Iterable[dict[str, Any]]:
        if hasattr(data, "iter_rows"):
            return data.iter_rows(named=True)
        return data

    @classmethod
    def _kickoff_at(cls, gameday: Any, gametime: Any) -> datetime | None:
        day_text = cls._text(gameday)
        time_text = cls._text(gametime)
        if not day_text or not time_text:
            return None

        try:
            day = date.fromisoformat(day_text)
            kickoff_time = time.fromisoformat(time_text)
        except ValueError:
            return None

        eastern = ZoneInfo("America/New_York")
        return datetime.combine(day, kickoff_time, tzinfo=eastern).astimezone(timezone.utc)

    @classmethod
    def _game_status(cls, row: dict[str, Any]) -> str:
        result = row.get("result")
        if result is None:
            return "scheduled"
        return "final"

    @staticmethod
    def _text(value: Any) -> str:
        return "" if value is None else str(value).strip()

    @classmethod
    def _optional_text(cls, value: Any) -> str | None:
        text = cls._text(value)
        return text or None

    @staticmethod
    def _integer(value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
