from __future__ import annotations

from dataclasses import dataclass

from gridiron_cortex.presentation.models.player_card import (
    PlayerCardModel,
)


@dataclass(frozen=True, slots=True)
class DashboardSummary:
    """Top-level Dashboard summary information."""

    player_count: int
    buy_count: int
    watch_count: int
    risk_count: int


@dataclass(frozen=True, slots=True)
class DashboardPresentationModel:
    """Presentation model for the Dashboard page."""

    summary: DashboardSummary

    top_buy: PlayerCardModel | None
    top_watch: PlayerCardModel | None
    top_risk: PlayerCardModel | None

    rankings: tuple[PlayerCardModel, ...]

    passing_tests: int
