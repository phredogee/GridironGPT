from gridiron_cortex.models.signal import Signal


class SignalProcessor:
    """
    Converts a resolved event into a fantasy-relevant signal.
    """

    POSITIVE_KEYWORDS = [
        "returns",
        "returned",
        "first-team",
        "starter",
        "cleared",
        "healthy",
        "full participant",
        "active",
        "breakout",
    ]

    NEGATIVE_KEYWORDS = [
        "injured",
        "injury",
        "out",
        "questionable",
        "doubtful",
        "limited",
        "missed",
        "misses practice",
        "setback",
        "suspended",
        "bench",
        "benched",
    ]

    def process(self, event, entities):
        headline = event.headline
        headline_lower = headline.lower()

        positive_hits = [
            word
            for word in self.POSITIVE_KEYWORDS
            if word in headline_lower
        ]

        negative_hits = [
            word
            for word in self.NEGATIVE_KEYWORDS
            if word in headline_lower
        ]

        has_structured_intelligence = (
            event.sentiment is not None
            or event.impact_score is not None
            or event.confidence is not None
            or bool(event.evidence)
        )

        if has_structured_intelligence:
            sentiment = event.sentiment or "neutral"
            impact_score = float(event.impact_score or 0.0)
            confidence = float(event.confidence or 0.0)

        else:
            if positive_hits and negative_hits:
                if len(negative_hits) > len(positive_hits):
                    sentiment = "negative"
                elif len(positive_hits) > len(negative_hits):
                    sentiment = "positive"
                else:
                    sentiment = "mixed"

            elif negative_hits:
                sentiment = "negative"

            elif positive_hits:
                sentiment = "positive"

            else:
                sentiment = "neutral"

            if sentiment == "positive":
                impact_score = 1.0
            elif sentiment == "negative":
                impact_score = -1.0
            else:
                impact_score = 0.0

            confidence = 1.0

        return Signal(
            headline=headline,
            entities=entities,
            sentiment=sentiment,
            impact_score=impact_score,
            positive_hits=positive_hits,
            negative_hits=negative_hits,
            confidence=confidence,
            signal_type=event.event_type or "news",
            evidence=dict(event.evidence),
        )
