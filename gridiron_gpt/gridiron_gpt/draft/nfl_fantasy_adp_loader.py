from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Callable


NFL_FANTASY_ADP_URL = "https://fantasy.nfl.com/draftcenter/breakdown"


@dataclass(frozen=True)
class NflFantasyAdpSnapshot:
    records: dict[str, float]
    source: str = "NFL Fantasy"


class NflFantasyAdpLoader:
    """Load public NFL Fantasy Draft Breakdown ADP values.

    The public Draft Breakdown page exposes a tabular Player / Avg. Pick (ADP)
    view. Parsing is isolated behind this loader so a future API-backed source can
    replace the HTML-table implementation without affecting consensus logic.
    """

    def __init__(
        self,
        *,
        url: str = NFL_FANTASY_ADP_URL,
        table_loader: Callable | None = None,
    ) -> None:
        self.url = url
        self.table_loader = table_loader

    def load(self) -> NflFantasyAdpSnapshot:
        tables = self._load_tables()
        for frame in tables:
            records = self._parse_table(frame)
            if records:
                return NflFantasyAdpSnapshot(records=records)
        return NflFantasyAdpSnapshot(records={})

    def _load_tables(self):
        if self.table_loader is not None:
            return self.table_loader(self.url)
        import pandas as pd

        return pd.read_html(self.url)

    @classmethod
    def _parse_table(cls, frame) -> dict[str, float]:
        if frame is None or getattr(frame, "empty", True):
            return {}

        work = frame.copy()
        work.columns = [cls._flatten_column(column) for column in work.columns]
        player_col = cls._find_column(work.columns, "player")
        adp_col = cls._find_column(work.columns, "avg. pick") or cls._find_column(
            work.columns, "adp"
        )
        if player_col is None or adp_col is None:
            return {}

        records: dict[str, float] = {}
        for row in work[[player_col, adp_col]].itertuples(index=False, name=None):
            player_text, raw_adp = row
            player_name = cls._player_name(player_text)
            adp = cls._adp(raw_adp)
            if player_name and adp is not None:
                records[player_name] = adp
        return records

    @staticmethod
    def _flatten_column(column) -> str:
        if isinstance(column, tuple):
            parts = [str(part).strip() for part in column if str(part).strip()]
            return " ".join(dict.fromkeys(parts))
        return str(column).strip()

    @staticmethod
    def _find_column(columns, needle: str) -> str | None:
        needle = needle.casefold()
        for column in columns:
            if needle in str(column).casefold():
                return column
        return None

    @staticmethod
    def _player_name(value) -> str:
        text = re.sub(r"\s+", " ", str(value or "")).strip()
        if not text:
            return ""
        match = re.match(r"^(.*?)\s+(QB|RB|WR|TE)\b", text, flags=re.IGNORECASE)
        return (match.group(1) if match else text).strip()

    @staticmethod
    def _adp(value) -> float | None:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return None
        if not math.isfinite(numeric) or numeric <= 0:
            return None
        return numeric
