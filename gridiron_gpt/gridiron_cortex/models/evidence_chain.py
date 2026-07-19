from dataclasses import dataclass, field


@dataclass(frozen=True)
class EvidenceStep:
    """One traceable step in a Cortex reasoning chain."""

    faculty: str
    step_type: str
    summary: str
    entity_name: str | None = None
    value: float | str | None = None
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EvidenceChain:
    """Structured explanation of how Cortex reached a conclusion."""

    entity_name: str
    action: str
    confidence: float
    steps: list[EvidenceStep] = field(default_factory=list)
