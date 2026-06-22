from datetime import datetime, timezone
from typing import Optional

from gridiron_gpt.storage.supabase_client import get_supabase_client


def save_signal(
    player: str,
    value: float,
    source: str,
    team: Optional[str] = None,
    position: Optional[str] = None,
    headline: Optional[str] = None,
    signal_type: Optional[str] = None,
    impact: Optional[str] = None,
    confidence: float = 1.0,
    article_id: Optional[int] = None,
    event_date: Optional[str] = None,
    signal_event_hash: Optional[str] = None,
) -> dict:
    client = get_supabase_client()

    payload = {
        "player": player,
        "team": team,
        "position": position,
        "source": source,
        "headline": headline,
        "signal_type": signal_type,
        "impact": impact,
        "value": value,
        "confidence": confidence,
        "article_id": article_id,
        "event_date": event_date or datetime.now(timezone.utc).isoformat(),
        "signal_event_hash": signal_event_hash,
    }

    result = (
        client.table("signals")
        .upsert(payload, on_conflict="signal_event_hash")
        .execute()
    )

    return result.data[0]


def get_recent_signals(limit: int = 10) -> list[dict]:
    client = get_supabase_client()

    result = (
        client.table("signals")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return result.data


def get_player_signals(player: str, limit: int = 25) -> list[dict]:
    client = get_supabase_client()

    result = (
        client.table("signals")
        .select("*")
        .eq("player", player)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return result.data
