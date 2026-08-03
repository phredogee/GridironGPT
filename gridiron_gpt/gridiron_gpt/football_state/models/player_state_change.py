from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from gridiron_gpt.football_state.models.player_state import CanonicalPlayerState


@dataclass(frozen=True)
class PlayerStateChange:
    """Meaningful difference between two canonical player-state snapshots."""

    player_id: str
    player_name: str
    previous: CanonicalPlayerState | None
    current: CanonicalPlayerState
    changed_fields: dict[str, tuple[Any, Any]] = field(default_factory=dict)

    @property
    def is_new_player(self) -> bool:
        return self.previous is None

    @property
    def meaningful_change(self) -> bool:
        return self.is_new_player or bool(self.changed_fields)

    @property
    def team_changed(self) -> bool:
        return "team" in self.changed_fields

    @property
    def roster_status_changed(self) -> bool:
        return "roster_status" in self.changed_fields

    @property
    def depth_chart_changed(self) -> bool:
        return "depth_chart_position" in self.changed_fields

    @property
    def position_changed(self) -> bool:
        return "position" in self.changed_fields
