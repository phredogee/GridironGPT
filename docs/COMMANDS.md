# Commands

## Tests

```bash
pytest -q
```

Current expected baseline on develop/v1.1: 709 passing tests.

## Run Scheduled Ingestion Manually

```bash
PYTHONPATH=. python scripts/run_scheduled_ingestion.py
```

## Start Streamlit

```bash
streamlit run gridiron_gpt/apps/streamlit/app.py
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