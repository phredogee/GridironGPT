import json
import os
from datetime import date
from pathlib import Path
from gridiron_gpt.data_ingest.player_matcher import extract_player_and_team

import feedparser

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

        player, team = extract_player_and_team(title)

        items.append({
            "date": date.today().isoformat(),
            "player": player,
            "team": team,
            "headline": title,
            "source": source,
            "fantasy_impact": _guess_impact(title, summary),
            "url": entry.get("link", ""),
        })

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
