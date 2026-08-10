from abc import ABC, abstractmethod

from gridiron_gpt.football_state.models.player_state import CanonicalPlayerState


class PlayerStateRepository(ABC):
    """Persistence contract for canonical NFL player-state snapshots."""

    @abstractmethod
    def save(self, state: CanonicalPlayerState) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, player_id: str) -> CanonicalPlayerState | None:
        raise NotImplementedError

    @abstractmethod
    def get_history(self, player_id: str) -> list[CanonicalPlayerState]:
        raise NotImplementedError

    @abstractmethod
    def all_latest(self) -> list[CanonicalPlayerState]:
        raise NotImplementedError
