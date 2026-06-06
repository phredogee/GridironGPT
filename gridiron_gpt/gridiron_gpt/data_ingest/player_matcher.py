PLAYER_TEAM_MAP = {
    "Tank Dell": {"team": "HOU", "aliases": ["Tank Dell", "Dell"]},
    "Joe Mixon": {"team": "HOU", "aliases": ["Joe Mixon", "Mixon"]},
    "Baker Mayfield": {"team": "TB", "aliases": ["Baker Mayfield", "Mayfield"]},
    "Christian Watson": {"team": "GB", "aliases": ["Christian Watson", "WR Watson", "Watson"]},
    "Jonathon Cooper": {"team": "DEN", "aliases": ["Jonathon Cooper", "LB Cooper", "Cooper"]},
}


def extract_player_and_team(text: str) -> tuple[str, str]:
    lowered = text.lower()

    for player, data in PLAYER_TEAM_MAP.items():
        for alias in data["aliases"]:
            if alias.lower() in lowered:
                return player, data["team"]

    return "Unknown", "UNK"
