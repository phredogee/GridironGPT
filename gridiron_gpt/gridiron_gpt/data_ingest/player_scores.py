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


def _add_signal(scores, item, source):
    player = item.get("player", "Unknown")
    team = item.get("team", "UNK")

    if player == "Unknown":
        return

    impact = item.get("fantasy_impact", "unknown").lower()
    value = IMPACT_SCORES.get(impact, 0.0)

    key = (player, team)

    scores[key]["score"] += value
    scores[key]["signals"].append({
        "source": source,
        "headline": item.get("headline", "No headline"),
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
            lines.append(f"{player} ({team}) — Score: {data['score']:+.1f}")
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
