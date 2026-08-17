from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FantasyRankingWeights:
    """Explicit weights for the application-level fantasy ranking score."""

    # Preserve the established five-signal balance inside 95% of the model and
    # reserve 5% for position-normalized projected fantasy production.
    baseline: float = 0.5225
    market: float = 0.19
    role: float = 0.095
    cortex: float = 0.095
    availability: float = 0.0475
    projection: float = 0.05

    def validate(self) -> None:
        values = (
            self.baseline,
            self.market,
            self.role,
            self.cortex,
            self.availability,
            self.projection,
        )
        if any(weight < 0 for weight in values):
            raise ValueError("ranking weights must be non-negative")
        if abs(sum(values) - 1.0) > 1e-9:
            raise ValueError("ranking weights must sum to 1.0")


@dataclass(frozen=True)
class FantasyRankingInputs:
    """Normalized 0-100 inputs used to calculate one fantasy ranking score.

    A component may be None when its source is genuinely unavailable. Missing
    evidence is not treated as poor evidence; the scorer redistributes weight
    across the components that are present.
    """

    player_id: str
    player_name: str
    team: str | None
    position: str | None

    baseline_score: float | None
    market_score: float | None
    role_score: float | None
    cortex_score: float | None
    availability_score: float | None
    projection_score: float | None = None

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

    ANCHOR_EVIDENCE_COMPONENTS = {
        "baseline",
        "market",
    }

    def __init__(self, weights: FantasyRankingWeights | None = None) -> None:
        self.weights = weights or FantasyRankingWeights()
        self.weights.validate()

    def score(self, inputs: FantasyRankingInputs) -> FantasyRankingScore:
        raw_components = {
            "baseline": inputs.baseline_score,
            "market": inputs.market_score,
            "role": inputs.role_score,
            "cortex": inputs.cortex_score,
            "availability": inputs.availability_score,
            "projection": inputs.projection_score,
        }
        configured_weights = {
            "baseline": self.weights.baseline,
            "market": self.weights.market,
            "role": self.weights.role,
            "cortex": self.weights.cortex,
            "availability": self.weights.availability,
            "projection": self.weights.projection,
        }

        components = {
            name: self._normalize(value)
            for name, value in raw_components.items()
            if value is not None
        }

        active_weight = sum(
            configured_weights[name]
            for name in components
            if configured_weights[name] > 0
        )
        if active_weight <= 0:
            raise ValueError("at least one weighted ranking component must be available")

        has_anchor_evidence = any(
            name in components and configured_weights[name] > 0
            for name in self.ANCHOR_EVIDENCE_COMPONENTS
        )
        if not has_anchor_evidence:
            raise ValueError(
                "at least one anchor ranking evidence component must be available"
            )

        weighted = {
            name: value * (configured_weights[name] / active_weight)
            for name, value in components.items()
            if configured_weights[name] > 0
        }

        ranking_score = round(sum(weighted.values()), 3)

        return FantasyRankingScore(
            player_id=inputs.player_id,
            player_name=inputs.player_name,
            team=inputs.team,
            position=inputs.position,
            ranking_score=ranking_score,
            components=components,
            weighted_components={key: round(value, 3) for key, value in weighted.items()},
            provenance={
                key: value
                for key, value in inputs.provenance.items()
                if key in components
            },
        )

    @staticmethod
    def _normalize(value: float) -> float:
        return max(0.0, min(100.0, float(value)))
