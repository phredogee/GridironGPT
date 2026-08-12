# Known Issues

## Rankings Are Not Yet Fantasy Rankings

The current RankingService orders latest Cortex player scorecards by `overall_score`. This proves ranking infrastructure and position filtering, but the resulting Top 25/QB/RB/WR/TE lists are **not authoritative fantasy rankings**.

Players with recent positive Cortex evidence may rank above elite fantasy players with little processed news, and players without scorecards may be absent entirely. Do not expose these lists as draft rankings until the dedicated Fantasy Ranking Score layer supplies baseline fantasy value and appropriate contextual adjustments.

## Football Context Is Factual-Only

Roster availability, next opponent, home/away location, and bye week are now available to Cortex explanations. In v1.1 these facts intentionally do not modify Cortex scores. Scoring effects should be introduced only through an explicit, tested fantasy-ranking or decision policy rather than silently changing the meaning of Cortex `overall_score`.

## 2026 Structured Data Coverage

The project can persist 2026 roster/player state from the available roster source, but not every structured nflverse/nflreadpy dataset is guaranteed to expose the future/current 2026 season at the same time. Earlier validation showed some nflreadpy season loaders still reporting 2025 as their current supported season.

Future injury, depth-chart, projection, and statistical integrations must handle source-specific season availability instead of assuming all datasets advance together.

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

Cortex, football state, and ingestion observability currently persist operational/history data locally. Continuous collection will increase JSONL storage over time. Retention, compaction, archival, or database migration should be evaluated as history becomes substantial.

## Source Overlap

Additional providers should not be added solely to increase record volume. New sources should be evaluated for unique evidence, reliability, timeliness, and fantasy-football value.