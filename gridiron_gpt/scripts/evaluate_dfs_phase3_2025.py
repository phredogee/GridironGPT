"""One-time held-out 2025 evaluation of the locked Phase 3 DFS model.

Loads the previously selected model without fitting or tuning it.
Outputs evaluation artifacts under data/dfs/models/phase3/final_evaluation/.
"""
from pathlib import Path
import json
from pyexpat import features
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error

DATA = Path('data/dfs/processed/dfs_offense_player_week_2020_2025_reg.parquet')
MODEL = Path('data/dfs/models/phase3/tuning/random_forest_tuned.joblib')
OUT = Path('data/dfs/models/phase3/final_evaluation')
POSITIONS = ('QB', 'RB', 'WR', 'TE')
TARGET = 'fantasy_points_ppr'
BASELINE = 'fantasy_points_ppr_roll3'


def metrics(actual, predicted):
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    errors = predicted - actual
    return {
        'rows': len(actual),
        'mae': float(mean_absolute_error(actual, predicted)),
        'rmse': float(np.sqrt(mean_squared_error(actual, predicted))),
        'bias': float(np.mean(errors)),
        'median_absolute_error': float(median_absolute_error(actual, predicted)),
    }


def main():
    if not DATA.is_file() or not MODEL.is_file():
        raise FileNotFoundError(f'Check dataset/model paths: {DATA}, {MODEL}')
    if OUT.exists() and any(OUT.iterdir()):
        raise FileExistsError(f'{OUT} already contains results; refusing to overwrite held-out test outputs.')
    model = joblib.load(MODEL)
    if not hasattr(model, 'feature_names_in_'):
        raise RuntimeError('Model lacks feature_names_in_; inspect model before test evaluation.')
    features = list(model.feature_names_in_)
    if 'season' in features or TARGET in features:
        raise RuntimeError('Potential target/test leakage detected in feature list.')
    df = pd.read_parquet(DATA, filters=[('season', '==', 2025)])
    df = df.loc[df['position'].isin(POSITIONS)].copy()
    needed = set(features) | {'season', 'position', 'week', TARGET, BASELINE}
    missing = needed.difference(df.columns)
    if missing:
        raise ValueError(f'Missing columns: {sorted(missing)}')
    if len(df) != 6037 or not (df['season'] == 2025).all():
        raise ValueError(f'Unexpected 2025 test data size/season: {len(df)}')
    if df[TARGET].isna().any():
        raise ValueError('2025 test target contains missing values.')

    predicted = model.predict(df[features])
    result = df[['season', 'week', 'position', TARGET, BASELINE]].copy()
    for optional in ('player_id', 'player_name', 'player_display_name', 'team'):
        if optional in df.columns:
            result[optional] = df[optional].values
    result['predicted_ppr'] = predicted
    result['error'] = result['predicted_ppr'] - result[TARGET]
    result['absolute_error'] = result['error'].abs()
    eligible = result[BASELINE].notna()

    records = []
    def record(group, model_name, subset, column):
        if subset.empty:
            return
        records.append({'group': group, 'model': model_name,
                        **metrics(subset[TARGET], subset[column])})

    record('all_2025', 'tuned_random_forest', result, 'predicted_ppr')
    record('baseline_eligible', 'tuned_random_forest', result.loc[eligible], 'predicted_ppr')
    record('baseline_eligible', 'rolling_baseline', result.loc[eligible], BASELINE)
    record('cold_start', 'tuned_random_forest', result.loc[~eligible], 'predicted_ppr')
    for pos in POSITIONS:
        pos_rows = result.loc[result['position'].eq(pos)]
        record(f'position_{pos}', 'tuned_random_forest', pos_rows, 'predicted_ppr')
        pos_eligible = pos_rows.loc[pos_rows[BASELINE].notna()]
        record(f'position_{pos}_baseline_eligible', 'tuned_random_forest', pos_eligible, 'predicted_ppr')
        record(f'position_{pos}_baseline_eligible', 'rolling_baseline', pos_eligible, BASELINE)
        record(f'cold_start_{pos}', 'tuned_random_forest', pos_rows.loc[pos_rows[BASELINE].isna()], 'predicted_ppr')

    table = pd.DataFrame(records)
    OUT.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT / 'test_metrics_2025.csv', index=False)
    result.to_csv(OUT / 'test_predictions_2025.csv', index=False)
    result.nlargest(30, 'absolute_error').to_csv(OUT / 'largest_errors_2025.csv', index=False)
    (OUT / 'test_manifest.json').write_text(json.dumps({
        'test_season': 2025,
        'model_file': str(MODEL),
        'model_features': features,
        'test_rows': len(result),
        'baseline_eligible_rows': int(eligible.sum()),
        'cold_start_rows': int((~eligible).sum()),
        'position_filter': list(POSITIONS),
        'model_retrained_or_tuned_on_test': False,
    }, indent=2) + '\n')
    print('\nHELD-OUT 2025 TEST RESULTS — LOCKED MODEL')
    print(table[['group', 'model', 'rows', 'mae', 'rmse', 'bias']].round(4).to_string(index=False))
    print(f'\nSaved evaluation artifacts to {OUT}')
    print('Model was NOT retrained or tuned on 2025.')

if __name__ == '__main__':
    main()
