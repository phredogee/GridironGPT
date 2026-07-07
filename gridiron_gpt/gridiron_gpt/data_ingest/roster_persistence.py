from gridiron_gpt.intelligence.signal_event_hash import (
    build_signal_event_hash_from_article,
)
from gridiron_gpt.intelligence.signal_persistence import process_signal


ROSTER_VALUE_MAP = {
    "positive": 1.0,
    "monitor": -0.5,
    "negative": -1.0,
    "unknown": 0.0,
}


def persist_roster_items(roster_items: list[dict]) -> dict:
    signals_saved = 0
    skipped = 0

    for item in roster_items:
        player = item.get("player", "Unknown")
        team = item.get("team", "UNK")
        headline = item.get("headline")
        impact = item.get("fantasy_impact", "unknown")
        event_date = item.get("date")

        if player == "Unknown" or not headline:
            skipped += 1
            continue

        value = ROSTER_VALUE_MAP.get(impact, 0.0)

        if value == 0.0:
            skipped += 1
            continue

        signal_event_hash = build_signal_event_hash_from_article(item)

        process_signal(
            player=player,
            team=team,
            source="roster_loader",
            headline=headline,
            signal_type="roster",
            impact=impact,
            value=value,
            confidence=1.0,
            event_date=event_date,
            signal_event_hash=signal_event_hash,
        )

        signals_saved += 1

    return {
        "signals_saved": signals_saved,
        "skipped": skipped,
    }
