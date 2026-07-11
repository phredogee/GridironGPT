import json
from dataclasses import asdict
from pathlib import Path

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.storage.event_repository import EventRepository


class JsonEventRepository(EventRepository):
    """
    Append-only JSONL repository for normalized events.
    """

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.touch(exist_ok=True)

    def contains(self, fingerprint: str) -> bool:
        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()

                    if not line:
                        continue

                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if record.get("fingerprint") == fingerprint:
                        return True

        except OSError as exc:
            raise RuntimeError(
                f"Unable to read event repository: {self.file_path}"
            ) from exc

        return False

    def save(self, event: RawEvent) -> None:
        record = asdict(event)
        record["fingerprint"] = event.fingerprint()

        try:
            with self.file_path.open("a", encoding="utf-8") as file:
                file.write(json.dumps(record) + "\n")
        except OSError as exc:
            raise RuntimeError(
                f"Unable to save event to: {self.file_path}"
            ) from exc
