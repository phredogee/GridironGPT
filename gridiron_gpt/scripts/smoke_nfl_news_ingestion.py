from collections import Counter
from pathlib import Path
import sys

# Allow this file to be executed directly from the repository root with:
#   python scripts/smoke_nfl_news_ingestion.py
# Python otherwise places scripts/ (rather than the project root) first on
# sys.path, which prevents the gridiron_gpt package from being resolved.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gridiron_gpt.ingestion.services.ingestion_service import (
    IngestionService,
)
from gridiron_gpt.ingestion.sources.nfl_news import (
    default_nfl_news_adapters,
)


FANTASY_SKILL_POSITIONS = {"QB", "RB", "WR", "TE"}


def main() -> None:
    service = IngestionService()
    adapters = default_nfl_news_adapters()

    events = service.ingest_many(adapters)

    by_source = Counter(event.source for event in events)
    resolved = [event for event in events if event.player]
    unresolved = [event for event in events if not event.player]

    fantasy_resolved = [
        event
        for event in resolved
        if (event.position or "").upper() in FANTASY_SKILL_POSITIONS
    ]
    other_resolved = [
        event
        for event in resolved
        if (event.position or "").upper() not in FANTASY_SKILL_POSITIONS
    ]

    players = Counter(
        event.player
        for event in resolved
        if event.player
    )
    positions = Counter(
        (event.position or "UNKNOWN").upper()
        for event in resolved
    )

    print("NFL news ingestion smoke test")
    print("=" * 32)
    print(f"total_events={len(events)}")
    print(f"resolved_events={len(resolved)}")
    print(f"fantasy_skill_resolved={len(fantasy_resolved)}")
    print(f"other_position_resolved={len(other_resolved)}")
    print(f"unresolved_events={len(unresolved)}")
    print()

    print("events_by_source")
    for source, count in sorted(by_source.items()):
        print(f"  {source}: {count}")

    print()
    print("resolved_by_position")
    for position, count in sorted(positions.items()):
        print(f"  {position}: {count}")

    print()
    print("top_resolved_players")
    for player, count in players.most_common(20):
        print(f"  {player}: {count}")

    if other_resolved:
        print()
        print("sample_non_fantasy_resolved")
        for event in other_resolved[:10]:
            print(
                f"  [{event.position or 'UNKNOWN'}] "
                f"{event.player}: {event.headline}"
            )

    if unresolved:
        print()
        print("sample_unresolved_headlines")
        for event in unresolved[:10]:
            print(f"  [{event.source}] {event.headline}")


if __name__ == "__main__":
    main()
