from __future__ import annotations

from dataclasses import dataclass

from gridiron_gpt.football_state.models.game_state import CanonicalGameState
from gridiron_gpt.football_state.models.player_state import CanonicalPlayerState
from gridiron_gpt.football_state.services.player_availability_classifier import PlayerAvailability


@dataclass(frozen=True)
class FootballContext:
    """Provider-neutral football context assembled for one player."""

    player: CanonicalPlayerState
    availability: PlayerAvailability
    next_game: CanonicalGameState | None
    bye_week: int | None

    @property
    def opponent(self) -> str | None:
        if self.next_game is None or not self.player.team:
            return None
        if self.next_game.home_team == self.player.team:
            return self.next_game.away_team
        if self.next_game.away_team == self.player.team:
            return self.next_game.home_team
        return None

    @property
    def location(self) -> str | None:
        if self.next_game is None or not self.player.team:
            return None
        if self.next_game.home_team == self.player.team:
            return "HOME"
        if self.next_game.away_team == self.player.team:
            return "AWAY"
        return None
