"""Strict, retrospective-only mapping of locked-model PPR predictions to a DK salary slate.

No player-name-only guessing, no live projections, no scoring-rule conversion.
"""
import re
import unicodedata
from pathlib import Path
import pandas as pd
from dfs_agents import CoordinatorAgent


def _name(value):
    value = unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', re.sub(r'\b(jr|sr|ii|iii|iv)\b', '', value))


def match_historical_slate(slate: pd.DataFrame, data_path: Path, model_path: Path,
                           season: int, week: int):
    """Return slate with 'Model PPR' and audit metadata. Require name+team+position match.

    The selected historical season/week must be explicitly chosen by the user.
    Historical 2025 test results are retrospective, not future DFS forecasts.
    """
    if not (2020 <= int(season) <= 2025 and 1 <= int(week) <= 18):
        raise ValueError('Choose a historical season (2020–2025) and week (1–18).')
    results, events = CoordinatorAgent(data_path, model_path).run(int(season), int(week))
    name_col = next((c for c in ('player_display_name', 'player_name') if c in results.columns), None)
    if name_col is None or 'team' not in results.columns:
        raise ValueError('Historical dataset requires a player name and team for safe matching.')
    historical = results[[name_col, 'team', 'position', 'projected_ppr']].copy()
    historical['_match'] = list(zip(historical[name_col].map(_name), historical['team'].astype(str).str.upper().str.strip(), historical['position'].astype(str).str.upper().str.strip()))
    # Ambiguous keys are never assigned predictions.
    counts = historical['_match'].value_counts()
    valid = historical.loc[historical['_match'].map(counts).eq(1)]
    lookup = valid.set_index('_match')['projected_ppr'].to_dict()
    output = slate.copy()
    output['_match'] = list(zip(output['Player'].map(_name), output['Team'].astype(str).str.upper().str.strip(), output['Position'].astype(str).str.upper().str.strip()))
    output['Model PPR'] = output['_match'].map(lookup)
    output.loc[~output['Position'].isin(['QB', 'RB', 'WR', 'TE']), 'Model PPR'] = float('nan')
    output.drop(columns=['_match'], inplace=True)
    matched = int(output['Model PPR'].notna().sum())
    return output, {'matched': matched, 'total': len(output), 'unmatched': len(output)-matched,
                    'season': int(season), 'week': int(week),
                    'events': [e.__dict__ for e in events]}
