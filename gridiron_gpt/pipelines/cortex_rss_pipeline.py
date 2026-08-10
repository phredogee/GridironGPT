from pathlib import Path

from gridiron_cortex.facade import CortexFacade
from gridiron_cortex.intake.event_pipeline import process_rss_items
from gridiron_gpt.data_ingest.rss_news_fetcher import (
    fetch_rss_news,
    get_rss_feeds_from_env,
)
from gridiron_gpt.intelligence.story_dedup import are_duplicate_stories
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
        "matched_items": 0,
        "unmatched_skipped": 0,
        "items_processed": 0,
        "duplicates": 0,
        "batch_duplicates": 0,
        "persisted_duplicates": 0,
        "feed_breakdown": {},
        "errors": [],
    }

    all_matched_items: list[dict] = []

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

        summary["feed_breakdown"][source] = {
            "fetched": len(items),
            "matched": 0,
            "processed": 0,
            "duplicates": 0,
            "batch_duplicates": 0,
            "persisted_duplicates": 0,
            "unmatched": 0,
        }

        for item in items:
            player = item.get("player")

            if not player or player == "Unknown":
                unmatched_repository.save(item)

                summary["unmatched_skipped"] += 1
                summary["feed_breakdown"][source]["unmatched"] += 1
                continue

            all_matched_items.append(item)

            summary["matched_items"] += 1
            summary["feed_breakdown"][source]["matched"] += 1

    unique_items: list[dict] = []

    for item in all_matched_items:
        duplicate = next(
            (
                existing
                for existing in unique_items
                if are_duplicate_stories(
                    item,
                    existing,
                    threshold=0.80,
                )
            ),
            None,
        )

        if duplicate is not None:
            source = item.get("source", "Unknown")

            summary["duplicates"] += 1
            summary["batch_duplicates"] += 1

            if source in summary["feed_breakdown"]:
                summary["feed_breakdown"][source]["duplicates"] += 1
                summary["feed_breakdown"][source]["batch_duplicates"] += 1

            continue

        unique_items.append(item)

    results = process_rss_items(
        items=unique_items,
        cortex=cortex,
    )

    for item, result in zip(unique_items, results):
        source = item.get("source", "Unknown")

        if result.explanation == "Duplicate event ignored.":
            summary["duplicates"] += 1
            summary["persisted_duplicates"] += 1

            if source in summary["feed_breakdown"]:
                summary["feed_breakdown"][source]["duplicates"] += 1
                summary["feed_breakdown"][source]["persisted_duplicates"] += 1
        else:
            summary["items_processed"] += 1

            if source in summary["feed_breakdown"]:
                summary["feed_breakdown"][source]["processed"] += 1

    return summary
