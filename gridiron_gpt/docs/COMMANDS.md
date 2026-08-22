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
878 passed
```

## Draft Assistant Tests

```bash
pytest -q tests/test_fantasy_draft_pool_service.py
pytest -q tests/test_fantasy_roster_needs_service.py
pytest -q tests/test_fantasy_roster_advice_service.py
pytest -q tests/test_fantasy_best_fit_service.py
pytest -q tests/test_fantasy_best_fit_view.py
```

These cover drafted-player filtering, Best Available / Best Value behavior, roster deficits/advice, Best Fit ordering, production-score immutability, and Best Fit explanation semantics.

## Launch GridironGPT

From the inner `gridiron_gpt` project directory:

```bash
streamlit run apps/streamlit/Home.py
```

Use Draft Mode on the Fantasy Rankings page to validate:
- drafted players disappear from recommendation pools,
- `Mine` assigns a player to My Team,
- roster-needs counts update,
- Best Available / Best Value ordering remains stable,
- Best Fit Right Now responds to roster context,
- advisory reasons remain understandable.

## Fantasy Ranking Inspection

```bash
PYTHONPATH=. python scripts/inspect_fantasy_ranking_model.py --scoring ppr --limit 50
```

## Ingestion Runtime Tests

```bash
pytest tests/test_ingestion_service.py -v
pytest tests/test_ingestion_runtime.py -v
pytest tests/test_ingestion_cortex_pipeline.py -v
```

## Ingestion Smoke Test

```bash
python scripts/smoke_nfl_news_ingestion.py
```

Live provider availability can make this less deterministic than the unit/integration suite.

## Commissioner Suite Tests

```bash
pytest tests/test_commissioner_suite.py tests/test_league_exports.py -v
```

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
