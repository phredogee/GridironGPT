"""Deprecated compatibility package.

Use :mod:`gridiron_cortex.observe` for new code.
"""

from gridiron_cortex.observe import (
    normalize_rss_item,
    process_rss_items,
)

__all__ = [
    "normalize_rss_item",
    "process_rss_items",
]
