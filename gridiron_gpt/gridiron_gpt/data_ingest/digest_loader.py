from gridiron_gpt.data_ingest.news_loader import load_news
from gridiron_gpt.data_ingest.injury_loader import load_injuries
from gridiron_gpt.data_ingest.roster_loader import load_roster_moves

def _impact_icon(impact: str) -> str:
    impact = (impact or "").lower()

    if impact == "positive":
        return "⬆"
    if impact == "negative":
        return "⬇"
    if impact in {"monitor", "neutral", "unknown"}:
        return "⚠"

    return "•"

def build_digest() -> str:
    news = load_news()
    injuries = load_injuries()
    roster_moves = load_roster_moves()

    lines = []
    lines.append("🏈 DAILY CAMP DIGEST")
    lines.append("")
    
    lines.append("News")
    if news:
        for item in news:
            lines.append(
                f"- {item.get('player', 'Unknown')} ({item.get('team', 'UNK')}): "
                f"{item.get('headline', 'No headline')} "
                f"[Impact: {item.get('fantasy_impact', 'unknown')}]"
            )
    else:
        lines.append("- No news items found.")

    lines.append("")
    lines.append("Injuries")
    if injuries:
        for item in injuries:
            lines.append(
                f"- {item.get('player', 'Unknown')} ({item.get('team', 'UNK')}): "
                f"{item.get('headline', 'No headline')} "
                f"[Status: {item.get('status', 'unknown')}; Injury: {item.get('injury', 'unknown')}]"
            )
    else:
        lines.append("- No injury items found.")

    lines.append("")
    lines.append("Roster Moves")
    if roster_moves:
        for item in roster_moves:
            lines.append(
                f"- {item.get('player', 'Unknown')} ({item.get('team', 'UNK')}): "
                f"{item.get('headline', 'No headline')} "
                f"[Movement: {item.get('movement', 'unknown')}; Impact: {item.get('fantasy_impact', 'unknown')}]"
            )
    else:
        lines.append("- No roster moves found.")

    lines.append("")
    lines.append("Fantasy Movers")

    mover_items = []

    for item in news:
        mover_items.append({
            "player": item.get("player", "Unknown"),
            "team": item.get("team", "UNK"),
            "headline": item.get("headline", "No headline"),
            "impact": item.get("fantasy_impact", "unknown"),
            "source": "News",
        })

    for item in injuries:
        mover_items.append({
            "player": item.get("player", "Unknown"),
            "team": item.get("team", "UNK"),
            "headline": item.get("headline", "No headline"),
            "impact": item.get("fantasy_impact", "monitor"),
            "source": "Injury",
        })

    for item in roster_moves:
        mover_items.append({
            "player": item.get("player", "Unknown"),
            "team": item.get("team", "UNK"),
            "headline": item.get("headline", "No headline"),
            "impact": item.get("fantasy_impact", "unknown"),
            "source": "Roster",
        })

    if mover_items:
        for item in mover_items:
            icon = _impact_icon(item["impact"])
            lines.append(
                f"{icon} {item['player']} ({item['team']}) — "
                f"{item['headline']} "
                f"[{item['source']}; Impact: {item['impact']}]"
            )
    else:
        lines.append("- No fantasy movers found.")

    return "\n".join(lines)
