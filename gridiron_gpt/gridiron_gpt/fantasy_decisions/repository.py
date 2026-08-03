from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from gridiron_gpt.fantasy_decisions.models import FantasyDecision


class JsonlFantasyDecisionRepository:
    """Append-only audit log for fantasy decisions."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def append(self, decision: FantasyDecision) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(decision)
        payload["decision_type"] = decision.decision_type.value
        payload["action"] = decision.action.value
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")

    def all(self) -> list[dict]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

    def latest(self, limit: int = 20) -> list[dict]:
        if limit <= 0:
            raise ValueError("limit must be positive")
        return self.all()[-limit:]
