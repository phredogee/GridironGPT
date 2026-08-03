from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone

from gridiron_gpt.data_ingest.player_catalog import load_player_catalog
from gridiron_gpt.football_state.models.player_state import CanonicalPlayerState
from gridiron_gpt.football_state.repositories.player_state_repository import PlayerStateRepository


class PlayerStateService:
    """Promote roster/catalog facts into canonical queryable player state."""

    def __init__(
        self,
        repository: PlayerStateRepository,
        *,
        catalog_loader: Callable[[], list[dict]] = load_player_catalog,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository
        self.catalog_loader = catalog_loader
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def refresh(self) -> list[CanonicalPlayerState]:
        effective_at = self.clock()
        states: list[CanonicalPlayerState] = []

        for player in self.catalog_loader():
            player_id = self._text(player.get("gsis_id"))
            player_name = self._text(player.get("player"))
            if not player_id or not player_name:
                continue

            state = CanonicalPlayerState(
                player_id=player_id,
                player_name=player_name,
                team=self._optional_text(player.get("team")),
                position=self._optional_text(player.get("position")),
                roster_status=self._optional_text(player.get("status")),
                depth_chart_position=self._optional_text(player.get("depth_chart_position")),
                jersey_number=player.get("jersey_number"),
                years_experience=player.get("years_exp"),
                college=self._optional_text(player.get("college")),
                rookie_year=player.get("rookie_year"),
                entry_year=player.get("entry_year"),
                draft_club=self._optional_text(player.get("draft_club")),
                draft_number=player.get("draft_number"),
                identifiers=self._identifiers(player),
                effective_at=effective_at,
                source="nflverse roster",
            )
            self.repository.save(state)
            states.append(state)

        return states

    def get(self, player_id: str) -> CanonicalPlayerState | None:
        return self.repository.get(player_id)

    @staticmethod
    def _identifiers(player: dict) -> dict[str, str]:
        mapping = {
            "gsis": player.get("gsis_id"),
            "espn": player.get("espn_id"),
            "sleeper": player.get("sleeper_id"),
            "pfr": player.get("pfr_id"),
            "yahoo": player.get("yahoo_id"),
            "rotowire": player.get("rotowire_id"),
        }
        return {key: str(value) for key, value in mapping.items() if value not in (None, "")}

    @staticmethod
    def _text(value) -> str:
        return "" if value is None else str(value).strip()

    @classmethod
    def _optional_text(cls, value) -> str | None:
        text = cls._text(value)
        return text or None
