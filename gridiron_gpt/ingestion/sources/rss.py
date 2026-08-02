from __future__ import annotations

from urllib.parse import unquote, urlparse

import feedparser

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

    The adapter performs provider parsing and player resolution only.
    It does not classify sentiment, fantasy impact, relevance, or
    recommendations.
    """

    def __init__(
        self,
        feed_url: str,
        source_name: str = "RSS Feed",
    ):
        self.feed_url = feed_url
        self._source_name = source_name

    @property
    def source_name(self) -> str:
        return self._source_name

    def fetch(self) -> list[SourceRecord]:
        feed = feedparser.parse(self.feed_url)
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

        if not matches:
            return [
                SourceRecord(
                    source=self.source_name,
                    headline=headline,
                    summary=summary or None,
                    published_at=published_at,
                    url=url or None,
                    metadata={
                        "feed_url": self.feed_url,
                    },
                )
            ]

        return [
            SourceRecord(
                source=self.source_name,
                headline=headline,
                summary=summary or None,
                published_at=published_at,
                url=url or None,
                player=match["player"],
                team=match.get("team"),
                position=match.get("position"),
                metadata={
                    "feed_url": self.feed_url,
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
