from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from gridiron_gpt.draft.fantasy_player_projection_service import PlayerFantasyProjection


@dataclass(frozen=True)
class FantasyProjectionView:
    projected_points: float
    projected_ppg: float


def build_projection_views(
    projections: Mapping[str, PlayerFantasyProjection],
) -> dict[str, FantasyProjectionView]:
    """Build a case-insensitive player-name lookup for informational ranking UI metrics."""
    return {
        player_name.casefold(): FantasyProjectionView(
            projected_points=projection.fantasy.projected_points,
            projected_ppg=projection.fantasy.projected_ppg,
        )
        for player_name, projection in projections.items()
    }


def projection_view_for_player(
    player_name: str,
    views: Mapping[str, FantasyProjectionView],
) -> FantasyProjectionView | None:
    """Return projection metrics without affecting ranking or market calculations."""
    return views.get(player_name.casefold())
