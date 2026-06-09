import json
from pathlib import Path


def load_relationships():
    data_file = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "relationships.json"
    )

    with open(data_file, "r") as f:
        return json.load(f)
