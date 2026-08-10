from dataclasses import dataclass, field
from gridiron_cortex.models.source_evidence import SourceEvidence

@dataclass
class CanonicalEvent:
    """
    One football development supported by one or more sources.
    """

    event_key: str

    player: str | None
    team: str | None

    category: str
    subtype: str
    polarity: str

    impact: float
    confidence: float
    consensus: float = 0.0

    evidence: list[SourceEvidence] = field(default_factory=list)

    @property
    def source_count(self) -> int:
        return len(self.evidence)

    @property
    def sources(self) -> list[str]:
        return list(
            dict.fromkeys(
                item.source
                for item in self.evidence
            )
        )
