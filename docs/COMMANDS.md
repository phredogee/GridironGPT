# Commands

## Tests

Run the full regression suite:

```bash
pytest -q
```

Current expected baseline on `main`: **939 passing tests** as of 2026-08-25.

Run the focused position-scarcity / Best Fit suite:

```bash
pytest -q \
  tests/test_fantasy_position_scarcity_service.py \
  tests/test_fantasy_position_scarcity_scenarios.py \
  tests/test_fantasy_best_fit_service.py \
  tests/test_fantasy_best_fit_view.py
```

Run taxonomy/classifier guards:

```bash
pytest -q tests/test_event_taxonomy.py tests/test_event_classifier.py
```

## Run Daily Production Ingestion Manually

```bash
python scripts/run_daily_ingestion.py
```

A healthy run should end with:

```text
processor_failures=0
status=healthy
```

Provider record counts may legitimately vary. A provider returning zero records is not itself the same as a processor failure; inspect the run diagnostics before attributing a failure to schedule timing.

## Run Scheduled/Local Ingestion

```bash
PYTHONPATH=. python scripts/run_scheduled_ingestion.py
```

## Inspect Structured Football State

```text
data/football_state/player_states.jsonl
data/football_state/game_states.jsonl
```

These stores remain separate from Cortex news/evidence persistence.

## Start Streamlit

```bash
streamlit run gridiron_gpt/apps/streamlit/app.py
```

The Draft Assistant Best Fit path now calculates position scarcity from the current undrafted candidate pool.

## Git Branch / Merge Workflow

Update local `main`:

```bash
git switch main
git pull --ff-only origin main
```

When a local feature branch and its remote have both advanced, fetch and merge explicitly rather than forcing a fast-forward:

```bash
git fetch origin
git merge --no-edit origin/<branch-name>
```

If Git has already performed a merge but cannot launch the configured editor, finish the pending merge with:

```bash
git commit --no-edit
```

To avoid the unavailable `nvim` editor configuration, choose an installed editor, for example:

```bash
git config --global core.editor "nano"
```

or:

```bash
git config --global core.editor "code --wait"
```

## Hourly WSL Cron

Edit the user crontab:

```bash
EDITOR=nano crontab -e
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