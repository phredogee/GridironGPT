# GridironGPT Useful Commands

## Pull Current Development Branch

```bash
git pull --ff-only origin develop/v1.1
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
869 passed
```

## Draft Assistant Tests

```bash
pytest -q tests/test_fantasy_draft_pool_service.py
pytest -q tests/test_fantasy_roster_needs_service.py
pytest -q tests/test_fantasy_roster_advice_service.py
```

These cover drafted-player filtering, Best Available / Best Value behavior, roster deficits, and advisory presentation semantics.

## Launch GridironGPT

From the inner `gridiron_gpt` project directory:

```bash
streamlit run apps/streamlit/Home.py
```

Use Draft Mode on the Fantasy Rankings page to validate:
- drafted players disappear from the available pool,
- `Mine` assigns a player to My Team,
- roster-needs counts update,
- Best Available / Best Value ordering remains stable,
- advisory badges appear for active roster needs.

## Fantasy Ranking Inspection

```bash
PYTHONPATH=. python scripts/inspect_fantasy_ranking_model.py --scoring ppr --limit 50
```

Use the current inspection script available in the repository when validating production ranking components and projection influence. If a script name changes, prefer `ls scripts | grep fantasy` before assuming a legacy path still exists.

## Ingestion Runtime Tests

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

Live provider availability can make this less deterministic than the unit/integration suite.

## Commissioner Suite Tests

```bash
pytest tests/test_commissioner_suite.py tests/test_league_exports.py -v
```

## Persisted-Signal Loader Tests

```bash
pytest tests/test_news_loader_persisted_signals.py -v
```

## Test Supabase Connection

```bash
PYTHONPATH=. python - <<'PY'
from gridiron_gpt.storage.supabase_client import get_supabase_client
print(get_supabase_client())
PY
```

Only use this when validating the Supabase-backed live-data path. Cortex core local persistence does not require Supabase for the regression suite.

## Recommended Development Checkpoint

```bash
git status
pytest -q
streamlit run apps/streamlit/Home.py
```

When the suite and smoke test are clean:

```bash
git add <changed-files>
git commit -m "<message>"
git push origin develop/v1.1
```

Do not force-push or overwrite the development branch when a normal fast-forward workflow is available.
