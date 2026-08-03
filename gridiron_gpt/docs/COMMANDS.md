# GridironGPT Useful Commands

## Pull Current Development Branch

```bash
git pull origin refactor/extract-cortex
```

## Full Regression Suite

Run after every major implementation batch:

```bash
pytest -q
```

Current checkpoint:

```text
619 passed
```

## Visualization Tests

```bash
pytest tests/test_visualization_models.py -v
```

## Commissioner Suite Tests

```bash
pytest tests/test_commissioner_suite.py tests/test_league_exports.py -v
```

## Live-Signal Loader Tests

```bash
pytest tests/test_news_loader_persisted_signals.py -v
```

## Launch GridironGPT

From the `gridiron_gpt` project directory:

```bash
PYTHONPATH=. streamlit run streamlit_app.py
```

## Live RSS Ingestion

```bash
PYTHONPATH=. python - <<'PY'
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path('.env'))

from gridiron_gpt.data_ingest.rss_news_fetcher import fetch_and_persist_from_env

print(fetch_and_persist_from_env())
PY
```

Expected output includes per-source fetched/saved/skipped counts and total signals persisted. Duplicate stories should be reported as skipped rather than raising a unique-key exception.

## Verify Live Signals Reach Scoring

```bash
PYTHONPATH=. python - <<'PY'
from gridiron_gpt.data_ingest.news_loader import load_news
from gridiron_gpt.data_ingest.player_scores import calculate_player_scores

news = load_news()
scores = calculate_player_scores()

print(f"Loaded news/signals: {len(news)}")
print(f"Scored players: {len(scores)}")

for (player, team), data in sorted(
    scores.items(),
    key=lambda item: item[1]["score"],
    reverse=True,
)[:15]:
    if data["score"] != 0:
        print(player, team, data["score"], len(data["signals"]))
PY
```

## Test Supabase Connection

```bash
PYTHONPATH=. python - <<'PY'
from gridiron_gpt.storage.supabase_client import get_supabase_client
print(get_supabase_client())
PY
```

## Recommendation Report

```bash
PYTHONPATH=. python - <<'PY'
from gridiron_gpt.data_ingest.player_scores import build_recommendations_report
print(build_recommendations_report())
PY
```

## Ingestion Smoke Test

```bash
python scripts/smoke_nfl_news_ingestion.py
```

## Git Status

```bash
git branch --show-current
git status
```

## Typical Development Checkpoint

```bash
git pull origin refactor/extract-cortex
pytest -q
PYTHONPATH=. streamlit run streamlit_app.py
```
