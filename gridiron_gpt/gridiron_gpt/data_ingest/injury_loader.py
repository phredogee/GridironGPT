import json
from pathlib import Path

INJURY_PATH = Path("data/injuries")


def load_injuries():
    items = []

    for file in INJURY_PATH.glob("*.json"):
        try:
            with open(file) as f:
                items.extend(json.load(f))
        except Exception as e:
            print(f"⚠️ Failed loading {file}: {e}")

    return items
