from collections import defaultdict

from gridiron_gpt.data_ingest.news_loader import load_news
from gridiron_gpt.data_ingest.roster_loader import load_roster_moves


def get_risers():
    grouped = defaultdict(list)

    for item in load_news():
        if item.get("fantasy_impact", "").lower() == "positive":
            key = (item.get("player", "Unknown"), item.get("team", "UNK"))
            grouped[key].append(item.get("headline", "No headline"))

    for item in load_roster_moves():
        if item.get("fantasy_impact", "").lower() == "positive":
            key = (item.get("player", "Unknown"), item.get("team", "UNK"))
            grouped[key].append(item.get("headline", "No headline"))

    return grouped


def build_risers_report() -> str:
    risers = get_risers()

    lines = []
    lines.append("⬆ CAMP RISERS")
    lines.append("")

    if not risers:
        lines.append("- No camp risers found.")
        return "\n".join(lines)

    for (player, team), headlines in risers.items():
        lines.append(f"{player} ({team})")
        for headline in headlines:
            lines.append(f"- {headline}")
        lines.append("Draft Outlook: Trending up. Monitor for repeated positive reports.")
        lines.append("")

    return "\n".join(lines).strip()
