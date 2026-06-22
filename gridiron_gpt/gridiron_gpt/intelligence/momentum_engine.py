from gridiron_gpt.storage.score_snapshot_repository import (
    get_recent_score_snapshots,
    get_player_score_history,
)


def calculate_player_momentum(player: str, limit: int = 7) -> dict:
    history = get_player_score_history(player, limit=limit)

    if not history:
        return {
            "player": player,
            "status": "no_history",
            "momentum_score": 0.0,
        }

    if len(history) == 1:
        current = history[0]

        return {
            "player": player,
            "team": current.get("team"),
            "current_score": current.get("adjusted_score"),
            "status": "first_snapshot",
            "momentum_score": 0.0,
        }

    current = history[0]
    previous = history[-1]

    current_score = float(current.get("adjusted_score") or current.get("score") or 0.0)
    previous_score = float(previous.get("adjusted_score") or previous.get("score") or 0.0)

    change = round(current_score - previous_score, 3)
    periods = max(1, len(history) - 1)
    velocity = round(change / periods, 3)

    if change > 0:
        direction = "rising"
    elif change < 0:
        direction = "falling"
    else:
        direction = "stable"

    return {
        "player": player,
        "team": current.get("team"),
        "current_score": current_score,
        "previous_score": previous_score,
        "change": change,
        "velocity": velocity,
        "direction": direction,
        "momentum_score": velocity,
        "snapshots_used": len(history),
        "status": "ok",
    }


def build_momentum_rankings(limit: int = 10) -> dict:
    recent = get_recent_score_snapshots(limit=200)

    seen_players = set()
    momentum_items = []

    for row in recent:
        player = row["player"]

        if player in seen_players:
            continue

        seen_players.add(player)

        momentum = calculate_player_momentum(player)

        if momentum["status"] == "no_history":
            continue

        momentum_items.append(momentum)

    risers = [
        item for item in momentum_items
        if item.get("direction") == "rising"
    ]

    fallers = [
        item for item in momentum_items
        if item.get("direction") == "falling"
    ]

    first_snapshots = [
        item for item in momentum_items
        if item.get("status") == "first_snapshot"
    ]

    risers.sort(key=lambda item: item.get("momentum_score", 0), reverse=True)
    fallers.sort(key=lambda item: item.get("momentum_score", 0))

    return {
        "risers": risers[:limit],
        "fallers": fallers[:limit],
        "first_snapshots": first_snapshots[:limit],
    }


def format_momentum_report(limit: int = 10) -> str:
    rankings = build_momentum_rankings(limit=limit)

    lines = []
    lines.append("🚀 MOMENTUM REPORT")
    lines.append("")

    lines.append("🔥 Top Risers")
    if rankings["risers"]:
        for item in rankings["risers"]:
            lines.append(
                f"- {item['player']} ({item.get('team') or 'UNK'}): "
                f"{item['previous_score']:+.2f} → {item['current_score']:+.2f} "
                f"({item['change']:+.2f}, velocity {item['velocity']:+.2f})"
            )
    else:
        lines.append("- None yet")

    lines.append("")
    lines.append("🧊 Top Fallers")
    if rankings["fallers"]:
        for item in rankings["fallers"]:
            lines.append(
                f"- {item['player']} ({item.get('team') or 'UNK'}): "
                f"{item['previous_score']:+.2f} → {item['current_score']:+.2f} "
                f"({item['change']:+.2f}, velocity {item['velocity']:+.2f})"
            )
    else:
        lines.append("- None yet")

    lines.append("")
    lines.append("🆕 First Snapshots")
    if rankings["first_snapshots"]:
        for item in rankings["first_snapshots"]:
            lines.append(
                f"- {item['player']} ({item.get('team') or 'UNK'}): "
                f"{float(item.get('current_score') or 0):+.2f}"
            )
    else:
        lines.append("- None")

    return "\n".join(lines)
