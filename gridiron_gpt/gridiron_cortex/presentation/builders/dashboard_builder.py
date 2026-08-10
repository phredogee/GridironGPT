from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from gridiron_cortex.presentation.models.dashboard import (
    DashboardPresentationModel,
    DashboardSummary,
)
from gridiron_cortex.presentation.models.player_card import (
    PlayerCardModel,
)

PlayerKey = tuple[str, str]
PlayerData = dict[str, Any]
RankedPlayer = tuple[PlayerKey, PlayerData]

RecommendationFunction = Callable[[float], str]
ConfidenceFunction = Callable[[Sequence[Any]], int | float]


def _score_from_data(data: PlayerData) -> float:
    """
    Return adjusted score when available.

    Falls back to the player's base score.
    """

    value = data.get(
        "adjusted_score",
        data.get("score", 0.0),
    )

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _confidence_from_data(
    data: PlayerData,
    confidence_from_signals: ConfidenceFunction,
) -> float:
    """Calculate confidence safely from a player's signals."""

    signals = data.get("signals", [])

    try:
        return float(
            confidence_from_signals(signals)
        )
    except (TypeError, ValueError, KeyError):
        return 0.0


def _build_dashboard_player(
    player_entry: RankedPlayer,
    *,
    recommendation_from_score: RecommendationFunction,
    confidence_from_signals: ConfidenceFunction,
) -> PlayerCardModel:
    """Convert one ranked player record into a presentation model."""

    (name, team), data = player_entry

    score = _score_from_data(data)

    confidence = _confidence_from_data(
        data,
        confidence_from_signals,
    )

    recommendation = recommendation_from_score(score)

    return PlayerCardModel(
        name=name,
        team=team,
        score=score,
        confidence=confidence,
        recommendation=recommendation,
    )


def _build_optional_player(
    players: Sequence[RankedPlayer],
    *,
    recommendation_from_score: RecommendationFunction,
    confidence_from_signals: ConfidenceFunction,
) -> PlayerCardModel | None:
    """Build the first player in a collection, when one exists."""

    if not players:
        return None

    return _build_dashboard_player(
        players[0],
        recommendation_from_score=recommendation_from_score,
        confidence_from_signals=confidence_from_signals,
    )


def build_dashboard_view_model(
    *,
    ranked_players: Sequence[RankedPlayer],
    buy_players: Sequence[RankedPlayer],
    watch_players: Sequence[RankedPlayer],
    risk_players: Sequence[RankedPlayer],
    player_count: int,
    recommendation_from_score: RecommendationFunction,
    confidence_from_signals: ConfidenceFunction,
    passing_tests: int,
    ranking_limit: int = 10,
) -> DashboardPresentationModel:
    """
    Build the framework-neutral Dashboard presentation model.
    """

    rankings = tuple(
        _build_dashboard_player(
            player_entry,
            recommendation_from_score=recommendation_from_score,
            confidence_from_signals=confidence_from_signals,
        )
        for player_entry in ranked_players[:ranking_limit]
    )

    return DashboardPresentationModel(
        summary=DashboardSummary(
            player_count=player_count,
            buy_count=len(buy_players),
            watch_count=len(watch_players),
            risk_count=len(risk_players),
        ),
        top_buy=_build_optional_player(
            buy_players,
            recommendation_from_score=recommendation_from_score,
            confidence_from_signals=confidence_from_signals,
        ),
        top_watch=_build_optional_player(
            watch_players,
            recommendation_from_score=recommendation_from_score,
            confidence_from_signals=confidence_from_signals,
        ),
        top_risk=_build_optional_player(
            risk_players,
            recommendation_from_score=recommendation_from_score,
            confidence_from_signals=confidence_from_signals,
        ),
        rankings=rankings,
        passing_tests=passing_tests,
    )
