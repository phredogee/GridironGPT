from gridiron_cortex.models.raw_event import RawEvent


def normalize_rss_item(item: dict) -> RawEvent:
    """
    Convert an RSS article into the canonical Cortex event.
    """

    return RawEvent(
        headline=item["headline"],
        source=item["source"],
        player=item.get("player"),
        team=item.get("team"),
        event_type=item.get("fantasy_impact"),
        published_at=item.get("date"),
        url=item.get("url"),
    )


def process_rss_items(
    items: list[dict],
    cortex,
):
    """
    Push RSS articles through Gridiron Cortex.
    """

    results = []

    for item in items:

        event = normalize_rss_item(item)

        result = cortex.process_event(event)

        results.append(result)

    return results
