from gridiron_gpt.storage.article_repository import save_raw_article
from gridiron_gpt.intelligence.signal_persistence import process_signal


IMPACT_VALUE_MAP = {
    "positive": 1.0,
    "neutral": 0.0,
    "unknown": 0.0,
    "monitor": -0.5,
    "negative": -1.0,
}


def persist_news_items(news_items: list[dict]) -> dict:
    articles_saved = 0
    signals_saved = 0
    skipped = 0

    for item in news_items:
        headline = item.get("headline")
        source = item.get("source", "unknown")
        url = item.get("url")
        event_date = item.get("date")
        player = item.get("player", "Unknown")
        team = item.get("team", "UNK")
        impact = item.get("fantasy_impact", "unknown")

        if not headline:
            skipped += 1
            continue

        article = save_raw_article(
            source=source,
            headline=headline,
            source_url=url,
            summary=None,
            published_at=event_date,
        )

        articles_saved += 1

        if player == "Unknown":
            skipped += 1
            continue

        value = IMPACT_VALUE_MAP.get(impact, 0.0)

        if value == 0.0:
            skipped += 1
            continue

        process_signal(
            player=player,
            team=team,
            source=source,
            headline=headline,
            signal_type="news",
            impact=impact,
            value=value,
            confidence=1.0,
            article_id=article["id"],
            event_date=event_date,
        )

        signals_saved += 1

    return {
        "articles_saved": articles_saved,
        "signals_saved": signals_saved,
        "skipped": skipped,
    }
