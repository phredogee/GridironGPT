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

def _overall_trend(impacts: list[str]) -> str:
    cleaned = [(impact or "").lower() for impact in impacts]

    if "negative" in cleaned:
        return "⬇ Trending Down"
    if "monitor" in cleaned:
        return "⚠ Monitor"
    if "positive" in cleaned:
        return "⬆ Trending Up"

    return "• No clear trend"

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
    lines.append("Player Summary")

    player_cards = {}

    for item in news:
        key = (item.get("player", "Unknown"), item.get("team", "UNK"))
        player_cards.setdefault(key, {"news": [], "injuries": [], "roster": [], "impacts": []})
        player_cards[key]["news"].append(item.get("headline", "No headline"))
        player_cards[key]["impacts"].append(item.get("fantasy_impact", "unknown"))

    for item in injuries:
        key = (item.get("player", "Unknown"), item.get("team", "UNK"))
        player_cards.setdefault(key, {"news": [], "injuries": [], "roster": [], "impacts": []})
        player_cards[key]["injuries"].append(
            f"{item.get('headline', 'No headline')} "
            f"[Status: {item.get('status', 'unknown')}; Injury: {item.get('injury', 'unknown')}]"
        )
        player_cards[key]["impacts"].append(item.get("fantasy_impact", "monitor"))

    for item in roster_moves:
        key = (item.get("player", "Unknown"), item.get("team", "UNK"))
        player_cards.setdefault(key, {"news": [], "injuries": [], "roster": [], "impacts": []})
        player_cards[key]["roster"].append(
            f"{item.get('headline', 'No headline')} "
            f"[Movement: {item.get('movement', 'unknown')}]"
        )
        player_cards[key]["impacts"].append(item.get("fantasy_impact", "unknown"))

    if player_cards:
        for (player, team), card in player_cards.items():
            lines.append("")
            lines.append(f"{player} ({team})")
            lines.append(f"Fantasy Outlook: {_overall_trend(card['impacts'])}")

            if card["news"]:
                lines.append("News")
                for headline in card["news"]:
                    lines.append(f"- {headline}")

            if card["injuries"]:
                lines.append("Injuries")
                for injury in card["injuries"]:
                    lines.append(f"- {injury}")

            if card["roster"]:
                lines.append("Roster")
                for move in card["roster"]:
                    lines.append(f"- {move}")
    else:
        lines.append("- No player updates found.")

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
