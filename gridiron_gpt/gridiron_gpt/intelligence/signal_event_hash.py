import hashlib

from gridiron_gpt.intelligence.story_dedup import normalize_headline


def build_signal_event_hash(
    story_hash: str | None,
    player: str,
    impact: str,
    event_date: str | None = None,
) -> str:
    key = "|".join(
        [
            story_hash or "",
            player.strip().lower(),
            impact.strip().lower(),
            event_date or "",
        ]
    )

    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def build_signal_event_hash_from_article(
    article: dict,
) -> str:
    story_hash = article.get("story_hash")

    if not story_hash:
        story_hash = hashlib.sha256(
            normalize_headline(
                article.get("headline", "")
            ).encode("utf-8")
        ).hexdigest()

    return build_signal_event_hash(
        story_hash=story_hash,
        player=article.get("player", "Unknown"),
        impact=article.get("fantasy_impact", "unknown"),
        event_date=article.get("date"),
    )
