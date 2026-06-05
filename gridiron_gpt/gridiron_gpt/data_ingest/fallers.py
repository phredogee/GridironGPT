from collections import defaultdict

from gridiron_gpt.data_ingest.news_loader import load_news
from gridiron_gpt.data_ingest.roster_loader import load_roster_moves


def get_fallers():
    grouped = defaultdict(list)

    for item in load_news():
        if item.get("fantasy_impact", "").lower() == "negative":
            key = (item.get("player", "Unknown"), item.get("team", "UNK"))
            grouped[key].append(item.get("headline", "No headline"))

    for item in load_roster_moves():
        if item.get("fantasy_impact", "").lower() == "negative":
            key = (item.get("player", "Unknown"), item.get("team", "UNK"))
            grouped[key].append(item.get("headline", "No headline"))

    return grouped


def build_fallers_report() -> str:
    fallers = get_fallers()

    lines = []
    lines.append("⬇ CAMP FALLERS")
    lines.append("")

    if not fallers:
        lines.append("- No camp fallers found.")
        return "\n".join(lines)

    for (player, team), headlines in fallers.items():
        lines.append(f"{player} ({team})")
        for headline in headlines:
            lines.append(f"- {headline}")
        lines.append("Draft Outlook: Risk increasing. Monitor closely before moving up draft boards.")
        lines.append("")

    return "\n".join(lines).strip()
