# GridironGPT Useful Commands

## Pull Current Development Branch

```bash
git pull origin refactor/extract-cortex
```

## Confirm Branch and Working Tree

```bash
git branch --show-current
git status
```

## Full Regression Suite

Run after every significant code or architecture change:

```bash
pytest -q
```

Current verified checkpoint:

```text
702 passed
```

## v1.0 Runtime-Ingestion Tests

```bash
pytest tests/test_ingestion_service.py -v
pytest tests/test_ingestion_runtime.py -v
pytest tests/test_ingestion_cortex_pipeline.py -v
```

These cover normalization/runtime handoff, downstream fail-open behavior, production composition, persistence, restart behavior, and Replay reconstruction.

## Ingestion Smoke Test

```bash
python scripts/smoke_nfl_news_ingestion.py
```

Use this when validating live provider behavior. Network/provider availability can make live smoke tests less deterministic than the unit/integration suite.

## Launch GridironGPT

From the `gridiron_gpt` project directory:

```bash
PYTHONPATH=. streamlit run streamlit_app.py
```

For the v1.0 smoke test, open the primary navigation surfaces and verify they render without runtime exceptions, especially Dashboard, Advisor, Players, Cortex Explorer, Cortex Inspector, and Ingestion Status.

## Visualization Tests

```bash
pytest tests/test_visualization_models.py -v
```

## Commissioner Suite Tests

```bash
pytest tests/test_commissioner_suite.py tests/test_league_exports.py -v
```

## Persisted-Signal Loader Tests

```bash
pytest tests/test_news_loader_persisted_signals.py -v
```

## Live RSS Persistence Path

```bash
PYTHONPATH=. python - <<'PY'
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path('.env'))

from gridiron_gpt.data_ingest.rss_news_fetcher import fetch_and_persist_from_env

print(fetch_and_persist_from_env())
PY
```

Duplicate stories should be skipped rather than raising a unique-key exception.

## Verify Signals Reach Legacy/Presentation Scoring

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

This command checks the scored-player map used by several presentation surfaces; it is separate from the Cortex runtime-ingestion integration tests above.

## Test Supabase Connection

```bash
PYTHONPATH=. python - <<'PY'
from gridiron_gpt.storage.supabase_client import get_supabase_client
print(get_supabase_client())
PY
```

Only use this when validating the Supabase-backed live-data path; Cortex core persistence is repository-backed and does not require this connection for local tests.

## Recommendation Report

```bash
PYTHONPATH=. python - <<'PY'
from gridiron_gpt.data_ingest.player_scores import build_recommendations_report
print(build_recommendations_report())
PY
```

## Final v1.0 Local Checkpoint

```bash
git pull origin refactor/extract-cortex
pytest -q
PYTHONPATH=. streamlit run streamlit_app.py
```

Do not tag or merge a release candidate until the full regression suite is green and the Streamlit smoke test is complete.
