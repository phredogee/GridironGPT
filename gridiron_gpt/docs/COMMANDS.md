# Useful Commands

## Phase C — Focused Regression Gate

```bash
pytest \
  tests/test_team_share_context.py \
  tests/test_contextual_statistical_reasoning.py \
  tests/test_statistical_event_interpreter.py \
  tests/test_nflverse_player_stats_adapter.py \
  tests/test_signal_processor.py \
  -v
```

Current focused C3.7 result:

```text
43 passed
```

## Live NFL News Ingestion Smoke Test

```bash
python scripts/smoke_nfl_news_ingestion.py
```

Reports total/resolved/unresolved events, provider counts, position counts, top resolved players, non-fantasy matches, and unresolved headlines.

## Run Full Test Suite

```bash
pytest
```

## Test Supabase

```bash
PYTHONPATH=. python -c "
from gridiron_gpt.storage.supabase_client import get_supabase_client
print(get_supabase_client())
"
```

## Legacy RSS Ingestion

```bash
PYTHONPATH=. python - <<'PY'
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path('.env'))

from gridiron_gpt.data_ingest.rss_news_fetcher import fetch_and_persist_from_env

print(fetch_and_persist_from_env())
PY
```

This command is retained for legacy compatibility. New ingestion development should use the unified `SourceAdapter` / `IngestionService` architecture.

## Run Recommendation Engine

```bash
PYTHONPATH=. python -c "
from gridiron_gpt.data_ingest.player_scores import build_recommendations_report
print(build_recommendations_report())
"
```

## Launch Dashboard

```bash
PYTHONPATH=. streamlit run streamlit_app.py
```
