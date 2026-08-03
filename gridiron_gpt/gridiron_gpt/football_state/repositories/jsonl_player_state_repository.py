from __future__ import annotations

import json
from pathlib import Path

from gridiron_gpt.football_state.models.player_state import CanonicalPlayerState
from gridiron_gpt.football_state.repositories.player_state_repository import PlayerStateRepository


class JsonlPlayerStateRepository(PlayerStateRepository):
    """Append-only JSONL repository for canonical player-state history."""

    def __init__(self, path: str | Path = "data/football_state/player_states.jsonl") -> None:
        self.path = Path(path)

    def save(self, state: CanonicalPlayerState) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(state.to_dict(), sort_keys=True) + "\n")

    def _load_all(self) -> list[CanonicalPlayerState]:
        if not self.path.exists():
            return []
        states: list[CanonicalPlayerState] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    states.append(CanonicalPlayerState.from_dict(json.loads(line)))
        return states

    def get(self, player_id: str) -> CanonicalPlayerState | None:
        matches = [state for state in self._load_all() if state.player_id == player_id]
        return matches[-1] if matches else None

    def get_history(self, player_id: str) -> list[CanonicalPlayerState]:
        return [state for state in self._load_all() if state.player_id == player_id]

    def all_latest(self) -> list[CanonicalPlayerState]:
        latest: dict[str, CanonicalPlayerState] = {}
        for state in self._load_all():
            latest[state.player_id] = state
        return list(latest.values())
