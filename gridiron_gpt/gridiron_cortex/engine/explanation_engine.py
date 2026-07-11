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
        ]

        for rec in recommendations:
            lines.append(
                f"{rec.entity_name} is a {rec.action} "
                f"with {rec.confidence}% confidence. "
                f"Score movement: {rec.score_delta}."
            )

        return " ".join(lines)
