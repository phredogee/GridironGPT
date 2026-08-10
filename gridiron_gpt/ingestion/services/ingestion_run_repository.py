from __future__ import annotations

import json
from pathlib import Path

from gridiron_gpt.ingestion.models.ingestion_run import IngestionRunSummary


class JsonlIngestionRunRepository:
    """Append-only local history for ingestion observability runs."""

    def __init__(self, path: str | Path = "data/ingestion/ingestion_runs.jsonl") -> None:
        self.path = Path(path)

    def save(self, summary: IngestionRunSummary) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(summary.to_dict(), sort_keys=True) + "\n")

    def load_all(self) -> list[dict]:
        if not self.path.exists():
            return []
        rows = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows

    def latest(self) -> dict | None:
        rows = self.load_all()
        return rows[-1] if rows else None
