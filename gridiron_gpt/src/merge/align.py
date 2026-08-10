from typing import Any


def _index_bios(
    bios: list[dict[str, Any]] | dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Normalize biography records into a lookup dictionary."""
    indexed: dict[str, dict[str, Any]] = {}

    if isinstance(bios, dict):
        for key, value in bios.items():
            if isinstance(value, dict):
                indexed[str(key)] = value

                player_id = value.get("playerId")
                name = value.get("name")

                if player_id:
                    indexed[str(player_id)] = value

                if name:
                    indexed[str(name).casefold()] = value
            else:
                indexed[str(key)] = {"bio": value}

        return indexed

    for bio in bios:
        if not isinstance(bio, dict):
            continue

        player_id = bio.get("playerId")
        name = bio.get("name")

        if player_id:
            indexed[str(player_id)] = bio

        if name:
            indexed[str(name).casefold()] = bio

    return indexed


def align_embeddings(
    players: list[dict[str, Any]],
    bios: list[dict[str, Any]] | dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Merge player records with matching biography records."""
    bio_index = _index_bios(bios)
    aligned: dict[str, dict[str, Any]] = {}

    for player in players:
        player_id = str(player.get("playerId", "")).strip()
        name = str(player.get("name", "")).strip()
        position = player.get("position", "Unknown")

        bio_record: dict[str, Any] | None = None

        if player_id:
            bio_record = bio_index.get(player_id)

        if bio_record is None and name:
            bio_record = bio_index.get(name.casefold())

        bio_record = bio_record or {}

        record_key = player_id or name

        if not record_key:
            continue

        embedding_record = {
            **player,
            "embedding": player.get("embedding", []),
        }

        bio_position = str(
            bio_record.get("position", "")
        ).strip().upper()

        player_position = str(
            player.get("position", "")
        ).strip().upper()

        position_match = (
            bool(player_position)
            and bool(bio_position)
            and player_position == bio_position
        )

        aligned[record_key] = {
            "playerId": player_id or bio_record.get("playerId", ""),
            "name": name or bio_record.get("name", ""),
            "position": position or bio_record.get("position", "Unknown"),
            "team": bio_record.get(
                "team",
                player.get("team", "Unknown"),
            ),
            "bio": bio_record,
            "embedding": embedding_record,
            "position_match": position_match,
        }

    return aligned
