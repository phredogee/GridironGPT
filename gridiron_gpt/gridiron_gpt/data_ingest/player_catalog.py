import json
from pathlib import Path

import nflreadpy as nfl

CATALOG_PATH = Path("data/player_catalog.json")


def build_player_aliases(
    player_name: str,
    team: str,
    position: str,
) -> list[str]:
    """
    Build deterministic aliases for player matching.
    """

    player_name = player_name.strip()

    if not player_name:
        return []

    team = (team or "").strip().upper()
    position = (position or "").strip().upper()

    aliases = {player_name}

    parts = player_name.split()

    if len(parts) >= 2:
        first = parts[0]
        last = parts[-1]

        aliases.add(f"{first[0]}. {last}")
        aliases.add(f"{first[0]} {last}")

        if position:
            aliases.add(f"{position} {last}")
            aliases.add(f"{position} {player_name}")

        if team:
            aliases.add(f"{team} {player_name}")

            if position:
                aliases.add(f"{team} {position} {last}")
                aliases.add(f"{team} {position} {player_name}")

    return sorted(
        aliases,
        key=lambda s: (len(s), s.casefold()),
        reverse=True,
    )


def build_player_catalog(
    catalog_path: Path = CATALOG_PATH,
) -> list[dict]:

    season = nfl.get_current_season()
    roster = nfl.load_rosters([season])

    players: dict[str, dict] = {}

    for row in roster.iter_rows(named=True):

        gsis_id = row.get("gsis_id")

        if not gsis_id:
            continue

        players[gsis_id] = {
            "player": row["full_name"],
            "team": row["team"],
            "position": row["position"],
            "gsis_id": gsis_id,
            "espn_id": row.get("espn_id"),
            "sleeper_id": row.get("sleeper_id"),
            "pfr_id": row.get("pfr_id"),
            "aliases": build_player_aliases(
                row["full_name"],
                row["team"],
                row["position"],
            ),
        }

    catalog = sorted(
        players.values(),
        key=lambda p: p["player"].casefold(),
    )

    catalog_path.parent.mkdir(parents=True, exist_ok=True)

    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)

    return catalog


def load_player_catalog(
    catalog_path: Path = CATALOG_PATH,
) -> list[dict]:

    if not catalog_path.exists():
        return build_player_catalog(catalog_path)

    with open(catalog_path, encoding="utf-8") as f:
        return json.load(f)
