from collections import defaultdict

from gridiron_gpt.data_ingest.news_loader import load_news
from gridiron_gpt.data_ingest.injury_loader import load_injuries
from gridiron_gpt.data_ingest.roster_loader import load_roster_moves
from gridiron_gpt.data_ingest.player_scores import IMPACT_SCORES


def _matches_player(item: dict, player_name: str) -> bool:
    return player_name.lower() in item.get("player", "").lower()


def _add_daily_signal(daily_scores, item, source):
    player = item.get("player", "Unknown")

    if player == "Unknown":
        return

    date = item.get("date", "unknown date")
    impact = item.get("fantasy_impact", "unknown").lower()
    value = IMPACT_SCORES.get(impact, 0.0)
    headline = item.get("headline", "No headline")

    existing = {
        signal["headline"]
        for signal in daily_scores[date]["signals"]
    }

    if headline in existing:
        return

    daily_scores[date]["score"] += value
    daily_scores[date]["signals"].append({
        "source": source,
        "headline": headline,
        "impact": impact,
        "value": value,
    })


def build_player_trend(player_name: str) -> str:
    daily_scores = defaultdict(lambda: {"score": 0.0, "signals": []})

    for item in load_news():
        if _matches_player(item, player_name):
            _add_daily_signal(daily_scores, item, "News")

    for item in load_injuries():
        if _matches_player(item, player_name):
            _add_daily_signal(daily_scores, item, "Injury")

    for item in load_roster_moves():
        if _matches_player(item, player_name):
            _add_daily_signal(daily_scores, item, "Roster")

    if not daily_scores:
        return f"No trend found for {player_name}."

    sorted_days = sorted(daily_scores.items())

    total_score = sum(day["score"] for _, day in sorted_days)
    first_score = sorted_days[0][1]["score"]
    last_score = sorted_days[-1][1]["score"]

    if len(sorted_days) == 1:
        direction = "Single-day signal"
    elif last_score > first_score:
        direction = "Rising 📈"
    elif last_score < first_score:
        direction = "Falling 📉"
    else:
        direction = "Flat ➖"

    lines = []
    lines.append(f"🏈 {player_name} Trend")
    lines.append("")
    lines.append(f"Total Score: {total_score:+.1f}")
    lines.append(f"Direction: {direction}")
    lines.append("")
    lines.append("Daily Signals")

    for date, data in sorted_days:
        lines.append("")
        lines.append(f"{date} — Score: {data['score']:+.1f}")

        for signal in sorted(data["signals"], key=lambda s: s["value"], reverse=True):
            value = signal["value"]
            prefix = "+" if value > 0 else ""
            lines.append(
                f"{prefix}{value:.1f} {signal['headline']} "
                f"[{signal['source']}; Impact: {signal['impact']}]"
            )

    return "\n".join(lines)
