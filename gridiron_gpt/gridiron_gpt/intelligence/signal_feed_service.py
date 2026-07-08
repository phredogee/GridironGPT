from gridiron_gpt.storage.supabase_client import get_supabase_client


def get_latest_signals(limit: int = 25) -> list[dict]:
    client = get_supabase_client()

    result = (
        client.table("signals")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return result.data


def get_latest_signals_by_type(
    signal_type: str,
    limit: int = 25,
) -> list[dict]:
    client = get_supabase_client()

    result = (
        client.table("signals")
        .select("*")
        .eq("signal_type", signal_type)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return result.data


def get_latest_signals_for_player(
    player: str,
    limit: int = 10,
) -> list[dict]:
    client = get_supabase_client()

    result = (
        client.table("signals")
        .select("*")
        .ilike("player", player)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return result.data


def format_latest_signals(limit: int = 15) -> str:
    signals = get_latest_signals(limit=limit)

    if not signals:
        return "No recent signals found."

    lines = []
    lines.append("📡 LATEST SIGNAL FEED")
    lines.append("")

    for signal in signals:
        lines.append(
            f"- [{signal.get('signal_type')}] "
            f"{signal.get('player')} ({signal.get('team') or 'UNK'}) "
            f"{signal.get('impact')} "
            f"{float(signal.get('value') or 0):+.2f} — "
            f"{signal.get('headline')}"
        )

    return "\n".join(lines)
