from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SourceRecord:
    """
    Source-neutral record produced by an ingestion adapter.

    SourceRecord represents evidence as received from an external
    provider before Cortex interprets its football significance.
    """

    source: str
    headline: str

    published_at: str | None = None
    url: str | None = None

    summary: str | None = None

    player: str | None = None
    team: str | None = None
    position: str | None = None

    source_id: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )
