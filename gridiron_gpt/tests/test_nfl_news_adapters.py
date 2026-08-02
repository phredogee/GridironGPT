from gridiron_gpt.ingestion.sources.nfl_news import (
    ESPNNFLNewsAdapter,
    RotoWireNFLNewsAdapter,
    default_nfl_news_adapters,
)
from gridiron_gpt.ingestion.sources.rss import RSSSourceAdapter


def test_espn_adapter_uses_named_feed_configuration():
    adapter = ESPNNFLNewsAdapter()

    assert isinstance(adapter, RSSSourceAdapter)
    assert adapter.source_name == "ESPN NFL"
    assert adapter.feed_url == ESPNNFLNewsAdapter.FEED_URL


def test_rotowire_adapter_uses_named_feed_configuration():
    adapter = RotoWireNFLNewsAdapter()

    assert isinstance(adapter, RSSSourceAdapter)
    assert adapter.source_name == "RotoWire NFL"
    assert adapter.feed_url == RotoWireNFLNewsAdapter.FEED_URL


def test_default_nfl_news_adapters_are_stable_and_ordered():
    adapters = default_nfl_news_adapters()

    assert [adapter.source_name for adapter in adapters] == [
        "ESPN NFL",
        "RotoWire NFL",
    ]
    assert all(
        isinstance(adapter, RSSSourceAdapter)
        for adapter in adapters
    )
