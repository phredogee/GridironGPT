from gridiron_gpt.intelligence.momentum_engine import build_momentum_rankings
from gridiron_gpt.intelligence.signal_feed_service import (
    get_latest_signals,
    get_latest_signals_by_type,
)


def build_camp_digest(limit: int = 10) -> dict:
    momentum = build_momentum_rankings(limit=limit)

    latest_signals = get_latest_signals(limit=limit)
    injuries = get_latest_signals_by_type("injury", limit=limit)
    roster_moves = get_latest_signals_by_type("roster", limit=limit)
    news = get_latest_signals_by_type("news", limit=limit)

    return {
        "risers": momentum.get("risers", []),
        "fallers": momentum.get("fallers", []),
        "first_snapshots": momentum.get("first_snapshots", []),
        "injuries": injuries,
        "roster_moves": roster_moves,
        "news": news,
        "latest_signals": latest_signals,
    }


def format_signal_line(signal: dict) -> str:
    return (
        f"- {signal.get('player')} ({signal.get('team') or 'UNK'}) "
        f"[{signal.get('signal_type')}] "
        f"{signal.get('impact')} "
        f"{float(signal.get('value') or 0):+.2f} — "
        f"{signal.get('headline')}"
    )


def format_camp_digest(limit: int = 10) -> str:
    digest = build_camp_digest(limit=limit)

    lines = []
    lines.append("🏈 TRAINING CAMP INTELLIGENCE DIGEST")
    lines.append("")

    lines.append("🔥 Biggest Risers")
    if digest["risers"]:
        for item in digest["risers"]:
            lines.append(
                f"- {item['player']} ({item.get('team') or 'UNK'}): "
                f"{item['change']:+.2f}"
            )
    else:
        lines.append("- None yet")

    lines.append("")
    lines.append("📉 Biggest Fallers")
    if digest["fallers"]:
        for item in digest["fallers"]:
            lines.append(
                f"- {item['player']} ({item.get('team') or 'UNK'}): "
                f"{item['change']:+.2f}"
            )
    else:
        lines.append("- None yet")

    lines.append("")
    lines.append("🚑 Injury Watch")
    if digest["injuries"]:
        for signal in digest["injuries"][:limit]:
            lines.append(format_signal_line(signal))
    else:
        lines.append("- No recent injury signals")

    lines.append("")
    lines.append("📢 Roster Moves")
    if digest["roster_moves"]:
        for signal in digest["roster_moves"][:limit]:
            lines.append(format_signal_line(signal))
    else:
        lines.append("- No recent roster signals")

    lines.append("")
    lines.append("📰 News Signals")
    if digest["news"]:
        for signal in digest["news"][:limit]:
            lines.append(format_signal_line(signal))
    else:
        lines.append("- No recent news signals")

    lines.append("")
    lines.append("📡 Latest Signals")
    if digest["latest_signals"]:
        for signal in digest["latest_signals"][:limit]:
            lines.append(format_signal_line(signal))
    else:
        lines.append("- No recent signals")

    return "\n".join(lines)
