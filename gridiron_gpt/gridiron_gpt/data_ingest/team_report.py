from collections import defaultdict

from gridiron_gpt.data_ingest.news_loader import load_news
from gridiron_gpt.data_ingest.injury_loader import load_injuries
from gridiron_gpt.data_ingest.roster_loader import load_roster_moves


TEAM_NAMES = {
    "ARI": "Arizona Cardinals",
    "ATL": "Atlanta Falcons",
    "BAL": "Baltimore Ravens",
    "BUF": "Buffalo Bills",
    "CAR": "Carolina Panthers",
    "CHI": "Chicago Bears",
    "CIN": "Cincinnati Bengals",
    "CLE": "Cleveland Browns",
    "DAL": "Dallas Cowboys",
    "DEN": "Denver Broncos",
    "DET": "Detroit Lions",
    "GB": "Green Bay Packers",
    "HOU": "Houston Texans",
    "IND": "Indianapolis Colts",
    "JAX": "Jacksonville Jaguars",
    "KC": "Kansas City Chiefs",
    "LAC": "Los Angeles Chargers",
    "LAR": "Los Angeles Rams",
    "LV": "Las Vegas Raiders",
    "MIA": "Miami Dolphins",
    "MIN": "Minnesota Vikings",
    "NE": "New England Patriots",
    "NO": "New Orleans Saints",
    "NYG": "New York Giants",
    "NYJ": "New York Jets",
    "PHI": "Philadelphia Eagles",
    "PIT": "Pittsburgh Steelers",
    "SEA": "Seattle Seahawks",
    "SF": "San Francisco 49ers",
    "TB": "Tampa Bay Buccaneers",
    "TEN": "Tennessee Titans",
    "WAS": "Washington Commanders",
}


def _team_matches(item: dict, team: str) -> bool:
    return item.get("team", "").upper() == team.upper()


def _trend_from_impacts(impacts: list[str]) -> str:
    cleaned = [(impact or "").lower() for impact in impacts]

    if "negative" in cleaned:
        return "⬇ Risk increasing"
    if "monitor" in cleaned:
        return "⚠ Monitor closely"
    if "positive" in cleaned:
        return "⬆ Positive momentum"

    return "• No clear movement"


def build_team_report(team: str) -> str:
    team = team.upper()
    team_name = TEAM_NAMES.get(team, team)

    news = [item for item in load_news() if _team_matches(item, team)]
    injuries = [item for item in load_injuries() if _team_matches(item, team)]
    roster_moves = [item for item in load_roster_moves() if _team_matches(item, team)]

    all_items = news + injuries + roster_moves

    lines = []
    lines.append(f"🏈 {team_name} Camp Report")
    lines.append("")

    if not all_items:
        lines.append(f"No camp updates found for {team}.")
        return "\n".join(lines)

    player_cards = defaultdict(lambda: {"news": [], "injuries": [], "roster": [], "impacts": []})

    for item in news:
        player = item.get("player", "Unknown")
        player_cards[player]["news"].append(item.get("headline", "No headline"))
        player_cards[player]["impacts"].append(item.get("fantasy_impact", "unknown"))

    for item in injuries:
        player = item.get("player", "Unknown")
        player_cards[player]["injuries"].append(
            f"{item.get('headline', 'No headline')} "
            f"[Status: {item.get('status', 'unknown')}; Injury: {item.get('injury', 'unknown')}]"
        )
        player_cards[player]["impacts"].append(item.get("fantasy_impact", "monitor"))

    for item in roster_moves:
        player = item.get("player", "Unknown")
        player_cards[player]["roster"].append(
            f"{item.get('headline', 'No headline')} "
            f"[Movement: {item.get('movement', 'unknown')}]"
        )
        player_cards[player]["impacts"].append(item.get("fantasy_impact", "unknown"))

    for player, card in sorted(player_cards.items()):
        lines.append(player)
        lines.append(f"Fantasy Outlook: {_trend_from_impacts(card['impacts'])}")

        if card["news"]:
            lines.append("News")
            for headline in card["news"]:
                lines.append(f"- {headline}")

        if card["injuries"]:
            lines.append("Injuries")
            for injury in card["injuries"]:
                lines.append(f"- {injury}")

        if card["roster"]:
            lines.append("Roster Moves")
            for move in card["roster"]:
                lines.append(f"- {move}")

        lines.append("")

    return "\n".join(lines).strip()
