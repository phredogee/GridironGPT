import hashlib
import re
from difflib import SequenceMatcher


STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "for",
    "to",
    "of",
    "in",
    "on",
    "with",
    "from",
    "by",
    "at",
    "is",
    "are",
    "was",
    "were",
}


def normalize_headline(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    words = [
        word
        for word in text.split()
        if word not in STOPWORDS
    ]
    return " ".join(words)


def story_hash(
    headline: str,
    player: str = "Unknown",
    event_date: str | None = None,
) -> str:
    normalized = normalize_headline(headline)

    key = "|".join(
        [
            normalized,
            player.lower().strip(),
            event_date or "",
        ]
    )

    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def headline_similarity(headline_a: str, headline_b: str) -> float:
    normalized_a = normalize_headline(headline_a)
    normalized_b = normalize_headline(headline_b)

    return round(
        SequenceMatcher(None, normalized_a, normalized_b).ratio(),
        3,
    )


def are_duplicate_stories(
    article_a: dict,
    article_b: dict,
    threshold: float = 0.80,
) -> bool:
    player_a = article_a.get("player", "Unknown")
    player_b = article_b.get("player", "Unknown")

    if player_a != "Unknown" and player_b != "Unknown" and player_a != player_b:
        return False

    headline_a = article_a.get("headline", "")
    headline_b = article_b.get("headline", "")

    if not headline_a or not headline_b:
        return False

    similarity = headline_similarity(headline_a, headline_b)

    return similarity >= threshold


def deduplicate_articles(
    articles: list[dict],
    threshold: float = 0.80,
) -> list[dict]:
    unique_articles = []

    for article in articles:
        is_duplicate = False

        for existing in unique_articles:
            if are_duplicate_stories(article, existing, threshold=threshold):
                is_duplicate = True
                break

        if not is_duplicate:
            unique_articles.append(article)

    return unique_articles
