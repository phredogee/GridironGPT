from __future__ import annotations

import math

import pandas as pd

from gridiron_gpt.draft.fantasy_ranking_population_service import FantasyRankingPopulation


def production_rankings_to_cli_frame(
    population: FantasyRankingPopulation,
    *,
    adp_by_name: dict[str, float] | None = None,
    teams: int = 12,
) -> pd.DataFrame:
    """Adapt the production ranking population to the legacy CLI display schema.

    This adapter does not recalculate player value. ``composite`` is the production
    ``ranking_score`` and ``suggested_round`` is derived only from overall rank so
    the existing CLI strategy/board presentation can be migrated independently.
    """
    if teams <= 0:
        raise ValueError("teams must be positive")

    adp_by_name = adp_by_name or {}
    rows: list[dict[str, object]] = []
    for rank, score in enumerate(population.overall, start=1):
        adp = adp_by_name.get(score.player_name)
        baseline = score.components.get("baseline")
        rows.append(
            {
                "rank": rank,
                "name": score.player_name,
                "position": score.position or "",
                "team": score.team or "",
                "hist_score": baseline if baseline is not None else math.nan,
                "adp": adp,
                "composite": score.ranking_score,
                "suggested_round": ((rank - 1) // teams) + 1,
                "injury": None,
                "note": None,
                "multiplier": 1.0,
            }
        )

    return pd.DataFrame(rows)
