from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from gridiron_gpt.data_ingest.player_catalog import load_player_catalog
from gridiron_gpt.football_state.models.player_state import CanonicalPlayerState
from gridiron_gpt.football_state.models.player_state_change import PlayerStateChange
from gridiron_gpt.football_state.repositories.player_state_repository import PlayerStateRepository


class PlayerStateService:
    """Promote roster/catalog facts into canonical queryable player state."""

    MEANINGFUL_FIELDS = (
        "team",
        "position",
        "roster_status",
        "depth_chart_position",
    )

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
        self.last_changes: list[PlayerStateChange] = []

    def refresh(self) -> list[CanonicalPlayerState]:
        states, changes = self._refresh()
        self.last_changes = changes
        return states

    def refresh_changes(self) -> list[PlayerStateChange]:
        _states, changes = self._refresh()
        self.last_changes = changes
        return changes

    def _refresh(self) -> tuple[list[CanonicalPlayerState], list[PlayerStateChange]]:
        effective_at = self.clock()
        states: list[CanonicalPlayerState] = []
        changes: list[PlayerStateChange] = []

        for player in self.catalog_loader():
            state = self._build_state(player, effective_at)
            if state is None:
                continue

            previous = self.repository.get(state.player_id)
            change = self.detect_change(previous, state)

            if change.meaningful_change:
                self.repository.save(state)
                changes.append(change)

            states.append(state)

        return states, changes

    def get(self, player_id: str) -> CanonicalPlayerState | None:
        return self.repository.get(player_id)

    @classmethod
    def detect_change(
        cls,
        previous: CanonicalPlayerState | None,
        current: CanonicalPlayerState,
    ) -> PlayerStateChange:
        changed_fields: dict[str, tuple[Any, Any]] = {}

        if previous is not None:
            for field_name in cls.MEANINGFUL_FIELDS:
                before = getattr(previous, field_name)
                after = getattr(current, field_name)
                if before != after:
                    changed_fields[field_name] = (before, after)

        return PlayerStateChange(
            player_id=current.player_id,
            player_name=current.player_name,
            previous=previous,
            current=current,
            changed_fields=changed_fields,
        )

    def _build_state(
        self,
        player: dict,
        effective_at: datetime,
    ) -> CanonicalPlayerState | None:
        player_id = self._text(player.get("gsis_id"))
        player_name = self._text(player.get("player"))
        if not player_id or not player_name:
            return None

        return CanonicalPlayerState(
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
        return {
            key: str(value)
            for key, value in mapping.items()
            if value not in (None, "")
        }

    @staticmethod
    def _text(value) -> str:
        return "" if value is None else str(value).strip()

    @classmethod
    def _optional_text(cls, value) -> str | None:
        text = cls._text(value)
        return text or None
