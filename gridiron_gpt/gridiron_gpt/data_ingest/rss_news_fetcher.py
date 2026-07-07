import json
import os
from datetime import date
from pathlib import Path

import feedparser

from gridiron_gpt.data_ingest.article_relevance import classify_article_relevance
from gridiron_gpt.data_ingest.news_persistence import persist_news_items
from gridiron_gpt.data_ingest.player_matcher import extract_players_from_text
from gridiron_gpt.intelligence.story_dedup import story_hash

NEWS_PATH = Path("data/news")


def _guess_impact(title: str, summary: str = "") -> str:
    text = f"{title} {summary}".lower()

    negative_terms = [
        "injury",
        "injured",
        "carted",
        "missed practice",
        "out",
        "doubtful",
        "suspended",
        "arrested",
        "domestic violence",
        "holdout",
        "setback",
        "released",
        "waived",
    ]

    monitor_terms = [
        "limited",
        "questionable",
        "day-to-day",
        "precaution",
        "contract talks",
        "not close",
        "uncertain",
        "competing",
    ]

    positive_terms = [
        "extension",
        "reach deal",
        "reworked deal",
        "signed",
        "first-team",
        "first team",
        "impressed",
        "standout",
        "breakout",
        "cleared",
        "returned",
        "activated",
        "healthy",
        "full participant",
    ]

    if any(term in text for term in negative_terms):
        return "negative"

    if any(term in text for term in monitor_terms):
        return "monitor"

    if any(term in text for term in positive_terms):
        return "positive"

    return "unknown"


def fetch_rss_news(feed_url: str, source: str = "RSS Feed") -> list[dict]:
    feed = feedparser.parse(feed_url)
    items = []

    for entry in feed.entries:
        title = entry.get("title", "No headline")
        summary = entry.get("summary", "")
        url = entry.get("link", "")

        text = f"{title} {summary}"
        matches = extract_players_from_text(text)
        fantasy_impact = _guess_impact(title, summary)

        if matches:
            for match in matches:
                items.append(
                    {
                        "date": date.today().isoformat(),
                        "player": match["player"],
                        "team": match["team"],
                        "position": match.get("position", "Unknown"),
                        "match_confidence": match.get("confidence", 1.0),
                        "matched_alias": match.get("matched_alias"),
                        "headline": title,
                        "source": source,

                        "story_hash": story_hash(
                            headline=title,
                            player=match["player"],
                            event_date=date.today().isoformat(),
                        ),

                        "fantasy_impact": fantasy_impact,
                        "article_relevance": classify_article_relevance(
                            title,
                            summary,
                            match["player"],
                        ),
                        "url": url,
                    }
                )
        else:
            items.append(
                {
                    "date": date.today().isoformat(),
                    "player": "Unknown",
                    "team": "UNK",
                    "position": "Unknown",
                    "match_confidence": 0.0,
                    "matched_alias": None,
                    "headline": title,
                    "source": source,

                    "story_hash": story_hash(
                        headline=title,
                        player="Unknown",
                        event_date=date.today().isoformat(),
                    ),

                    "fantasy_impact": fantasy_impact,
                    "article_relevance": classify_article_relevance(
                        title,
                        summary,
                        "Unknown",
                    ),
                    "url": url,
                }
            )

    return items


def save_rss_news(items: list[dict]) -> Path:
    NEWS_PATH.mkdir(parents=True, exist_ok=True)

    today_path = NEWS_PATH / f"{date.today().isoformat()}.json"

    existing_by_key = {}

    for file_path in NEWS_PATH.glob("*.json"):
        try:
            with open(file_path) as f:
                existing_items = json.load(f)
        except Exception:
            existing_items = []

        for item in existing_items:
            key = (
                item.get("headline", "").strip().lower(),
                item.get("url", "").strip().lower(),
            )
            existing_by_key[key] = item

    today_items = []

    if today_path.exists():
        with open(today_path) as f:
            today_items = json.load(f)

    today_keys = {
        (
            item.get("headline", "").strip().lower(),
            item.get("url", "").strip().lower(),
        )
        for item in today_items
    }

    for item in items:
        key = (
            item.get("headline", "").strip().lower(),
            item.get("url", "").strip().lower(),
        )

        if key in existing_by_key:
            continue

        if key in today_keys:
            continue

        today_items.append(item)
        today_keys.add(key)

    with open(today_path, "w") as f:
        json.dump(today_items, f, indent=2)

    return today_path


def fetch_and_save_from_env() -> tuple[int, Path]:
    feed_url = os.environ.get("GRIDIRON_RSS_URL")

    if not feed_url:
        raise RuntimeError("GRIDIRON_RSS_URL is not set.")

    source = os.environ.get("GRIDIRON_RSS_SOURCE", "RSS Feed")
    items = fetch_rss_news(feed_url, source=source)
    path = save_rss_news(items)

    return len(items), path

def get_rss_feeds_from_env() -> list[tuple[str, str]]:
    feeds_raw = os.environ.get("GRIDIRON_RSS_FEEDS")

    if feeds_raw:
        feeds = []

        for feed_config in feeds_raw.split(","):
            source, url = feed_config.split("|", 1)
            feeds.append((source.strip(), url.strip()))

        return feeds

    feed_url = os.environ.get("GRIDIRON_RSS_URL")

    if not feed_url:
        raise RuntimeError("GRIDIRON_RSS_URL or GRIDIRON_RSS_FEEDS is not set.")

    source = os.environ.get("GRIDIRON_RSS_SOURCE", "RSS Feed")
    return [(source, feed_url)]

def fetch_and_persist_from_env() -> dict:
    feeds = get_rss_feeds_from_env()

    combined_result = {
        "sources": [],
        "articles_found": 0,
        "articles_saved": 0,
        "signals_saved": 0,
        "skipped": 0,
        "items_fetched": 0,
    }

    for source, feed_url in feeds:
        items = fetch_rss_news(feed_url, source=source)

        result = persist_news_items(
            items,
            source_name=source,
        )

        combined_result["sources"].append({
            "source": source,
            "items_fetched": len(items),
            **result,
        })

        combined_result["articles_found"] += result.get("articles_found", 0)
        combined_result["articles_saved"] += result.get("articles_saved", 0)
        combined_result["signals_saved"] += result.get("signals_saved", 0)
        combined_result["skipped"] += result.get("skipped", 0)
        combined_result["items_fetched"] += len(items)

    return combined_result
