from gridiron_gpt.storage.article_repository import save_raw_article
from gridiron_gpt.intelligence.signal_persistence import process_signal
from gridiron_gpt.storage.ingestion_repository import (
    start_ingestion_run,
    finish_ingestion_run,
)

IMPACT_VALUE_MAP = {
    "positive": 1.0,
    "neutral": 0.0,
    "unknown": 0.0,
    "monitor": -0.5,
    "negative": -1.0,
}

def persist_news_items(news_items: list[dict], source_name: str = "news_json") -> dict:
    run_id = start_ingestion_run(source_name)

    articles_saved = 0
    signals_saved = 0
    skipped = 0
    skipped_no_headline = 0
    skipped_no_player = 0
    skipped_unknown_impact = 0
    skipped_zero_value = 0

    try:
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
                skipped_no_headline  += 1
                continue

            article = save_raw_article(
                source=source,
                headline=headline,
                source_url=url,
                summary=None,
                published_at=event_date,
                story_hash=item.get("story_hash"),
            )

            articles_saved += 1

            if player == "Unknown":
                skipped += 1
                skipped_no_player  += 1
                continue

            if impact == "unknown":
                skipped += 1
                skipped_unknown_impact += 1
                continue

            value = IMPACT_VALUE_MAP.get(impact, 0.0)

            if value == 0.0:
                skipped += 1
                skipped_zero_value += 1 
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

        finish_ingestion_run(
            run_id=run_id,
            status="success",
            articles_found=len(news_items),
            articles_new=articles_saved,
            articles_skipped=skipped,
        )

        return {
            "run_id": run_id,
            "status": "success",
            "articles_found": len(news_items),
            "articles_saved": articles_saved,
            "signals_saved": signals_saved,
            "skipped": skipped,
            "skipped_no_headline": skipped_no_headline,
            "skipped_no_player": skipped_no_player,
            "skipped_unknown_impact": skipped_unknown_impact,
            "skipped_zero_value": skipped_zero_value,
        }

    except Exception as exc:
        finish_ingestion_run(
            run_id=run_id,
            status="failed",
            articles_found=len(news_items),
            articles_new=articles_saved,
            articles_skipped=skipped,
            error_message=str(exc),
        )

        raise
