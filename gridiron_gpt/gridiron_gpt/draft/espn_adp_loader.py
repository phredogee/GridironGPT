from __future__ import annotations

from dataclasses import dataclass
import json
import math
from typing import Callable

import requests


ESPN_FANTASY_BASE_URL = (
    "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/"
    "seasons/{season}/segments/0/leaguedefaults/1"
)


@dataclass(frozen=True)
class EspnAdpSnapshot:
    records: dict[str, float]
    source: str = "ESPN"


class EspnAdpLoader:
    """Load ESPN Fantasy live-draft ADP from ESPN's fantasy player feed.

    ESPN's fantasy UI exposes live draft trends. The underlying player payload
    includes ``ownership.averageDraftPosition`` for players with draft activity.
    Network access is isolated behind ``json_loader`` so parsing remains fully
    unit-testable and a future endpoint change is contained to this adapter.
    """

    def __init__(
        self,
        *,
        season: int = 2026,
        scoring: str = "ppr",
        limit: int = 2000,
        timeout: float = 10.0,
        json_loader: Callable | None = None,
    ) -> None:
        self.season = int(season)
        self.scoring = scoring
        self.limit = int(limit)
        self.timeout = float(timeout)
        self.json_loader = json_loader

    def load(self) -> EspnAdpSnapshot:
        payload = self._load_payload()
        return EspnAdpSnapshot(records=self._parse_payload(payload))

    def _load_payload(self):
        if self.json_loader is not None:
            return self.json_loader()

        rank_type = {
            "ppr": "PPR",
            "half_ppr": "HALF",
            "standard": "STANDARD",
        }.get(self.scoring, "PPR")
        fantasy_filter = {
            "players": {
                "limit": self.limit,
                "sortDraftRanks": {
                    "sortPriority": 100,
                    "sortAsc": True,
                    "value": rank_type,
                },
            }
        }
        response = requests.get(
            ESPN_FANTASY_BASE_URL.format(season=self.season),
            params={"view": "kona_player_info"},
            headers={
                "Accept": "application/json",
                "User-Agent": "GridironGPT/1.0",
                "x-fantasy-filter": json.dumps(fantasy_filter),
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    def _parse_payload(cls, payload) -> dict[str, float]:
        players = cls._player_entries(payload)
        records: dict[str, float] = {}
        for entry in players:
            if not isinstance(entry, dict):
                continue
            player = entry.get("player") if isinstance(entry.get("player"), dict) else entry
            name = str(player.get("fullName") or player.get("name") or "").strip()
            if not name:
                continue

            ownership = player.get("ownership")
            if not isinstance(ownership, dict):
                ownership = entry.get("ownership") if isinstance(entry.get("ownership"), dict) else {}

            adp = cls._finite_positive(
                ownership.get("averageDraftPosition")
                or ownership.get("averageDraftPositionPercent")
            )
            if adp is None:
                continue
            records[name] = adp
        return records

    @staticmethod
    def _player_entries(payload) -> list:
        if isinstance(payload, list):
            return payload
        if not isinstance(payload, dict):
            return []
        players = payload.get("players")
        return players if isinstance(players, list) else []

    @staticmethod
    def _finite_positive(value) -> float | None:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return None
        if not math.isfinite(numeric) or numeric <= 0:
            return None
        return numeric
