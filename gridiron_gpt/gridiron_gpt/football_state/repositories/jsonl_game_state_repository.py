from __future__ import annotations

import json
from pathlib import Path

from gridiron_gpt.football_state.models.game_state import CanonicalGameState
from gridiron_gpt.football_state.repositories.game_state_repository import GameStateRepository


class JsonlGameStateRepository(GameStateRepository):
    """Append-only JSONL repository for canonical game-state history."""

    def __init__(self, path: str | Path = "data/football_state/game_states.jsonl") -> None:
        self.path = Path(path)

    def save(self, state: CanonicalGameState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(state.to_dict(), sort_keys=True) + "\n")

    def _load_all(self) -> list[CanonicalGameState]:
        if not self.path.exists():
            return []

        states: list[CanonicalGameState] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    states.append(CanonicalGameState.from_dict(json.loads(line)))
        return states

    def get(self, game_id: str) -> CanonicalGameState | None:
        matches = [state for state in self._load_all() if state.game_id == game_id]
        return matches[-1] if matches else None

    def get_history(self, game_id: str) -> list[CanonicalGameState]:
        return [state for state in self._load_all() if state.game_id == game_id]

    def all_latest(self) -> list[CanonicalGameState]:
        latest: dict[str, CanonicalGameState] = {}
        for state in self._load_all():
            latest[state.game_id] = state
        return list(latest.values())
