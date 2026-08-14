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

            if value >= 85.0:
                strengths.append(f"elite {label} ({value:.1f})")
            elif value >= 70.0:
                strengths.append(f"strong {label} ({value:.1f})")
            elif value < 45.0:
                concerns.append(f"weak {label} ({value:.1f})")
            elif value < 60.0 and component != "availability":
                concerns.append(f"below-average {label} ({value:.1f})")

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
