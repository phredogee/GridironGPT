import json
from datetime import date
from pathlib import Path

NEWS_PATH = Path("data/news")


def create_news_item(
    player: str,
    team: str,
    headline: str,
    source: str = "Manual Entry",
    fantasy_impact: str = "unknown",
) -> dict:
    return {
        "date": date.today().isoformat(),
        "player": player,
        "team": team.upper(),
        "headline": headline,
        "source": source,
        "fantasy_impact": fantasy_impact.lower(),
    }


def save_news_item(item: dict) -> Path:
    NEWS_PATH.mkdir(parents=True, exist_ok=True)

    file_path = NEWS_PATH / f"{item['date']}.json"

    if file_path.exists():
        with open(file_path) as f:
            items = json.load(f)
    else:
        items = []

    items.append(item)

    with open(file_path, "w") as f:
        json.dump(items, f, indent=2)

    return file_path
