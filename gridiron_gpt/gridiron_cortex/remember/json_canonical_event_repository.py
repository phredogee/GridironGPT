import json
from dataclasses import asdict
from pathlib import Path

from gridiron_cortex.models.canonical_event import (
    CanonicalEvent,
)
from gridiron_cortex.models.source_evidence import (
    SourceEvidence,
)
from gridiron_cortex.remember.canonical_event_repository import (
    CanonicalEventRepository,
)


class JsonCanonicalEventRepository(
    CanonicalEventRepository
):
    """
    Append-only JSONL repository for canonical-event history.

    Each save writes a complete snapshot. The latest snapshot for an
    event key represents the current canonical state.
    """

    def __init__(
        self,
        file_path: str | Path,
    ):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.file_path.touch(exist_ok=True)

    def save(
        self,
        canonical_event: CanonicalEvent,
    ) -> None:
        try:
            with self.file_path.open(
                "a",
                encoding="utf-8",
            ) as file:
                file.write(
                    json.dumps(
                        asdict(canonical_event)
                    )
                    + "\n"
                )
        except OSError as exc:
            raise RuntimeError(
                "Unable to save canonical event to: "
                f"{self.file_path}"
            ) from exc

    def get(
        self,
        event_key: str,
    ) -> CanonicalEvent | None:
        latest = None

        for canonical_event in self._read_all():
            if canonical_event.event_key == event_key:
                latest = canonical_event

        return latest

    def get_history(
        self,
        event_key: str,
    ) -> list[CanonicalEvent]:
        return [
            canonical_event
            for canonical_event in self._read_all()
            if canonical_event.event_key == event_key
        ]

    def _read_all(
        self,
    ) -> list[CanonicalEvent]:
        events: list[CanonicalEvent] = []

        try:
            with self.file_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                for line in file:
                    line = line.strip()

                    if not line:
                        continue

                    try:
                        record = json.loads(line)

                        evidence = [
                            SourceEvidence(**item)
                            for item in record.pop(
                                "evidence",
                                [],
                            )
                        ]

                        events.append(
                            CanonicalEvent(
                                **record,
                                evidence=evidence,
                            )
                        )
                    except (
                        json.JSONDecodeError,
                        TypeError,
                    ):
                        continue

        except OSError as exc:
            raise RuntimeError(
                "Unable to read canonical events from: "
                f"{self.file_path}"
            ) from exc

        return events
