from __future__ import annotations

from dataclasses import dataclass

from gridiron_gpt.draft.fantasy_ranking_score import FantasyRankingScore


@dataclass(frozen=True)
class FantasyRankingExplanation:
    summary: str
    strengths: tuple[str, ...]
    concerns: tuple[str, ...]
    evidence: tuple[str, ...]


class FantasyRankingExplanationService:
    """Explain a fantasy ranking directly from the evidence used to score it."""

    LABELS = {
        "baseline": "historical production",
        "market": "current market value",
        "role": "recent role/usage",
        "cortex": "Cortex intelligence",
        "availability": "availability",
    }

    def explain(
        self,
        score: FantasyRankingScore,
        *,
        overall_rank: int | None = None,
    ) -> FantasyRankingExplanation:
        strengths: list[str] = []
        concerns: list[str] = []
        evidence: list[str] = []

        for component, value in score.components.items():
            label = self.LABELS.get(component, component)
            provenance = score.provenance.get(component)
            detail = f"{label}: {value:.1f}"
            if provenance:
                detail += f" ({provenance})"
            evidence.append(detail)

            strength, concern = self._interpret_component(
                component,
                label,
                value,
            )
            if strength:
                strengths.append(strength)
            if concern:
                concerns.append(concern)

        rank_text = f"#{overall_rank} " if overall_rank is not None else ""
        summary = (
            f"{rank_text}{score.player_name} ({score.position or '-'}, "
            f"{score.team or '-'}) scores {score.ranking_score:.2f}."
        )

        if strengths:
            summary += " Driven by " + ", ".join(strengths[:2]) + "."
        if concerns:
            summary += " Tempered by " + ", ".join(concerns[:2]) + "."

        missing = [
            self.LABELS[name]
            for name in self.LABELS
            if name not in score.components
        ]
        if missing:
            summary += " Missing evidence: " + ", ".join(missing) + "."

        return FantasyRankingExplanation(
            summary=summary,
            strengths=tuple(strengths),
            concerns=tuple(concerns),
            evidence=tuple(evidence),
        )

    @staticmethod
    def _interpret_component(
        component: str,
        label: str,
        value: float,
    ) -> tuple[str | None, str | None]:
        """Translate component values without overstating neutral context.

        Availability is eligibility/risk context, not a talent strength. Cortex is
        centered near 50, so values in the neutral band should not be described as
        below average merely because they are below the generic 60-point threshold.
        """
        if component == "availability":
            return None, None

        if component == "cortex":
            if value >= 70.0:
                return f"elite {label} ({value:.1f})", None
            if value >= 60.0:
                return f"strong {label} ({value:.1f})", None
            if value < 35.0:
                return None, f"weak {label} ({value:.1f})"
            if value < 45.0:
                return None, f"below-average {label} ({value:.1f})"
            return None, None

        if value >= 85.0:
            return f"elite {label} ({value:.1f})", None
        if value >= 70.0:
            return f"strong {label} ({value:.1f})", None
        if value < 45.0:
            return None, f"weak {label} ({value:.1f})"
        if value < 60.0:
            return None, f"below-average {label} ({value:.1f})"
        return None, None
