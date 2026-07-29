from abc import ABC, abstractmethod

from gridiron_cortex.models.player_scorecard import PlayerScorecard


class PlayerScorecardRepository(ABC):
    """
    Persistence contract for Cortex player scorecards.

    Implementations may use JSONL, SQLite, PostgreSQL,
    cloud storage, or another persistence system.
    """

    @abstractmethod
    def get_latest(self, player_id: str) -> PlayerScorecard | None:
        """Return the most recent scorecard for a player."""
        raise NotImplementedError

    @abstractmethod
    def get_history(self, player_id: str) -> list[PlayerScorecard]:
        """Return all stored scorecards for a player."""
        raise NotImplementedError

    @abstractmethod
    def save(self, scorecard: PlayerScorecard) -> None:
        """Persist a new scorecard snapshot."""
        raise NotImplementedError

    @abstractmethod
    def get_all_latest(self) -> list[PlayerScorecard]:
        """
        Return the latest scorecard for every player.
        """

