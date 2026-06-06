import json
from datetime import date
from pathlib import Path

ROSTER_PATH = Path("data/roster_moves")


def create_roster_item(
    player: str,
    team: str,
    headline: str,
    movement: str = "unknown",
    fantasy_impact: str = "unknown",
) -> dict:
    return {
        "date": date.today().isoformat(),
        "player": player,
        "team": team.upper(),
        "headline": headline,
        "movement": movement.lower(),
        "fantasy_impact": fantasy_impact.lower(),
    }


def save_roster_item(item: dict) -> Path:
    ROSTER_PATH.mkdir(parents=True, exist_ok=True)

    file_path = ROSTER_PATH / f"{item['date']}.json"

    if file_path.exists():
        with open(file_path) as f:
            items = json.load(f)
    else:
        items = []

    items.append(item)

    with open(file_path, "w") as f:
        json.dump(items, f, indent=2)

    return file_path
