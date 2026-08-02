from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd

from gridiron_gpt.ingestion.models.source_record import SourceRecord
from gridiron_gpt.ingestion.sources.base import SourceAdapter


StatsLoader = Callable[[int | list[int], str], pd.DataFrame]


class NFLVersePlayerStatsAdapter(SourceAdapter):
    """Expose nflverse weekly player statistics as source-neutral records.

    The adapter emits factual statistical evidence only. It does not assign
    sentiment, fantasy impact, recommendations, or Cortex confidence.
    """

    def __init__(
        self,
        seasons: int | list[int],
        *,
        summary_level: str = "week",
        loader: StatsLoader | None = None,
        positions: set[str] | None = None,
    ) -> None:
        self.seasons = seasons
        self.summary_level = summary_level
        self.loader = loader or self._default_loader
        self.positions = positions

    @property
    def source_name(self) -> str:
        return "nflverse player stats"

    def fetch(self) -> list[SourceRecord]:
        frame = self.loader(self.seasons, self.summary_level)

        if frame.empty:
            return []

        records: list[SourceRecord] = []

        for row in frame.to_dict(orient="records"):
            position = self._text(row.get("position")).upper()

            if self.positions and position not in self.positions:
                continue

            player_id = self._text(row.get("player_id"))
            player_name = (
                self._text(row.get("player_display_name"))
                or self._text(row.get("player_name"))
            )
            team = self._text(row.get("team")).upper()
            season = row.get("season")
            week = row.get("week")
            season_type = self._text(row.get("season_type"))
            game_id = self._text(row.get("game_id"))
            opponent = self._text(row.get("opponent_team")).upper()

            if not player_id or not player_name:
                continue

            source_id = self._build_source_id(
                player_id=player_id,
                season=season,
                week=week,
                season_type=season_type,
                game_id=game_id,
            )

            headline = self._build_headline(
                player_name=player_name,
                season=season,
                week=week,
                team=team,
            )

            stats = self._extract_stat_values(row)

            records.append(
                SourceRecord(
                    source=self.source_name,
                    headline=headline,
                    player=player_name,
                    team=team or None,
                    position=position or None,
                    source_id=source_id,
                    metadata={
                        "provider": "nflverse",
                        "dataset": "player_stats",
                        "summary_level": self.summary_level,
                        "player_id": player_id,
                        "season": season,
                        "week": week,
                        "season_type": season_type or None,
                        "game_id": game_id or None,
                        "opponent_team": opponent or None,
                        "stats": stats,
                    },
                )
            )

        return records

    @staticmethod
    def _default_loader(
        seasons: int | list[int],
        summary_level: str,
    ) -> pd.DataFrame:
        import nflreadpy as nfl

        return nfl.load_player_stats(
            seasons,
            summary_level=summary_level,
        ).to_pandas()

    @staticmethod
    def _build_source_id(
        *,
        player_id: str,
        season: Any,
        week: Any,
        season_type: str,
        game_id: str,
    ) -> str:
        if game_id:
            return f"player_stats:{game_id}:{player_id}"

        return ":".join(
            [
                "player_stats",
                str(season or ""),
                str(week or ""),
                season_type or "",
                player_id,
            ]
        )

    @staticmethod
    def _build_headline(
        *,
        player_name: str,
        season: Any,
        week: Any,
        team: str,
    ) -> str:
        parts = [player_name]

        if team:
            parts.append(f"({team})")

        if season is not None and week is not None:
            parts.append(f"{season} Week {week} statistical line")
        elif season is not None:
            parts.append(f"{season} statistical line")
        else:
            parts.append("statistical line")

        return " ".join(parts)

    @staticmethod
    def _extract_stat_values(row: dict[str, Any]) -> dict[str, Any]:
        excluded = {
            "player_id",
            "player_name",
            "player_display_name",
            "position",
            "position_group",
            "headshot_url",
            "season",
            "week",
            "season_type",
            "game_id",
            "team",
            "opponent_team",
        }

        stats: dict[str, Any] = {}

        for key, value in row.items():
            if key in excluded:
                continue

            if pd.isna(value):
                continue

            if hasattr(value, "item"):
                value = value.item()

            stats[key] = value

        return stats

    @staticmethod
    def _text(value: Any) -> str:
        if value is None or pd.isna(value):
            return ""
        return str(value).strip()
