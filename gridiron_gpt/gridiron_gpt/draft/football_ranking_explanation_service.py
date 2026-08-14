from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class FootballRankingExplanation:
    summary: str
    takeaway: str
    headlines: tuple[str, ...]


class FootballRankingExplanationService:
    """Translate recent scored football signals into fan-facing ranking context."""

    def explain(
        self,
        *,
        recent_signals: list[dict] | tuple[dict, ...] | None,
        fallback: str,
    ) -> FootballRankingExplanation:
        signals = list(recent_signals or [])
        signals = [signal for signal in signals if signal.get("headline")]
        signals.sort(
            key=lambda signal: abs(float(signal.get("value", 0.0) or 0.0)),
            reverse=True,
        )

        headlines = tuple(
            str(signal.get("headline", "")).strip()
            for signal in signals[:3]
            if str(signal.get("headline", "")).strip()
        )

        if not headlines:
            return FootballRankingExplanation(
                summary="No recent football-specific signal is available.",
                takeaway=fallback,
                headlines=(),
            )

        summary = "Football read: " + " ".join(
            headline.rstrip(".") + "." for headline in headlines[:2]
        )
        takeaway = self._compact_takeaway(headlines[0], fallback=fallback)

        return FootballRankingExplanation(
            summary=summary,
            takeaway=takeaway,
            headlines=headlines,
        )

    @staticmethod
    def _compact_takeaway(headline: str, *, fallback: str) -> str:
        text = headline.casefold()
        patterns = (
            (("missed practice", "did not practice", "dnp"), "Missed practice"),
            (("limited practice", "limited participant"), "Limited in practice"),
            (("full practice", "full participant"), "Full practice return"),
            (("first-team", "first team", "starting reps"), "First-team reps"),
            (("second-team", "second team"), "Second-team reps"),
            (("losing reps", "fewer reps", "reduced reps"), "Losing reps"),
            (("more reps", "increased reps", "expanded role"), "Role expanding"),
            (("goal-line", "goal line"), "Goal-line role"),
            (("red-zone", "red zone"), "Red-zone role"),
            (("targets", "target share"), "Targets trending up"),
            (("carries", "carry share"), "Carries trending up"),
            (("injury", "injured", "hamstring", "ankle", "knee", "foot"), "Injury concern"),
            (("cleared", "returns", "returned", "activated"), "Back in action"),
            (("starter", "starting"), "Starting role"),
            (("backup", "rb2", "wr2", "te2"), "Backup pressure"),
        )

        for needles, label in patterns:
            if any(needle in text for needle in needles):
                return label

        words = re.findall(r"[A-Za-z0-9#'-]+", headline)
        if 2 <= len(words) <= 5:
            return " ".join(words)
        if len(words) > 5:
            return " ".join(words[:5])
        return fallback
