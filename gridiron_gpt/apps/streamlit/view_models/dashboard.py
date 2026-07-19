from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any


PlayerKey = tuple[str, str]
PlayerData = dict[str, Any]
RankedPlayer = tuple[PlayerKey, PlayerData]

RecommendationFunction = Callable[[float], str]
ConfidenceFunction = Callable[[Sequence[Any]], int | float]


@dataclass(frozen=True, slots=True)
class DashboardPlayer:
    """Player data prepared for Dashboard presentation."""

    name: str
    team: str
    score: float
    confidence: float
    recommendation: str


@dataclass(frozen=True, slots=True)
class DashboardSummary:
    """Top-level Dashboard counts."""

    player_count: int
    buy_count: int
    watch_count: int
    risk_count: int


@dataclass(frozen=True, slots=True)
class DashboardViewModel:
    """Complete presentation model for the Dashboard page."""

    summary: DashboardSummary
    top_buy: DashboardPlayer | None
    top_watch: DashboardPlayer | None
    top_risk: DashboardPlayer | None
    rankings: tuple[DashboardPlayer, ...]
    passing_tests: int


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
) -> DashboardPlayer:
    """Convert one ranked player record into a Dashboard player."""

    (name, team), data = player_entry

    score = _score_from_data(data)

    confidence = _confidence_from_data(
        data,
        confidence_from_signals,
    )

    recommendation = recommendation_from_score(score)

    return DashboardPlayer(
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
) -> DashboardPlayer | None:
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
) -> DashboardViewModel:
    """
    Build the framework-neutral Dashboard presentation model.

    This function contains no Streamlit rendering code.
    """

    rankings = tuple(
        _build_dashboard_player(
            player_entry,
            recommendation_from_score=recommendation_from_score,
            confidence_from_signals=confidence_from_signals,
        )
        for player_entry in ranked_players[:ranking_limit]
    )

    return DashboardViewModel(
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
