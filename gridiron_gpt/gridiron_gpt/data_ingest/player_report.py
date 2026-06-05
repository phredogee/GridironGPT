from gridiron_gpt.data_ingest.news_loader import load_news
from gridiron_gpt.data_ingest.injury_loader import load_injuries
from gridiron_gpt.data_ingest.roster_loader import load_roster_moves


def _matches_player(item: dict, player_name: str) -> bool:
    return player_name.lower() in item.get("player", "").lower()


def _overall_trend(impacts: list[str]) -> str:
    cleaned = [(impact or "").lower() for impact in impacts]

    if "negative" in cleaned:
        return "⬇ Trending Down"
    if "monitor" in cleaned:
        return "⚠ Monitor"
    if "positive" in cleaned:
        return "⬆ Trending Up"

    return "• No clear trend"


def build_player_report(player_name: str) -> str:
    news = [item for item in load_news() if _matches_player(item, player_name)]
    injuries = [item for item in load_injuries() if _matches_player(item, player_name)]
    roster_moves = [item for item in load_roster_moves() if _matches_player(item, player_name)]

    all_items = news + injuries + roster_moves
    if not all_items:
        return f"No camp report found for {player_name}."

    player = all_items[0].get("player", player_name)
    team = all_items[0].get("team", "UNK")

    impacts = [item.get("fantasy_impact", "unknown") for item in all_items]

    lines = []
    lines.append(f"🏈 {player} ({team})")
    lines.append("")
    lines.append(f"Fantasy Outlook: {_overall_trend(impacts)}")
    lines.append("")

    if news:
        lines.append("News")
        for item in news:
            lines.append(f"- {item.get('headline', 'No headline')} [Impact: {item.get('fantasy_impact', 'unknown')}]")
        lines.append("")

    if injuries:
        lines.append("Injuries")
        for item in injuries:
            lines.append(
                f"- {item.get('headline', 'No headline')} "
                f"[Status: {item.get('status', 'unknown')}; Injury: {item.get('injury', 'unknown')}]"
            )
        lines.append("")

    if roster_moves:
        lines.append("Roster")
        for item in roster_moves:
            lines.append(
                f"- {item.get('headline', 'No headline')} "
                f"[Movement: {item.get('movement', 'unknown')}; Impact: {item.get('fantasy_impact', 'unknown')}]"
            )

    return "\n".join(lines).strip()
