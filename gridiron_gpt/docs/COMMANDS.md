# Useful Commands

## Phase C — Reliability / Observability Regression Gate

```bash
pytest \
  tests/test_ingestion_observability.py \
  tests/test_provider_health_tracker.py \
  tests/test_ingestion_health_integration.py \
  tests/test_ingestion_rate_limit.py \
  tests/test_ingestion_timeout.py \
  tests/test_ingestion_retry.py \
  tests/test_ingestion_provider_boundary.py \
  tests/test_ingestion_service.py \
  tests/test_nfl_news_adapters.py \
  -v
```

Validated Phase C closeout result:

```text
43 passed
```

## Live NFL News Ingestion Smoke Test

```bash
python scripts/smoke_nfl_news_ingestion.py
```

Reports total/resolved/unresolved events, provider counts, position counts, top resolved players, non-fantasy matches, and unresolved headlines.

## Run Full Test Suite

Run this at major phase boundaries and before large merges:

```bash
pytest
```

## Show Current Branch

```bash
git branch --show-current
```

## Check Working Tree

```bash
git status
```

## Update Current Development Branch

```bash
git pull origin refactor/extract-cortex
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
