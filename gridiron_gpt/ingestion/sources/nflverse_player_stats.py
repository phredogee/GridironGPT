from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd

from gridiron_gpt.ingestion.models.source_record import SourceRecord
from gridiron_gpt.ingestion.sources.base import SourceAdapter


StatsLoader = Callable[[int | list[int], str], pd.DataFrame]
CONTEXT_METRICS = (
    "carries",
    "rushing_attempts",
    "targets",
    "receptions",
    "rushing_yards",
    "receiving_yards",
    "passing_yards",
    "passing_tds",
    "passing_touchdowns",
    "rushing_tds",
    "rushing_touchdowns",
    "receiving_tds",
    "receiving_touchdowns",
    "interceptions",
    "passing_interceptions",
    "sacks",
    "sacks_suffered",
)


class NFLVersePlayerStatsAdapter(SourceAdapter):
    """Expose nflverse weekly player statistics as source-neutral records.

    Weekly records include player rolling baselines and team opportunity-share
    context. The adapter remains factual: Cortex decides how those changes
    affect fantasy intelligence.
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

        rows = frame.to_dict(orient="records")
        context_by_index = self._build_context(rows)
        share_by_index = self._build_team_share_context(rows)
        records: list[SourceRecord] = []

        for index, row in enumerate(rows):
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
                        "stat_context": context_by_index.get(index),
                        "team_share_context": share_by_index.get(index),
                    },
                )
            )

        return records

    @classmethod
    def _build_context(cls, rows: list[dict[str, Any]]) -> dict[int, dict]:
        grouped: dict[str, list[tuple[int, dict[str, Any]]]] = {}
        for index, row in enumerate(rows):
            player_id = cls._text(row.get("player_id"))
            if player_id:
                grouped.setdefault(player_id, []).append((index, row))

        result: dict[int, dict] = {}
        for player_rows in grouped.values():
            ordered = sorted(
                player_rows,
                key=lambda item: (
                    cls._sortable_number(item[1].get("season")),
                    cls._sortable_number(item[1].get("week")),
                ),
            )
            history: list[dict[str, Any]] = []
            for index, row in ordered:
                current = cls._context_values(row)
                baseline = cls._average_metrics(history)
                deltas = {
                    key: round(current.get(key, 0.0) - baseline.get(key, 0.0), 3)
                    for key in current
                    if key in baseline
                }
                result[index] = {
                    "prior_games": len(history),
                    "baseline": baseline,
                    "current": current,
                    "deltas": deltas,
                }
                history.append(current)
        return result

    @classmethod
    def _build_team_share_context(cls, rows: list[dict[str, Any]]) -> dict[int, dict]:
        game_groups: dict[tuple, list[tuple[int, dict[str, Any]]]] = {}
        for index, row in enumerate(rows):
            team = cls._text(row.get("team")).upper()
            if not team:
                continue
            key = (
                row.get("season"),
                row.get("week"),
                cls._text(row.get("season_type")),
                team,
            )
            game_groups.setdefault(key, []).append((index, row))

        current_shares: dict[int, dict[str, float]] = {}
        for group in game_groups.values():
            team_carries = sum(cls._stat_number(row, "carries", "rushing_attempts") for _, row in group)
            team_targets = sum(cls._stat_number(row, "targets") for _, row in group)
            team_pass_attempts = sum(
                cls._stat_number(row, "attempts", "passing_attempts")
                for _, row in group
                if cls._text(row.get("position")).upper() == "QB"
            )
            for index, row in group:
                position = cls._text(row.get("position")).upper()
                shares: dict[str, float] = {}
                carries = cls._stat_number(row, "carries", "rushing_attempts")
                targets = cls._stat_number(row, "targets")
                attempts = cls._stat_number(row, "attempts", "passing_attempts")
                if team_carries > 0 and carries > 0:
                    shares["carry_share"] = round(carries / team_carries, 4)
                if team_targets > 0 and targets > 0:
                    shares["target_share"] = round(targets / team_targets, 4)
                if position == "QB" and team_pass_attempts > 0 and attempts > 0:
                    shares["pass_attempt_share"] = round(attempts / team_pass_attempts, 4)
                current_shares[index] = shares

        player_groups: dict[str, list[tuple[int, dict[str, Any]]]] = {}
        for index, row in enumerate(rows):
            player_id = cls._text(row.get("player_id"))
            if player_id:
                player_groups.setdefault(player_id, []).append((index, row))

        result: dict[int, dict] = {}
        for player_rows in player_groups.values():
            ordered = sorted(
                player_rows,
                key=lambda item: (
                    cls._sortable_number(item[1].get("season")),
                    cls._sortable_number(item[1].get("week")),
                ),
            )
            history: list[dict[str, float]] = []
            for index, _row in ordered:
                current = current_shares.get(index, {})
                baseline = cls._average_metrics(history)
                deltas = {
                    key: round(current[key] - baseline[key], 4)
                    for key in current
                    if key in baseline
                }
                result[index] = {
                    "prior_games": len(history),
                    "baseline": baseline,
                    "current": current,
                    "deltas": deltas,
                }
                history.append(current)
        return result

    @classmethod
    def _context_values(cls, row: dict[str, Any]) -> dict[str, float]:
        values: dict[str, float] = {}
        for key in CONTEXT_METRICS:
            value = cls._numeric(row.get(key))
            if value is not None:
                values[key] = value
        carries = values.get("carries", values.get("rushing_attempts", 0.0))
        receptions = values.get("receptions", 0.0)
        values["touches"] = carries + receptions
        values["scrimmage_yards"] = values.get("rushing_yards", 0.0) + values.get("receiving_yards", 0.0)
        return values

    @staticmethod
    def _average_metrics(history: list[dict[str, float]]) -> dict[str, float]:
        if not history:
            return {}
        keys = set().union(*(entry.keys() for entry in history))
        averages: dict[str, float] = {}
        for key in keys:
            values = [entry[key] for entry in history if key in entry]
            if values:
                averages[key] = round(sum(values) / len(values), 4)
        return averages

    @classmethod
    def _stat_number(cls, row: dict[str, Any], *keys: str) -> float:
        for key in keys:
            value = cls._numeric(row.get(key))
            if value is not None:
                return value
        return 0.0

    @staticmethod
    def _default_loader(seasons: int | list[int], summary_level: str) -> pd.DataFrame:
        import nflreadpy as nfl
        return nfl.load_player_stats(seasons, summary_level=summary_level).to_pandas()

    @staticmethod
    def _build_source_id(*, player_id: str, season: Any, week: Any, season_type: str, game_id: str) -> str:
        if game_id:
            return f"player_stats:{game_id}:{player_id}"
        return ":".join(["player_stats", str(season or ""), str(week or ""), season_type or "", player_id])

    @staticmethod
    def _build_headline(*, player_name: str, season: Any, week: Any, team: str) -> str:
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
        excluded = {"player_id", "player_name", "player_display_name", "position", "position_group", "headshot_url", "season", "week", "season_type", "game_id", "team", "opponent_team"}
        stats: dict[str, Any] = {}
        for key, value in row.items():
            if key in excluded or pd.isna(value):
                continue
            if hasattr(value, "item"):
                value = value.item()
            stats[key] = value
        return stats

    @staticmethod
    def _numeric(value: Any) -> float | None:
        if value is None or pd.isna(value):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _sortable_number(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return -1.0

    @staticmethod
    def _text(value: Any) -> str:
        if value is None or pd.isna(value):
            return ""
        return str(value).strip()
