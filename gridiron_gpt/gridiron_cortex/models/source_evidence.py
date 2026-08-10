from dataclasses import dataclass, field


@dataclass(frozen=True)
class SourceEvidence:
    """One source reporting a canonical football event."""

    headline: str
    source: str

    category: str
    subtype: str

    published_at: str | None = None
    url: str | None = None

    confidence: float = 0.0

    metadata: dict = field(default_factory=dict)
