import hashlib
from datetime import datetime, timezone
from typing import Optional

from gridiron_gpt.storage.supabase_client import get_supabase_client


def build_content_hash(
    source: str,
    headline: str,
    published_at: Optional[str] = None,
) -> str:
    normalized = "|".join(
        [
            source.strip().lower(),
            headline.strip().lower(),
            published_at.strip() if published_at else "",
        ]
    )

    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def save_raw_article(
    source: str,
    headline: str,
    source_url: Optional[str] = None,
    summary: Optional[str] = None,
    published_at: Optional[str] = None,
) -> dict:
    client = get_supabase_client()

    content_hash = build_content_hash(
        source=source,
        headline=headline,
        published_at=published_at,
    )

    payload = {
        "source": source,
        "source_url": source_url,
        "headline": headline,
        "summary": summary,
        "published_at": published_at,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "content_hash": content_hash,
    }

    result = (
        client.table("raw_articles")
        .upsert(payload, on_conflict="content_hash")
        .execute()
    )

    return result.data[0]


def get_recent_articles(limit: int = 10) -> list[dict]:
    client = get_supabase_client()

    result = (
        client.table("raw_articles")
        .select("*")
        .order("fetched_at", desc=True)
        .limit(limit)
        .execute()
    )

    return result.data
