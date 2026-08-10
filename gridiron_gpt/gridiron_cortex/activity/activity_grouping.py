from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from gridiron_cortex.activity.activity_models import ActivityCard, ActivityGroup
from gridiron_cortex.events.event_types import CortexEventType


def group_activity(cards: Iterable[ActivityCard]) -> tuple[ActivityGroup, ...]:
    grouped: dict[str, list[ActivityCard]] = defaultdict(list)
    for card in cards:
        grouped[card.correlation_id].append(card)

    results: list[ActivityGroup] = []
    for correlation_id, items in grouped.items():
        ordered = sorted(items, key=lambda card: card.timestamp)
        article = next(
            (
                card
                for card in ordered
                if card.event_type == CortexEventType.ARTICLE_RECEIVED
            ),
            None,
        )
        headline = (
            article.subtitle
            if article is not None
            else ordered[0].entity_name
            or ordered[0].subtitle
        )
        entity_name = next(
            (card.entity_name for card in ordered if card.entity_name),
            None,
        )
        source = next((card.source for card in ordered if card.source), None)
        results.append(
            ActivityGroup(
                correlation_id=correlation_id,
                headline=headline,
                timestamp=ordered[0].timestamp,
                cards=tuple(ordered),
                source=source,
                entity_name=entity_name,
            )
        )

    return tuple(
        sorted(results, key=lambda group: group.latest_timestamp, reverse=True)
    )
