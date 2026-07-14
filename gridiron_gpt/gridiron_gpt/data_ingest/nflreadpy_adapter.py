"""nflverse structured-data adapter powered by nflreadpy."""

from __future__ import annotations

from typing import Any

import nflreadpy as nfl


def _clean_value(value: Any) -> Any:
    """Convert values into JSON-safe primitives."""
    if value is None:
        return None

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return value


def _clean_record(record: dict[str, Any]) -> dict[str, Any]:
    """Return a JSON-safe copy of a Polars row dictionary."""
    return {
        key: _clean_value(value)
        for key, value in record.items()
    }


def load_players() -> list[dict[str, Any]]:
    """Load the nflverse player identity table."""
    frame = nfl.load_players()

    return [
        _clean_record(record)
        for record in frame.to_dicts()
    ]


def load_rosters(season: int) -> list[dict[str, Any]]:
    """Load NFL roster records for one season."""
    frame = nfl.load_rosters([season])

    return [
        _clean_record(record)
        for record in frame.to_dicts()
    ]


def load_weekly_player_stats(
    season: int,
) -> list[dict[str, Any]]:
    """Load weekly player statistics for one season."""
    frame = nfl.load_player_stats([season])

    return [
        _clean_record(record)
        for record in frame.to_dicts()
    ]


def fetch_nflverse_snapshot(season: int) -> dict[str, Any]:
    """Load the initial structured-data snapshot for Cortex."""
    players = load_players()
    rosters = load_rosters(season)
    weekly_stats = load_weekly_player_stats(season)

    return {
        "source": "nflverse",
        "season": season,
        "players": players,
        "rosters": rosters,
        "weekly_player_stats": weekly_stats,
        "counts": {
            "players": len(players),
            "rosters": len(rosters),
            "weekly_player_stats": len(weekly_stats),
        },
    }
