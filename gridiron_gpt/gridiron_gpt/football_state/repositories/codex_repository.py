from __future__ import annotations

import json
from pathlib import Path

from gridiron_gpt.football_state.models.codex_entry import CodexEntry, CodexEntryType


class JsonlCodexRepository:
    """Append-only historical football knowledge store with deterministic dedupe."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def append(self, entry: CodexEntry) -> bool:
        if entry.fingerprint() in {existing.fingerprint() for existing in self.all()}:
            return False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry.to_dict(), sort_keys=True) + "\n")
        return True

    def all(self) -> list[CodexEntry]:
        if not self.path.exists():
            return []
        entries = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    entries.append(CodexEntry.from_dict(json.loads(line)))
        return entries

    def for_player(
        self,
        player_id: str,
        *,
        entry_type: CodexEntryType | None = None,
    ) -> list[CodexEntry]:
        entries = [entry for entry in self.all() if entry.player_id == player_id]
        if entry_type is not None:
            entries = [entry for entry in entries if entry.entry_type == entry_type]
        return sorted(entries, key=lambda entry: entry.occurred_at)

    def latest(
        self,
        player_id: str,
        entry_type: CodexEntryType,
    ) -> CodexEntry | None:
        entries = self.for_player(player_id, entry_type=entry_type)
        return entries[-1] if entries else None
