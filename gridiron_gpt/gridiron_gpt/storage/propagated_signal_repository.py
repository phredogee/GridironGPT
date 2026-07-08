from gridiron_gpt.storage.supabase_client import get_supabase_client


def save_propagated_signal(signal: dict) -> dict:
    """
    Save a propagated signal impact record.

    Expected signal fields may include:
    - source_player
    - affected_player
    - impact_score
    - reason
    - source_event_id
    - created_at
    """
    supabase = get_supabase_client()
    response = supabase.table("propagated_signals").insert(signal).execute()
    return response.data


def save_propagated_signals(signals: list[dict]) -> list[dict]:
    """
    Save multiple propagated signal records.
    """
    if not signals:
        return []

    supabase = get_supabase_client()
    response = supabase.table("propagated_signals").insert(signals).execute()
    return response.data


def get_propagated_signals_for_player(player_name: str, limit: int = 25) -> list[dict]:
    """
    Fetch propagated signals affecting a specific player.
    """
    supabase = get_supabase_client()
    response = (
        supabase.table("propagated_signals")
        .select("*")
        .eq("affected_player", player_name)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data
