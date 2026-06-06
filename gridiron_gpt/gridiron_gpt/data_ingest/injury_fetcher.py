import json
from datetime import date
from pathlib import Path

INJURY_PATH = Path("data/injuries")


def create_injury_item(
    player: str,
    team: str,
    headline: str,
    status: str = "unknown",
    injury: str = "unknown",
    fantasy_impact: str = "monitor",
) -> dict:
    return {
        "date": date.today().isoformat(),
        "player": player,
        "team": team.upper(),
        "headline": headline,
        "status": status.lower(),
        "injury": injury.lower(),
        "fantasy_impact": fantasy_impact.lower(),
    }


def save_injury_item(item: dict) -> Path:
    INJURY_PATH.mkdir(parents=True, exist_ok=True)

    file_path = INJURY_PATH / f"{item['date']}.json"

    if file_path.exists():
        with open(file_path) as f:
            items = json.load(f)
    else:
        items = []

    items.append(item)

    with open(file_path, "w") as f:
        json.dump(items, f, indent=2)

    return file_path
