from __future__ import annotations

from gridiron_gpt.ingestion.sources.rss import RSSSourceAdapter


class ESPNNFLNewsAdapter(RSSSourceAdapter):
    """ESPN NFL news feed adapter."""

    FEED_URL = "https://www.espn.com/espn/rss/nfl/news"

    def __init__(self):
        super().__init__(
            feed_url=self.FEED_URL,
            source_name="ESPN NFL",
        )


class RotoWireNFLNewsAdapter(RSSSourceAdapter):
    """RotoWire NFL player-news feed adapter."""

    FEED_URL = "https://www.rotowire.com/rss/news.php?sport=NFL"

    def __init__(self):
        super().__init__(
            feed_url=self.FEED_URL,
            source_name="RotoWire NFL",
        )


def default_nfl_news_adapters() -> list[RSSSourceAdapter]:
    """Return the default named NFL news sources for ingestion."""
    return [
        ESPNNFLNewsAdapter(),
        RotoWireNFLNewsAdapter(),
    ]
