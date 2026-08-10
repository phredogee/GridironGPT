from dataclasses import dataclass


@dataclass(frozen=True)
class SourceReliability:
    """
    Provides reliability scores for news sources.
    """

    DEFAULT_SCORE = 0.70

    SCORES = {
        "NFL.com": 1.00,
        "ESPN": 1.00,
        "The Athletic": 0.99,
        "NBC Sports": 0.98,
        "Yahoo Sports": 0.95,
        "CBS Sports": 0.95,
        "Fox Sports": 0.93,
        "Pro Football Talk": 0.92,
        "Sleeper": 0.90,
        "Unknown": DEFAULT_SCORE,
    }

    @classmethod
    def score(
        cls,
        source: str,
    ) -> float:
        return cls.SCORES.get(
            source,
            cls.DEFAULT_SCORE,
        )

    @classmethod
    def confidence_boost(
        cls,
        sources: list[str],
    ) -> float:
        weighted_score = sum(
            cls.score(source)
            for source in sources
        )

        return min(
            weighted_score * 0.02,
            0.08,
        )
