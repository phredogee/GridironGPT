from collections import defaultdict

from gridiron_gpt.data_ingest.news_loader import load_news
from gridiron_gpt.data_ingest.injury_loader import load_injuries
from gridiron_gpt.data_ingest.roster_loader import load_roster_moves


IMPACT_SCORES = {
    "positive": 1.0,
    "neutral": 0.0,
    "unknown": 0.0,
    "monitor": -0.5,
    "negative": -1.0,
}

def recommendation_from_score(score: float) -> str:
    if score >= 2:
        return "BUY"

    if score > 0:
        return "WATCH"

    if score == 0:
        return "HOLD"

    if score > -1:
        return "MONITOR"

    return "SELL"

def _add_signal(scores, item, source):
    player = item.get("player", "Unknown")
    team = item.get("team", "UNK")

    if player == "Unknown":
        return

    impact = item.get("fantasy_impact", "unknown").lower()
    value = IMPACT_SCORES.get(impact, 0.0)

    key = (player, team)
    headline = item.get("headline", "No headline")

    existing_headlines = {
        signal["headline"]
        for signal in scores[key]["signals"]
    }

    if headline in existing_headlines:
        return

    scores[key]["score"] += value
    scores[key]["signals"].append({
        "source": source,
        "headline": headline,
        "impact": impact,
        "value": value,
    })

def calculate_player_scores():
    scores = defaultdict(lambda: {"score": 0.0, "signals": []})

    for item in load_news():
        _add_signal(scores, item, "News")

    for item in load_injuries():
        _add_signal(scores, item, "Injury")

    for item in load_roster_moves():
        _add_signal(scores, item, "Roster")

    return scores


def build_draft_watch_report() -> str:
    scores = calculate_player_scores()

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1]["score"],
        reverse=True,
    )

    risers = [(key, data) for key, data in ranked if data["score"] > 0]
    fallers = [(key, data) for key, data in ranked if data["score"] < 0]

    lines = []
    lines.append("📈 DRAFT WATCH")
    lines.append("")

    lines.append("🔥 Biggest Risers")
    if risers:
        for (player, team), data in risers[:10]:
            rating = recommendation_from_score(data["score"])

            lines.append(
                f"{player} ({team}) — "
                f"Score: {data['score']:+.1f} "
                f"[{rating}]"
            )

            for signal in data["signals"][:3]:
                if signal["value"] > 0:
                    lines.append(f"+ {signal['headline']} [{signal['source']}]")
            lines.append("")
    else:
        lines.append("- No risers found.")
        lines.append("")

    lines.append("⚠ Biggest Concerns")
    if fallers:
        for (player, team), data in fallers[:10]:
            lines.append(f"{player} ({team}) — Score: {data['score']:+.1f}")
            for signal in data["signals"][:3]:
                if signal["value"] < 0:
                    lines.append(f"- {signal['headline']} [{signal['source']}]")
            lines.append("")
    else:
        lines.append("- No concerns found.")

    return "\n".join(lines).strip()

def build_player_scorecard(player_name: str) -> str:
    scores = calculate_player_scores()

    matched_key = None
    matched_data = None

    for (player, team), data in scores.items():
        if player_name.lower() in player.lower():
            matched_key = (player, team)
            matched_data = data
            break

    if not matched_key or not matched_data:
        return f"No scorecard found for {player_name}."

    player, team = matched_key
    score = matched_data["score"]
    signals = matched_data["signals"]

    recommendation = recommendation_from_score(score)

    lines = []
    lines.append(f"🏈 {player} Scorecard")
    lines.append("")
    lines.append(f"Team: {team}")
    lines.append(f"Current Score: {score:+.1f}")
    lines.append(f"Recommendation: {recommendation}")
    lines.append("")
    lines.append("Signals")

    for signal in sorted(signals, key=lambda s: s["value"], reverse=True):
        value = signal["value"]
        prefix = "+" if value > 0 else ""
        lines.append(
            f"{prefix}{value:.1f}  {signal['headline']} "
            f"[{signal['source']}; Impact: {signal['impact']}]"
        )

    return "\n".join(lines)

def build_signal_rankings(limit: int = 25) -> str:
    scores = calculate_player_scores()

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1]["score"],
        reverse=True,
    )

    ranked = [
        ((player, team), data)
        for (player, team), data in ranked
        if data["score"] != 0
    ]

    lines = []
    lines.append("🏆 SIGNAL RANKINGS")
    lines.append("")

    if not ranked:
        lines.append("- No scored players found.")
        return "\n".join(lines)

    for idx, ((player, team), data) in enumerate(ranked[:limit], start=1):
        rating = recommendation_from_score(data["score"])
        lines.append(
            f"{idx}. {player} ({team}) — "
            f"Score: {data['score']:+.1f} [{rating}]"
        )

    return "\n".join(lines)
