"""Transparent DraftKings NFL Classic scoring reference and retrospective calculator.

This module scores *observed game statistics*. It cannot turn a PPR point
prediction into a reliable DraftKings projection: bonus probabilities and
fumble-loss expectations require separate models.
"""
from dataclasses import dataclass
from typing import Mapping

@dataclass(frozen=True)
class DKScoring:
    passing_yards: float = 0.04
    passing_td: float = 4.0
    interception: float = -1.0
    rushing_yards: float = 0.1
    rushing_td: float = 6.0
    receiving_yards: float = 0.1
    receiving_td: float = 6.0
    reception: float = 1.0
    fumble_lost: float = -1.0
    passing_300_bonus: float = 3.0
    rushing_100_bonus: float = 3.0
    receiving_100_bonus: float = 3.0

RULES = DKScoring()

def score_observed_offense(stats: Mapping[str, float]):
    """Calculate historical DK offensive points; missing fields make results incomplete.

    Returns (score, missing_fields). Never substitute this for a forecast.
    """
    fields = ('passing_yards', 'passing_tds', 'passing_interceptions',
              'rushing_yards', 'rushing_tds', 'receiving_yards',
              'receiving_tds', 'receptions', 'fumbles_lost')
    missing = [f for f in fields if f not in stats or stats[f] is None]
    if missing:
        return None, missing
    s = {f: float(stats[f]) for f in fields}
    points = (s['passing_yards'] * RULES.passing_yards
              + s['passing_tds'] * RULES.passing_td
              + s['passing_interceptions'] * RULES.interception
              + s['rushing_yards'] * RULES.rushing_yards
              + s['rushing_tds'] * RULES.rushing_td
              + s['receiving_yards'] * RULES.receiving_yards
              + s['receiving_tds'] * RULES.receiving_td
              + s['receptions'] * RULES.reception
              + s['fumbles_lost'] * RULES.fumble_lost)
    points += RULES.passing_300_bonus if s['passing_yards'] >= 300 else 0
    points += RULES.rushing_100_bonus if s['rushing_yards'] >= 100 else 0
    points += RULES.receiving_100_bonus if s['receiving_yards'] >= 100 else 0
    return round(points, 2), []


def dst_demo_estimate(uploaded_average, floor=0.0, ceiling=20.0):
    """Explicit demo-only DST estimate from uploaded historical DK average.

    This is NOT a trained DST model or a current-game projection.
    """
    import math
    try:
        value = float(uploaded_average)
    except (ValueError, TypeError):
        return None
    if not math.isfinite(value):
        return None
    return round(max(floor, min(ceiling, value)), 2)
