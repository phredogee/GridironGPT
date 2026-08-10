# Known Issues

## WSL Scheduler Availability

The current hourly collector runs through cron inside Debian/WSL. Scheduled ingestion therefore depends on the WSL environment and cron service being available. A Windows restart or WSL lifecycle behavior can prevent collection until the environment is running again.

Longer term, consider a host-level scheduler or deployed always-on runtime.

## PYTHONPATH Required Under Cron

The scheduled runner imports the local `gridiron_gpt` package. Cron does not inherit the interactive shell environment, so the job must set `PYTHONPATH=.` after changing into the repository directory.

Without it, the runner fails with:

```text
ModuleNotFoundError: No module named 'gridiron_gpt'
```

## Duplicate Volume

RSS providers frequently expose the same articles across successive hourly polls. This is expected. Cortex fingerprint deduplication prevents repeated evidence from changing score history. Ingestion Status should be used to distinguish normalized events from newly accepted Cortex events.

## Local JSONL Growth

Cortex and ingestion observability currently persist operational/history data locally. Continuous collection will increase JSONL storage over time. Retention, compaction, archival, or database migration should be evaluated as history becomes substantial.

## Source Overlap

Additional providers should not be added solely to increase record volume. New sources should be evaluated for unique evidence, reliability, timeliness, and fantasy-football value.