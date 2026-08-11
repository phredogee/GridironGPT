from abc import ABC, abstractmethod

from gridiron_gpt.football_state.models.game_state import CanonicalGameState


class GameStateRepository(ABC):
    """Persistence contract for canonical NFL game-state snapshots."""

    @abstractmethod
    def save(self, state: CanonicalGameState) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, game_id: str) -> CanonicalGameState | None:
        raise NotImplementedError

    @abstractmethod
    def get_history(self, game_id: str) -> list[CanonicalGameState]:
        raise NotImplementedError

    @abstractmethod
    def all_latest(self) -> list[CanonicalGameState]:
        raise NotImplementedError
