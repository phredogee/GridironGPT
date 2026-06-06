from gridiron_gpt.data_ingest.player_catalog import load_player_catalog


MANUAL_ALIASES = {
    "Christian Watson": ["WR Watson"],
    "Jonathon Cooper": ["LB Cooper"],
}


def extract_player_and_team(text: str) -> tuple[str, str]:
    lowered = text.lower()
    catalog = load_player_catalog()

    for item in catalog:
        player = item["player"]
        team = item["team"]
        aliases = item.get("aliases", [])

        aliases.extend(MANUAL_ALIASES.get(player, []))

        for alias in aliases:
            if alias.lower() in lowered:
                return player, team

    return "Unknown", "UNK"
