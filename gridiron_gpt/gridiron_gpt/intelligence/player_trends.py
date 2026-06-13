from gridiron_gpt.storage.score_snapshot_repository import (
    get_player_score_history,
)


def get_player_trend(player: str) -> dict:
    history = get_player_score_history(player, limit=2)

    if not history:
        return {
            "player": player,
            "status": "no_history",
        }

    current = history[0]

    if len(history) == 1:
        return {
            "player": player,
            "current_score": current["adjusted_score"],
            "status": "first_snapshot",
        }

    previous = history[1]

    current_score = current["adjusted_score"]
    previous_score = previous["adjusted_score"]

    change = round(current_score - previous_score, 2)

    if change > 0:
        direction = "rising"
    elif change < 0:
        direction = "falling"
    else:
        direction = "stable"

    return {
        "player": player,
        "current_score": current_score,
        "previous_score": previous_score,
        "change": change,
        "direction": direction,
    }


def format_player_trend(player: str) -> str:
    trend = get_player_trend(player)

    if trend["status"] == "no_history":
        return f"No score history found for {player}."

    if trend["status"] == "first_snapshot":
        return (
            f"{player}\n"
            f"Current Score: {trend['current_score']}\n"
            f"Trend: First Snapshot"
        )

    return (
        f"{player}\n"
        f"Current Score: {trend['current_score']}\n"
        f"Previous Score: {trend['previous_score']}\n"
        f"Change: {trend['change']:+.2f}\n"
        f"Direction: {trend['direction'].upper()}"
    )
