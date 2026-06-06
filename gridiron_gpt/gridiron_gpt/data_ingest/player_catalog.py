import json
import re
from pathlib import Path

DOCS_PATH = Path("data/index/gridiron_docs.json")
CATALOG_PATH = Path("data/player_catalog.json")


PLAYER_PATTERN = re.compile(
    r"^(?P<player>.+?) is a .+? \((?P<position>[A-Z]+)\) for .+? \((?P<team>[A-Z]+)\),"
)


def build_player_catalog(
    docs_path: Path = DOCS_PATH,
    catalog_path: Path = CATALOG_PATH,
) -> list[dict]:
    with open(docs_path) as f:
        docs = json.load(f)

    players = {}

    for doc in docs:
        match = PLAYER_PATTERN.search(doc)
        if not match:
            continue

        player = match.group("player").strip()
        team = match.group("team").strip()
        position = match.group("position").strip()

        players[player] = {
            "player": player,
            "team": team,
            "position": position,
            "aliases": [
                player,
            ],
        }

    catalog = sorted(players.values(), key=lambda item: item["player"])

    with open(catalog_path, "w") as f:
        json.dump(catalog, f, indent=2)

    return catalog


def load_player_catalog(catalog_path: Path = CATALOG_PATH) -> list[dict]:
    if not catalog_path.exists():
        return build_player_catalog(catalog_path=catalog_path)

    with open(catalog_path) as f:
        return json.load(f)
