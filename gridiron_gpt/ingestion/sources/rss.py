from __future__ import annotations

from urllib.parse import unquote, urlparse

import feedparser
import requests

from gridiron_gpt.data_ingest.player_matcher import (
    extract_players_from_text,
)
from gridiron_gpt.ingestion.models.source_record import (
    SourceRecord,
)
from gridiron_gpt.ingestion.sources.base import (
    SourceAdapter,
)


class RSSSourceAdapter(SourceAdapter):
    """
    Retrieve evidence from an RSS feed.

    The adapter performs provider retrieval, parsing, and player resolution only.
    It does not classify sentiment, fantasy impact, relevance, or recommendations.

    HTTP retrieval uses an explicit timeout so a slow or unavailable provider cannot
    leave a feedparser-owned network call hanging beyond the ingestion retry policy.
    """

    def __init__(
        self,
        feed_url: str,
        source_name: str = "RSS Feed",
        request_timeout_seconds: float = 8.0,
    ):
        if request_timeout_seconds <= 0:
            raise ValueError("request_timeout_seconds must be positive")

        self.feed_url = feed_url
        self._source_name = source_name
        self.request_timeout_seconds = request_timeout_seconds

    @property
    def source_name(self) -> str:
        return self._source_name

    def fetch(self) -> list[SourceRecord]:
        response = requests.get(
            self.feed_url,
            timeout=self.request_timeout_seconds,
            headers={
                "User-Agent": "GridironGPT/1.1 (+https://github.com/phredogee/GridironGPT)",
                "Accept": "application/rss+xml, application/xml, text/xml, */*",
            },
        )
        response.raise_for_status()

        feed = feedparser.parse(response.content)
        records: list[SourceRecord] = []

        for entry in feed.entries:
            records.extend(
                self._records_from_entry(entry)
            )

        return records

    def _records_from_entry(
        self,
        entry,
    ) -> list[SourceRecord]:
        headline = entry.get(
            "title",
            "No headline",
        )
        summary = entry.get(
            "summary",
            "",
        )
        url = entry.get(
            "link",
            "",
        )
        published_at = (
            entry.get("published")
            or entry.get("updated")
        )
        source_id = (
            entry.get("id")
            or entry.get("guid")
            or url
            or None
        )

        searchable_text = " ".join(
            part
            for part in (
                headline,
                summary,
                self._extract_url_text(url),
            )
            if part
        )

        matches = extract_players_from_text(
            searchable_text
        )

        shared_metadata = {
            "feed_url": self.feed_url,
            "article_source_id": source_id,
            "matched_player_count": len(matches),
        }

        if not matches:
            return [
                SourceRecord(
                    source=self.source_name,
                    headline=headline,
                    summary=summary or None,
                    published_at=published_at,
                    url=url or None,
                    source_id=source_id,
                    metadata=shared_metadata,
                )
            ]

        return [
            SourceRecord(
                source=self.source_name,
                headline=headline,
                summary=summary or None,
                published_at=published_at,
                url=url or None,
                source_id=source_id,
                player=match["player"],
                team=match.get("team"),
                position=match.get("position"),
                metadata={
                    **shared_metadata,
                    "match_confidence": match.get(
                        "confidence",
                    ),
                    "matched_alias": match.get(
                        "matched_alias",
                    ),
                },
            )
            for match in matches
        ]

    @staticmethod
    def _extract_url_text(url: str) -> str:
        if not url:
            return ""

        path = unquote(
            urlparse(url).path
        )

        normalized = (
            path
            .replace("-", " ")
            .replace("_", " ")
            .replace("/", " ")
        )

        return " ".join(
            token
            for token in normalized.split()
            if not token.isdigit()
        )
