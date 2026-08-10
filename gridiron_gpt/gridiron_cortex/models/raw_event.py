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

        Provider identity and event-subject identity are intentionally
        combined. One source article can legitimately produce multiple
        player-specific RawEvents, so the same provider record must remain
        distinct for each resolved player while repeated fetches for that
        same player remain duplicates.

        Identity preference is:
        1. provider source ID + event subject,
        2. provider URL + event subject,
        3. normalized event content as a fallback.
        """
        source = self.source.strip().casefold()
        source_id = self.evidence.get("source_id")
        subject = self._identity_subject()

        if source_id:
            parts = [
                "source_id",
                source,
                str(source_id).strip().casefold(),
                subject,
            ]
        elif self.url:
            parts = [
                "url",
                source,
                self.url.strip().casefold(),
                subject,
            ]
        else:
            parts = [
                "content",
                self.headline.strip().casefold(),
                source,
                subject,
                (self.event_type or "").strip().casefold(),
                (self.published_at or "").strip().casefold(),
            ]

        payload = "|".join(parts)
        return sha256(payload.encode("utf-8")).hexdigest()

    def _identity_subject(self) -> str:
        """Return the entity-specific portion of provider-record identity."""
        player_id = (self.player_id or "").strip().casefold()
        player = (self.player or "").strip().casefold()
        team = (self.team or "").strip().casefold()

        if player_id:
            return f"player_id:{player_id}"

        if player:
            return f"player:{player}|team:{team}"

        if team:
            return f"team:{team}"

        return "unresolved"
