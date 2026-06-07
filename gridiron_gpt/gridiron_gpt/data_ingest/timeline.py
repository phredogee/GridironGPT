from collections import defaultdict

from gridiron_gpt.data_ingest.news_loader import load_news
from gridiron_gpt.data_ingest.injury_loader import load_injuries
from gridiron_gpt.data_ingest.roster_loader import load_roster_moves


def _matches_player(item: dict, player_name: str) -> bool:
    return player_name.lower() in item.get("player", "").lower()


def build_player_timeline(player_name: str) -> str:
    events = defaultdict(list)

    for item in load_news():
        if _matches_player(item, player_name):
            events[item.get("date", "unknown date")].append(
                ("NEWS", item.get("headline", "No headline"))
            )

    for item in load_injuries():
        if _matches_player(item, player_name):
            events[item.get("date", "unknown date")].append(
                (
                    "INJURY",
                    f"{item.get('headline', 'No headline')} "
                    f"[Status: {item.get('status', 'unknown')}; Injury: {item.get('injury', 'unknown')}]",
                )
            )

    for item in load_roster_moves():
        if _matches_player(item, player_name):
            events[item.get("date", "unknown date")].append(
                (
                    "ROSTER",
                    f"{item.get('headline', 'No headline')} "
                    f"[Movement: {item.get('movement', 'unknown')}]",
                )
            )

    if not events:
        return f"No timeline found for {player_name}."

    lines = []
    lines.append(f"🏈 {player_name} Timeline")
    lines.append("")

    for event_date in sorted(events):
        lines.append(event_date)

        for category, headline in events[event_date]:
            lines.append(f"{category}")
            lines.append(f"- {headline}")

        lines.append("")

    return "\n".join(lines).strip()
