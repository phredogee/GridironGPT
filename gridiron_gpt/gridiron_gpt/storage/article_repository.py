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


def _find_existing_article(
    client,
    *,
    story_hash: Optional[str],
    content_hash: str,
) -> Optional[dict]:
    """Return an existing article matched by either deduplication key."""
    if story_hash:
        result = (
            client.table("raw_articles")
            .select("*")
            .eq("story_hash", story_hash)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]

    result = (
        client.table("raw_articles")
        .select("*")
        .eq("content_hash", content_hash)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def save_raw_article(
    source: str,
    headline: str,
    source_url: Optional[str] = None,
    summary: Optional[str] = None,
    published_at: Optional[str] = None,
    story_hash: Optional[str] = None,
) -> dict:
    """Persist an article and report whether a new row was created.

    Duplicate story or content hashes are normal ingestion outcomes. Existing
    rows are returned with ``_created`` set to ``False`` so callers can skip
    downstream work without treating the duplicate as a failed run.
    """
    client = get_supabase_client()

    content_hash = build_content_hash(
        source=source,
        headline=headline,
        published_at=published_at,
    )

    existing = _find_existing_article(
        client,
        story_hash=story_hash,
        content_hash=content_hash,
    )
    if existing:
        return {**existing, "_created": False}

    payload = {
        "source": source,
        "source_url": source_url,
        "headline": headline,
        "summary": summary,
        "published_at": published_at,
        "story_hash": story_hash,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "content_hash": content_hash,
    }

    conflict_key = "story_hash" if story_hash else "content_hash"
    result = (
        client.table("raw_articles")
        .upsert(payload, on_conflict=conflict_key)
        .execute()
    )

    if result.data:
        return {**result.data[0], "_created": True}

    # Defensive fallback for a concurrent insert that won the race.
    existing = _find_existing_article(
        client,
        story_hash=story_hash,
        content_hash=content_hash,
    )
    if existing:
        return {**existing, "_created": False}

    raise RuntimeError("raw article persistence returned no row")


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
