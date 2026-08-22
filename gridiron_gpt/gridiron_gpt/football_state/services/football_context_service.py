from __future__ import annotations

from datetime import datetime

from gridiron_gpt.football_state.models.football_context import FootballContext
from gridiron_gpt.football_state.repositories.player_state_repository import PlayerStateRepository
from gridiron_gpt.football_state.services.player_availability_classifier import (
    PlayerAvailabilityClassifier,
)
from gridiron_gpt.football_state.services.schedule_state_service import ScheduleStateService


class FootballContextService:
    """Assemble provider-neutral player and schedule context for consumers."""

    def __init__(
        self,
        player_repository: PlayerStateRepository,
        schedule_service: ScheduleStateService,
    ) -> None:
        self.player_repository = player_repository
        self.schedule_service = schedule_service

    def for_player(
        self,
        player_id: str,
        *,
        as_of: datetime | None = None,
    ) -> FootballContext | None:
        player = self.player_repository.get(player_id)
        if player is None:
            return None

        availability = PlayerAvailabilityClassifier.classify(player)
        next_game = None
        bye_week = None

        if player.team:
            next_game = self.schedule_service.next_game_for_team(player.team, as_of=as_of)
            bye_week = self._bye_week(player.team)

        return FootballContext(
            player=player,
            availability=availability,
            next_game=next_game,
            bye_week=bye_week,
        )

    def _bye_week(self, team: str) -> int | None:
        for week in range(1, 19):
            if self.schedule_service.is_bye_week(team, week):
                return week
        return None
