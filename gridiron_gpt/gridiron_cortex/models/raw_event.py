from dataclasses import dataclass
from hashlib import sha256
from typing import Optional


@dataclass
class RawEvent:
    """
    Normalized event entering the Cortex engine.
    """

    headline: str
    source: str
    player: Optional[str] = None
    team: Optional[str] = None
    event_type: Optional[str] = None
    published_at: Optional[str] = None
    url: Optional[str] = None

    def fingerprint(self) -> str:
        """
        Return a stable identity for deduplication.

        The first version uses normalized event content rather than a
        generated database ID.
        """
        parts = [
            self.headline.strip().lower(),
            self.source.strip().lower(),
            (self.player or "").strip().lower(),
            (self.team or "").strip().lower(),
            (self.event_type or "").strip().lower(),
            (self.published_at or "").strip().lower(),
            (self.url or "").strip().lower(),
        ]

        payload = "|".join(parts)
        return sha256(payload.encode("utf-8")).hexdigest()
