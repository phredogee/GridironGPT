from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FantasyRankingWeights:
    """Explicit weights for the application-level fantasy ranking score."""

    baseline: float = 0.55
    market: float = 0.20
    role: float = 0.10
    cortex: float = 0.10
    availability: float = 0.05

    def validate(self) -> None:
        values = (
            self.baseline,
            self.market,
            self.role,
            self.cortex,
            self.availability,
        )
        if any(weight < 0 for weight in values):
            raise ValueError("ranking weights must be non-negative")
        if abs(sum(values) - 1.0) > 1e-9:
            raise ValueError("ranking weights must sum to 1.0")


@dataclass(frozen=True)
class FantasyRankingInputs:
    """Normalized 0-100 inputs used to calculate one fantasy ranking score."""

    player_id: str
    player_name: str
    team: str | None
    position: str | None

    baseline_score: float
    market_score: float
    role_score: float
    cortex_score: float
    availability_score: float

    provenance: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class FantasyRankingScore:
    """Explainable application-level fantasy ranking result."""

    player_id: str
    player_name: str
    team: str | None
    position: str | None

    ranking_score: float
    components: dict[str, float]
    weighted_components: dict[str, float]
    provenance: dict[str, str]


class FantasyRankingScorer:
    """Combine normalized fantasy inputs without redefining Cortex score semantics."""

    def __init__(self, weights: FantasyRankingWeights | None = None) -> None:
        self.weights = weights or FantasyRankingWeights()
        self.weights.validate()

    def score(self, inputs: FantasyRankingInputs) -> FantasyRankingScore:
        components = {
            "baseline": self._normalize(inputs.baseline_score),
            "market": self._normalize(inputs.market_score),
            "role": self._normalize(inputs.role_score),
            "cortex": self._normalize(inputs.cortex_score),
            "availability": self._normalize(inputs.availability_score),
        }

        weighted = {
            "baseline": components["baseline"] * self.weights.baseline,
            "market": components["market"] * self.weights.market,
            "role": components["role"] * self.weights.role,
            "cortex": components["cortex"] * self.weights.cortex,
            "availability": components["availability"] * self.weights.availability,
        }

        ranking_score = round(sum(weighted.values()), 3)

        return FantasyRankingScore(
            player_id=inputs.player_id,
            player_name=inputs.player_name,
            team=inputs.team,
            position=inputs.position,
            ranking_score=ranking_score,
            components=components,
            weighted_components={
                key: round(value, 3)
                for key, value in weighted.items()
            },
            provenance=dict(inputs.provenance),
        )

    @staticmethod
    def _normalize(value: float) -> float:
        return max(0.0, min(100.0, float(value)))
