from pathlib import Path

from gridiron_cortex.facade import CortexFacade
from gridiron_cortex.intake.event_pipeline import process_rss_items
from gridiron_gpt.data_ingest.rss_news_fetcher import (
    fetch_rss_news,
    get_rss_feeds_from_env,
)
from gridiron_gpt.storage.unmatched_news_repository import (
    UnmatchedNewsRepository,
)

def run_cortex_rss_pipeline(
    data_directory: str | Path = "data/cortex",
) -> dict:
    cortex = CortexFacade(data_directory=data_directory)
    unmatched_repository = UnmatchedNewsRepository(
        Path(data_directory) / "unmatched_news.jsonl"
    )
    feeds = get_rss_feeds_from_env()

    summary = {
        "feeds_checked": 0,
        "items_fetched": 0,
        "items_processed": 0,
        "duplicates": 0,
        "unmatched_skipped": 0,
        "errors": [],
    }

    for source, feed_url in feeds:
        summary["feeds_checked"] += 1

        try:
            items = fetch_rss_news(
                feed_url=feed_url,
                source=source,
            )
        except Exception as exc:
            summary["errors"].append(
                {
                    "source": source,
                    "error": str(exc),
                }
            )
            continue

        summary["items_fetched"] += len(items)

        matched_items = []

        for item in items:
            player = item.get("player")

            if not player or player == "Unknown":
                unmatched_repository.save(item)
                summary["unmatched_skipped"] += 1
                continue

            matched_items.append(item)

        results = process_rss_items(
            items=matched_items,
            cortex=cortex,
        )

        for result in results:
            if result.explanation == "Duplicate event ignored.":
                summary["duplicates"] += 1
            else:
                summary["items_processed"] += 1

    return summary
