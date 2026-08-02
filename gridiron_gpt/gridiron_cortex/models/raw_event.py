from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Optional


@dataclass
class RawEvent:
    """
    Normalized event entering the Cortex engine.
    """

    headline: str
    source: str
    player: Optional[str] = None
    team: Optional[str] = None
    summary: str | None = None
    event_type: Optional[str] = None
    published_at: Optional[str] = None
    url: Optional[str] = None
    sentiment: Optional[str] = None
    impact_score: Optional[float] = None
    confidence: Optional[float] = None
    evidence: dict[str, Any] = field(default_factory=dict)
    player_id: Optional[str] = None
    position: Optional[str] = None

    def fingerprint(self) -> str:
        """
        Return a stable provider-record identity for deduplication.

        Identity preference is:
        1. provider source ID when available,
        2. provider + URL when available,
        3. normalized event content as a fallback.

        This lets re-fetched provider records remain duplicates even if
        presentation fields such as the headline are edited later.
        """
        source = self.source.strip().casefold()
        source_id = self.evidence.get("source_id")

        if source_id:
            parts = [
                "source_id",
                source,
                str(source_id).strip().casefold(),
            ]
        elif self.url:
            parts = [
                "url",
                source,
                self.url.strip().casefold(),
            ]
        else:
            parts = [
                "content",
                self.headline.strip().casefold(),
                source,
                (self.player or "").strip().casefold(),
                (self.team or "").strip().casefold(),
                (self.event_type or "").strip().casefold(),
                (self.published_at or "").strip().casefold(),
            ]

        payload = "|".join(parts)
        return sha256(payload.encode("utf-8")).hexdigest()
