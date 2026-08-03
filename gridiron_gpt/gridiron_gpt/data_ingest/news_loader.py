import json
from pathlib import Path

from gridiron_gpt.storage.signal_repository import get_scoring_signals

NEWS_PATH = Path("data/news")


def _load_local_news() -> list[dict]:
    items: list[dict] = []

    for file in NEWS_PATH.glob("*.json"):
        try:
            with open(file, encoding="utf-8") as handle:
                items.extend(json.load(handle))
        except Exception as exc:
            print(f"⚠️ Failed loading {file}: {exc}")

    return items


def _load_persisted_news() -> list[dict]:
    """Adapt persisted direct signals to the legacy news-item shape."""
    try:
        signals = get_scoring_signals()
    except Exception as exc:
        # Local-only development and tests must continue to work when
        # Supabase is not configured or temporarily unavailable.
        print(f"⚠️ Failed loading persisted signals: {exc}")
        return []

    return [
        {
            "player": signal.get("player") or "Unknown",
            "team": signal.get("team") or "UNK",
            "position": signal.get("position") or "Unknown",
            "headline": signal.get("headline") or "No headline",
            "source": signal.get("source") or "Persisted Signal",
            "fantasy_impact": signal.get("impact") or "unknown",
            "date": signal.get("event_date") or signal.get("created_at"),
            "signal_event_hash": signal.get("signal_event_hash"),
            "confidence": signal.get("confidence", 1.0),
        }
        for signal in signals
        if signal.get("player")
    ]


def _dedupe_news(items: list[dict]) -> list[dict]:
    deduped: list[dict] = []
    seen: set[tuple[str, str, str]] = set()

    for item in items:
        key = (
            str(item.get("player") or "Unknown").strip().lower(),
            str(item.get("headline") or "").strip().lower(),
            str(item.get("date") or "").strip(),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    return deduped


def load_news() -> list[dict]:
    """Load local news plus live signals persisted in Supabase."""
    return _dedupe_news(_load_local_news() + _load_persisted_news())
