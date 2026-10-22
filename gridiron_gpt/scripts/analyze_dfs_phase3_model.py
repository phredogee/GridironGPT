"""Analyze the tuned DFS Random Forest using 2024 validation data only.

Run from the GridironGPT repository root:
    python scripts/analyze_dfs_phase3_model.py

Requires pandas, numpy, scikit-learn, joblib and a parquet engine.
No matplotlib required. The 2025 test set is never evaluated.
"""
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error

DATA_PATH = Path('data/dfs/processed/dfs_offense_player_week_2020_2025_reg.parquet')
MODEL_PATH = Path('data/dfs/models/phase3/tuning/random_forest_tuned.joblib')
OUTPUT_DIR = Path('data/dfs/models/phase3/analysis')
TARGET = 'fantasy_points_ppr'
BASELINE = 'fantasy_points_ppr_roll3'
SEED = 42


def metrics(actual, predicted):
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    error = predicted - actual
    return {
        'rows': len(actual),
        'mae': float(mean_absolute_error(actual, predicted)),
        'rmse': float(np.sqrt(mean_squared_error(actual, predicted))),
        'bias': float(np.mean(error)),
        'median_absolute_error': float(np.median(np.abs(error))),
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    model = joblib.load(MODEL_PATH)  # Only load artifacts you created/trust.
    feature_names = list(model.feature_names_in_)
    required = set(feature_names + [TARGET, BASELINE, 'season', 'position', 'player_id', 'week'])
    # Filter the season at parquet-read time to avoid loading 2025 observations.
    df = pd.read_parquet(DATA_PATH, filters=[('season', '==', 2024)])
    VALID_POSITIONS = ["QB", "RB", "WR", "TE"]
    df = df.loc[df["position"].isin(VALID_POSITIONS)].copy()
    df = df.loc[df['season'] == 2024].copy().reset_index(drop=True)
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f'Missing columns: {missing}')
    if df.empty:
        raise ValueError('No 2024 validation rows found')

    predictions = model.predict(df[feature_names])
    results = df[['player_id', 'position', 'season', 'week', TARGET, BASELINE]].copy()
    if 'player_name' in df:
        results.insert(1, 'player_name', df['player_name'])
    results = results.rename(columns={TARGET: 'actual_ppr', BASELINE: 'baseline_ppr'})
    results['predicted_ppr'] = predictions
    results['error'] = results['predicted_ppr'] - results['actual_ppr']
    results['absolute_error'] = results['error'].abs()
    results['baseline_eligible'] = results['baseline_ppr'].notna()

    rows = []
    def add(group, label, subset, column):
        if not subset.empty:
            rows.append({'group': group, 'model': label,
                         **metrics(subset['actual_ppr'], subset[column])})

    add('all_2024', 'tuned_random_forest', results, 'predicted_ppr')
    ready = results.loc[results['baseline_eligible']]
    cold = results.loc[~results['baseline_eligible']]
    add('baseline_eligible', 'tuned_random_forest', ready, 'predicted_ppr')
    add('baseline_eligible', 'rolling_baseline', ready, 'baseline_ppr')
    add('cold_start', 'tuned_random_forest', cold, 'predicted_ppr')
    for pos in ['QB', 'RB', 'WR', 'TE']:
        subset = ready.loc[ready['position'] == pos]
        add(f'position_{pos}', 'tuned_random_forest', subset, 'predicted_ppr')
        add(f'position_{pos}', 'rolling_baseline', subset, 'baseline_ppr')
        cold_pos = cold.loc[cold['position'] == pos]
        add(f'cold_start_{pos}', 'tuned_random_forest', cold_pos, 'predicted_ppr')

    metric_table = pd.DataFrame(rows)
    metric_table.to_csv(OUTPUT_DIR / 'tuned_model_metrics.csv', index=False)
    results.sort_values('absolute_error', ascending=False).head(30).to_csv(
        OUTPUT_DIR / 'largest_prediction_errors.csv', index=False)
    results.to_csv(OUTPUT_DIR / 'tuned_validation_predictions.csv', index=False)

    print('Computing permutation importance on 2024 validation rows...')
    importance = permutation_importance(
        model, df[feature_names], df[TARGET],
        scoring='neg_mean_absolute_error', n_repeats=3,
        random_state=SEED, n_jobs=1,
    )
    importance_table = pd.DataFrame({
        'feature': feature_names,
        'mae_increase_mean': importance.importances_mean,
        'mae_increase_std': importance.importances_std,
    }).sort_values('mae_increase_mean', ascending=False)
    importance_table.to_csv(OUTPUT_DIR / 'permutation_feature_importance.csv', index=False)

    metadata = {
        'validation_season': 2024,
        'model_path': str(MODEL_PATH),
        'total_validation_rows': int(len(results)),
        'baseline_eligible_rows': int(len(ready)),
        'cold_start_rows': int(len(cold)),
        'importance_method': 'permutation, 3 repeats, negative MAE',
        'note': 'Correlated rolling/lag features can share or mask permutation importance.',
        'test_season': '2025 reserved; not evaluated',
    }
    (OUTPUT_DIR / 'analysis_config.json').write_text(json.dumps(metadata, indent=2))
    print('\nMODEL METRICS (2024)')
    print(metric_table.to_string(index=False, float_format=lambda x: f'{x:.4f}'))
    print('\nTOP 12 PERMUTATION FEATURES (MAE increase when shuffled)')
    print(importance_table.head(12).to_string(index=False, float_format=lambda x: f'{x:.4f}'))
    print(f'\nSaved outputs to {OUTPUT_DIR}')
    print('2025 test season was not evaluated.')


if __name__ == '__main__':
    main()
