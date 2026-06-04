import json
from pathlib import Path

ROSTER_PATH = Path("data/roster_moves")


def load_roster_moves():
    items = []

    for file in ROSTER_PATH.glob("*.json"):
        try:
            with open(file) as f:
                items.extend(json.load(f))
        except Exception as e:
            print(f"⚠️ Failed loading {file}: {e}")

    return items
