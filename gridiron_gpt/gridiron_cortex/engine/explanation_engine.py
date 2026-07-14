class ExplanationEngine:
    """
    Converts engine output into a plain-English explanation.
    """

    def explain(self, signal, impacts, recommendations):
        if not recommendations:
            return "No recommendation was generated for this event."

        lines = [
            f"Signal analyzed: {signal.headline}",
            f"Signal sentiment: {signal.sentiment}.",
            f"Signal impact: {signal.impact_score:+.3f}.",
        ]

        evidence = signal.evidence or {}

        evidence_count = int(
            evidence.get("evidence_count") or 0
        )
        sources = evidence.get("sources") or []
        methods = evidence.get("methods") or []
        classification = evidence.get("classification")
        reasons = evidence.get("reasons") or []

        if evidence_count:
            lines.append(
                f"Evidence count: {evidence_count}."
            )

        if sources:
            lines.append(
                "Sources: "
                + ", ".join(str(source) for source in sources)
                + "."
            )

        if methods:
            lines.append(
                "Methods: "
                + ", ".join(str(method) for method in methods)
                + "."
            )

        if classification:
            lines.append(
                f"Trend classification: {classification}."
            )

        for reason in reasons[:3]:
            lines.append(f"Evidence: {reason}")

        for rec in recommendations:
            lines.append(
                f"{rec.entity_name} is a {rec.action} "
                f"with {rec.confidence}% confidence. "
                f"Score movement: {rec.score_delta:+.3f}."
            )

        return " ".join(lines)
