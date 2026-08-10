from __future__ import annotations

from collections import Counter

from gridiron_gpt.football_state.models.codex_entry import CodexEntryType
from gridiron_gpt.football_state.repositories.codex_repository import JsonlCodexRepository


class CodexContextService:
    """Query compact historical context without turning history into automatic score changes."""

    def __init__(self, repository: JsonlCodexRepository):
        self.repository = repository

    def summarize(self, player_id: str) -> dict:
        entries = self.repository.for_player(player_id)
        counts = Counter(entry.entry_type.value for entry in entries)
        teams = []
        for entry in entries:
            if entry.team and entry.team not in teams:
                teams.append(entry.team)
        seasons = sorted({entry.season for entry in entries})
        return {
            "player_id": player_id,
            "entry_count": len(entries),
            "entry_types": dict(counts),
            "teams": teams,
            "seasons": seasons,
            "latest_role": self._summary(player_id, CodexEntryType.ROLE_HISTORY),
            "latest_availability": self._summary(player_id, CodexEntryType.AVAILABILITY_HISTORY),
            "latest_production": self._summary(player_id, CodexEntryType.PRODUCTION_HISTORY),
        }

    def recent(self, player_id: str, limit: int = 5):
        if limit <= 0:
            raise ValueError("limit must be positive")
        entries = self.repository.for_player(player_id)
        return list(reversed(entries[-limit:]))

    def _summary(self, player_id: str, entry_type: CodexEntryType) -> str | None:
        entry = self.repository.latest(player_id, entry_type)
        return entry.summary if entry else None
