from datetime import date
from typing import Optional

from gridiron_gpt.storage.supabase_client import get_supabase_client


def save_player_score_snapshot(
    player: str,
    score: float,
    snapshot_date: Optional[str] = None,
    team: Optional[str] = None,
    adjusted_score: Optional[float] = None,
    confidence: Optional[int] = None,
    recommendation: Optional[str] = None,
) -> dict:
    client = get_supabase_client()

    payload = {
        "player": player,
        "team": team,
        "score": score,
        "adjusted_score": adjusted_score,
        "confidence": confidence,
        "recommendation": recommendation,
        "snapshot_date": snapshot_date or date.today().isoformat(),
    }

    result = (
        client.table("player_score_snapshots")
        .insert(payload)
        .execute()
    )

    return result.data[0]


def get_player_score_history(
    player: str,
    limit: int = 30,
) -> list[dict]:
    client = get_supabase_client()

    result = (
        client.table("player_score_snapshots")
        .select("*")
        .eq("player", player)
        .order("snapshot_date", desc=True)
        .limit(limit)
        .execute()
    )

    return result.data


def get_recent_score_snapshots(limit: int = 50) -> list[dict]:
    client = get_supabase_client()

    result = (
        client.table("player_score_snapshots")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return result.data
