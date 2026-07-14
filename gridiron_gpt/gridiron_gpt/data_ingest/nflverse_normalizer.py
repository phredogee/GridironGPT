"""Normalize nflverse records for Gridiron Cortex ingestion."""

from __future__ import annotations

from typing import Any


def normalize_roster_record(record: dict[str, Any]) -> dict[str, Any]:
    """Normalize one nflverse roster row."""
    return {
        "source": "nflverse",
        "event_type": "roster_snapshot",
        "player_id": (
            record.get("gsis_id")
            or record.get("player_id")
            or record.get("espn_id")
            or ""
        ),
        "player_name": (
            record.get("full_name")
            or record.get("player_name")
            or record.get("display_name")
            or ""
        ),
        "team": record.get("team") or "",
        "position": record.get("position") or "",
        "season": record.get("season"),
        "week": record.get("week"),
        "status": (
            record.get("status")
            or record.get("roster_status")
            or ""
        ),
        "metadata": record,
    }


def normalize_weekly_stat_record(
    record: dict[str, Any],
) -> dict[str, Any]:
    """Normalize one nflverse weekly-stat row."""
    return {
        "source": "nflverse",
        "event_type": "weekly_player_stats",
        "player_id": (
            record.get("player_id")
            or record.get("gsis_id")
            or ""
        ),
        "player_name": (
            record.get("player_display_name")
            or record.get("player_name")
            or record.get("display_name")
            or ""
        ),
        "team": (
            record.get("recent_team")
            or record.get("team")
            or ""
        ),
        "position": (
            record.get("position_group")
            or record.get("position")
            or ""
        ),
        "season": record.get("season"),
        "week": record.get("week"),
        "statistics": {
            key: value
            for key, value in record.items()
            if key not in {
                "player_id",
                "gsis_id",
                "player_display_name",
                "player_name",
                "display_name",
                "recent_team",
                "team",
                "position",
                "position_group",
                "season",
                "week",
            }
        },
        "metadata": record,
    }


def normalize_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Normalize roster and weekly-stat collections."""
    rosters = [
        normalize_roster_record(record)
        for record in snapshot.get("rosters", [])
    ]

    weekly_stats = [
        normalize_weekly_stat_record(record)
        for record in snapshot.get("weekly_player_stats", [])
    ]

    return {
        "source": "nflverse",
        "season": snapshot.get("season"),
        "rosters": rosters,
        "weekly_player_stats": weekly_stats,
        "counts": {
            "rosters": len(rosters),
            "weekly_player_stats": len(weekly_stats),
        },
    }
