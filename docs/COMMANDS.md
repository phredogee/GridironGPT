# Commands

## Tests

```bash
pytest -q
```

Current expected baseline on `develop/v1.1`: **744 passing tests** as of 2026-08-12.

Run the football-context facade integration test directly:

```bash
pytest -q tests/test_cortex_facade_football_context.py
```

## Run Scheduled Ingestion Manually

```bash
PYTHONPATH=. python scripts/run_scheduled_ingestion.py
```

A healthy run should report provider counts, records received, normalized events, new Cortex events, duplicates ignored, and processor failures.

## Inspect Structured Football State

Canonical football state is stored under:

```text
data/football_state/player_states.jsonl
data/football_state/game_states.jsonl
```

These stores are separate from Cortex news/evidence persistence.

## Start Streamlit

```bash
streamlit run gridiron_gpt/apps/streamlit/app.py
```

## Ranking Infrastructure Smoke Check

`RankingService` can currently sort latest Cortex scorecards overall and by position. Treat this output as an infrastructure test, not an authoritative fantasy ranking, until the Fantasy Ranking Score layer is implemented.

Run ranking-specific tests with:

```bash
pytest -q tests/test_ranking_service.py
```

If the ranking test filename changes, locate it with:

```bash
find tests -iname '*ranking*'
```

## Hourly WSL Cron

Edit the user crontab with nano:

```bash
EDITOR=nano crontab -e
```

Configured entry:

```cron
0 * * * * cd /home/phredo/projects/my_project/gridiron_gpt && PYTHONPATH=. /home/phredo/projects/my_project/gridiron_gpt/venv/bin/python scripts/run_scheduled_ingestion.py >> data/ingestion/cron.log 2>&1
```

Verify:

```bash
crontab -l
sudo service cron status
```

Inspect scheduled-run output:

```bash
tail -n 50 data/ingestion/cron.log
```

## Cron-like Manual Validation

```bash
cd /home/phredo/projects/my_project/gridiron_gpt && env -i HOME="$HOME" PATH="/usr/bin:/bin" PYTHONPATH=. /home/phredo/projects/my_project/gridiron_gpt/venv/bin/python scripts/run_scheduled_ingestion.py
```

This stripped environment is useful for detecting assumptions that work in an interactive shell but fail under cron.