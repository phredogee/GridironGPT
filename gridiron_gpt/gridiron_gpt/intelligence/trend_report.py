from gridiron_gpt.storage.score_snapshot_repository import (
    get_recent_score_snapshots,
)
from gridiron_gpt.intelligence.player_trends import get_player_trend


def build_trend_report(limit: int = 10) -> str:
    recent = get_recent_score_snapshots(limit=100)

    seen_players = set()
    trends = []

    for row in recent:
        player = row["player"]

        if player in seen_players:
            continue

        seen_players.add(player)
        trend = get_player_trend(player)

        if trend.get("status") == "no_history":
            continue

        trends.append(trend)

    rising = [
        trend for trend in trends
        if trend.get("direction") == "rising"
    ]

    falling = [
        trend for trend in trends
        if trend.get("direction") == "falling"
    ]

    first_snapshots = [
        trend for trend in trends
        if trend.get("status") == "first_snapshot"
    ]

    rising.sort(key=lambda item: item.get("change", 0), reverse=True)
    falling.sort(key=lambda item: item.get("change", 0))

    lines = []
    lines.append("📈 PLAYER TREND REPORT")
    lines.append("")

    lines.append("🔥 Risers")
    if rising:
        for trend in rising[:limit]:
            lines.append(
                f"- {trend['player']}: "
                f"{trend['previous_score']} → {trend['current_score']} "
                f"({trend['change']:+.2f})"
            )
    else:
        lines.append("- None yet")

    lines.append("")
    lines.append("🧊 Fallers")
    if falling:
        for trend in falling[:limit]:
            lines.append(
                f"- {trend['player']}: "
                f"{trend['previous_score']} → {trend['current_score']} "
                f"({trend['change']:+.2f})"
            )
    else:
        lines.append("- None yet")

    lines.append("")
    lines.append("🆕 First Snapshots")
    if first_snapshots:
        for trend in first_snapshots[:limit]:
            lines.append(
                f"- {trend['player']}: {trend['current_score']}"
            )
    else:
        lines.append("- None")

    return "\n".join(lines)
