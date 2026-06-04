import json
from pathlib import Path

NEWS_PATH = Path("data/news")


def load_news():
    items = []

    for file in NEWS_PATH.glob("*.json"):
        try:
            with open(file) as f:
                items.extend(json.load(f))
        except Exception as e:
            print(f"⚠️ Failed loading {file}: {e}")

    return items
