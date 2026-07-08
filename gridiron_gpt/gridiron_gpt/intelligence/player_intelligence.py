from gridiron_gpt.data_ingest.player_scores import (
    calculate_player_scores,
    confidence_from_signals,
    recommendation_from_score,
)
from gridiron_gpt.intelligence.player_trends import get_player_trend
from gridiron_gpt.intelligence.momentum_engine import calculate_player_momentum


def build_player_intelligence(player: str) -> dict:
    scores = calculate_player_scores()

    matched_key = None
    matched_data = None

    for (candidate_player, team), data in scores.items():
        if candidate_player.lower() == player.lower():
            matched_key = (candidate_player, team)
            matched_data = data
            break

    if matched_data is None:
        return {
            "player": player,
            "status": "not_found",
        }

    player_name, team = matched_key
    score = matched_data["score"]
    signals = matched_data["signals"]

    confidence = confidence_from_signals(signals)
    recommendation = recommendation_from_score(score)
    trend = get_player_trend(player_name)
    momentum = calculate_player_momentum(player_name)

    recent_signals = signals[-5:]

    return {
        "player": player_name,
        "team": team,
        "status": "ok",
        "score": round(score, 2),
        "recommendation": recommendation,
        "confidence": confidence,
        "trend": trend,
        "momentum": momentum,
        "recent_signals": recent_signals,
    }


def format_player_intelligence(player: str) -> str:
    intel = build_player_intelligence(player)

    if intel["status"] == "not_found":
        return f"No intelligence found for {player}."

    lines = []
    lines.append(f"🏈 PLAYER INTELLIGENCE: {intel['player']} ({intel['team']})")
    lines.append("")
    lines.append(f"Recommendation: {intel['recommendation']}")
    lines.append(f"Score: {intel['score']:+.2f}")
    lines.append(f"Confidence: {intel['confidence']}%")

    momentum = intel["momentum"]
    lines.append("")
    lines.append("Momentum:")
    lines.append(f"- Status: {momentum.get('status')}")
    lines.append(f"- Direction: {momentum.get('direction', 'n/a')}")
    lines.append(f"- Momentum Score: {momentum.get('momentum_score', 0):+.2f}")

    trend = intel["trend"]
    lines.append("")
    lines.append("Trend:")
    lines.append(f"- Status: {trend.get('status')}")
    if "change" in trend:
        lines.append(f"- Change: {trend['change']:+.2f}")

    lines.append("")
    lines.append("Recent Signals:")

    if intel["recent_signals"]:
        for signal in intel["recent_signals"]:
            lines.append(
                f"- [{signal.get('source')}] "
                f"{signal.get('impact')} "
                f"{signal.get('value'):+.2f}: "
                f"{signal.get('headline')}"
            )
    else:
        lines.append("- None")

    return "\n".join(lines)
