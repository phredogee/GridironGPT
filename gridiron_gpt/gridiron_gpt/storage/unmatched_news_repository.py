import json
from datetime import datetime, timezone
from pathlib import Path


class UnmatchedNewsRepository:
    def __init__(
        self,
        path: str | Path = "data/cortex/unmatched_news.jsonl",
    ):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, item: dict) -> bool:
        fingerprint = (
            item.get("story_hash")
            or self._fallback_fingerprint(item)
        )

        if self.contains(fingerprint):
            return False

        record = {
            **item,
            "unmatched_fingerprint": fingerprint,
            "review_status": "pending",
            "captured_at": datetime.now(timezone.utc).isoformat(),
        }

        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record) + "\n")

        return True

    def contains(self, fingerprint: str) -> bool:
        if not self.path.exists():
            return False

        with self.path.open(encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue

                record = json.loads(line)

                if (
                    record.get("unmatched_fingerprint")
                    == fingerprint
                ):
                    return True

        return False

    @staticmethod
    def _fallback_fingerprint(item: dict) -> str:
        return "|".join(
            [
                item.get("headline", "").strip().lower(),
                item.get("url", "").strip().lower(),
                item.get("source", "").strip().lower(),
            ]
        )
