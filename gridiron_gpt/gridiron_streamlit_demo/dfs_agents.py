"""Historical demonstration agents. No network access, live slates, or training."""
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

POSITIONS = ('QB', 'RB', 'WR', 'TE')

@dataclass
class AgentEvent:
    agent: str
    status: str
    detail: str

class DataAgent:
    def __init__(self, data_path: Path):
        self.data_path = Path(data_path)

    def fetch_week(self, season: int, week: int, positions=POSITIONS):
        if not self.data_path.is_file():
            raise FileNotFoundError(f'Historical dataset missing: {self.data_path}')
        # Read the requested season when supported by the Parquet reader.
        df = pd.read_parquet(self.data_path, filters=[('season', '==', int(season))])
        required = {'season', 'week', 'position', 'fantasy_points_ppr'}
        missing = required.difference(df.columns)
        if missing:
            raise ValueError(f'Dataset is missing required columns: {sorted(missing)}')
        df = df.loc[(df['season'] == season) & (df['week'] == week) &
                    df['position'].isin(positions) & df['position'].isin(POSITIONS)].copy()
        if df.empty:
            raise ValueError('No matching QB/RB/WR/TE records for the selected week.')
        return df

class ProjectionAgent:
    def __init__(self, model_path: Path):
        self.model_path = Path(model_path)

    def predict(self, records: pd.DataFrame):
        if not self.model_path.is_file():
            raise FileNotFoundError(f'Trained model missing: {self.model_path}')
        model = joblib.load(self.model_path)
        if not hasattr(model, 'feature_names_in_'):
            raise ValueError('Model does not expose feature_names_in_; cannot verify input schema.')
        features = list(model.feature_names_in_)
        forbidden = {'fantasy_points_ppr', 'season'}
        if forbidden.intersection(features):
            raise ValueError('Model expects target or season as an input; aborting for safety.')
        missing = [feature for feature in features if feature not in records.columns]
        if missing:
            raise ValueError(f'Missing trained-model features: {missing}')
        predicted = np.asarray(model.predict(records[features]), dtype=float)
        if not np.isfinite(predicted).all():
            raise ValueError('Model returned non-finite predictions.')
        result = records.copy()
        result['projected_ppr'] = predicted
        result['absolute_error'] = (result['projected_ppr'] - result['fantasy_points_ppr']).abs()
        return result

class CoordinatorAgent:
    """Deterministic agent handoffs and audit events for a historical demo."""
    def __init__(self, data_path: Path, model_path: Path):
        self.data_agent = DataAgent(data_path)
        self.projection_agent = ProjectionAgent(model_path)

    def run(self, season: int, week: int, positions=POSITIONS):
        events = []
        events.append(AgentEvent('Coordinator Agent', 'started', f'Historical {season} week {week} requested'))
        try:
            rows = self.data_agent.fetch_week(season, week, positions)
            events.append(AgentEvent('Data Agent', 'completed', f'Validated {len(rows):,} player-week records'))
            result = self.projection_agent.predict(rows)
            events.append(AgentEvent('Projection Agent', 'completed', f'Generated {len(result):,} locked-model predictions'))
            events.append(AgentEvent('Coordinator Agent', 'completed', 'Returned projections for human review; no lineup generated'))
            return result, events
        except Exception as exc:
            events.append(AgentEvent('Coordinator Agent', 'failed', str(exc)))
            raise AgentWorkflowError(str(exc), events) from exc

class AgentWorkflowError(RuntimeError):
    def __init__(self, message, events):
        super().__init__(message)
        self.events = events
