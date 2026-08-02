from collections import Counter

from gridiron_gpt.ingestion.services.ingestion_service import (
    IngestionService,
)
from gridiron_gpt.ingestion.sources.nfl_news import (
    default_nfl_news_adapters,
)


def main() -> None:
    service = IngestionService()
    adapters = default_nfl_news_adapters()

    events = service.ingest_many(adapters)

    by_source = Counter(event.source for event in events)
    resolved = [event for event in events if event.player]
    unresolved = [event for event in events if not event.player]
    players = Counter(
        event.player
        for event in resolved
        if event.player
    )

    print("NFL news ingestion smoke test")
    print("=" * 32)
    print(f"total_events={len(events)}")
    print(f"resolved_events={len(resolved)}")
    print(f"unresolved_events={len(unresolved)}")
    print()

    print("events_by_source")
    for source, count in sorted(by_source.items()):
        print(f"  {source}: {count}")

    print()
    print("top_resolved_players")
    for player, count in players.most_common(20):
        print(f"  {player}: {count}")

    if unresolved:
        print()
        print("sample_unresolved_headlines")
        for event in unresolved[:10]:
            print(f"  [{event.source}] {event.headline}")


if __name__ == "__main__":
    main()
