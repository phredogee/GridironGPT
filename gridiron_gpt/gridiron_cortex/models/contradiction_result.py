from dataclasses import dataclass, field


@dataclass
class ContradictionResult:
    """
    Represents whether evidence supporting a CanonicalEvent
    contains conflicting information.
    """

    has_conflict: bool = False

    severity: float = 0.0

    confidence_penalty: float = 0.0

    conflicting_sources: list[str] = field(default_factory=list)

    explanation: str = ""
