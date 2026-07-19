"""Cortex Observe faculty.

Acquires raw information from feeds, APIs, documents, reports, and event
streams, then prepares that information for the Understand faculty.
"""

from gridiron_cortex.observe.event_pipeline import (
    normalize_rss_item,
    process_rss_items,
)

__all__ = [
    "normalize_rss_item",
    "process_rss_items",
]
