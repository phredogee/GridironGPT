# gridiron_gpt/draft/changes.py

import os
from typing import Dict

DEFAULT_CHANGES_PATH = "data/offseason_changes.yaml"


def load_offseason_changes(path: str = DEFAULT_CHANGES_PATH) -> Dict[str, dict]:
    """Load offseason change multipliers from YAML. Returns {player_name: {multiplier, note}}."""
    if not os.path.exists(path):
        return {}
    import yaml
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    return data.get("players", {})
