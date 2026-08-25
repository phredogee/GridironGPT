# Known Issues

## Position Scarcity Is Advisory, Not Player Value

Position scarcity measures the opportunity cost of waiting at a position. It must not be interpreted as a replacement fantasy ranking. Best Fit applies only a bounded low/medium/high scarcity bonus (`0/1/2`) and never mutates production `ranking_score`.

A high-scarcity player can move ahead of a closely ranked alternative, but should not leapfrog a materially stronger player. Changes to these bounds require explicit ordering/regression tests.

## Scarcity Depends on Candidate-Pool Accuracy

Scarcity is calculated from the current undrafted candidate pool. If a drafted player remains available in application state, or an available player is incorrectly removed, the measured position depth and tier cliff can be wrong. Draft-night pick-state accuracy is therefore part of the scarcity contract.

## Tier Metadata Matters

Tier-cliff reasoning depends on usable tier information. Candidates without tier metadata can still participate in existing Best Fit behavior, but tier-boundary explanations should not be inferred when the source data does not support them.

## Live Taxonomy Requires Integrity Guards

A live RotoWire event exposed a malformed `transaction.released` taxonomy rule that lacked `impact`, producing a downstream `KeyError`. The rule is fixed and taxonomy integrity tests now require all rule fields plus non-empty phrases. New taxonomy rules must preserve that contract.

## Provider Record Counts Vary

ESPN and RotoWire may return different record counts between runs, including zero records from a provider. A low/zero record count alone does not prove a scheduling failure. Production health is determined from provider failures and Cortex processor failures, with diagnostics inspected when a run reports `status=attention`.

## Football Context Is Factual-Only

Roster availability, next opponent, home/away location, and bye week are available to explanations. These facts should affect fantasy decisions only through explicit, tested ranking/decision policies rather than silently changing Cortex `overall_score`.

## 2026 Structured Data Coverage

Not every nflverse/nflreadpy dataset is guaranteed to expose the 2026 season at the same time. Injury, depth-chart, projection, and statistical integrations must handle source-specific season availability.

## WSL Scheduler Availability

Local WSL cron collection depends on the Debian/WSL environment and cron service being available. GitHub Actions daily ingestion reduces dependence on the workstation for the production daily refresh, but local hourly collection can still stop across host/WSL lifecycle events.

## PYTHONPATH Under Cron

The local scheduled runner imports the repository package. Cron must set `PYTHONPATH=.` after changing into the repository directory or imports can fail.

## Duplicate Volume

RSS providers frequently expose the same articles across successive polls. This is expected. Cortex fingerprint deduplication prevents repeated evidence from changing score history. Operational views should distinguish normalized events from newly accepted Cortex events.

## Local JSONL Growth

Cortex, football state, and local observability history can grow continuously. Retention, compaction, archival, or database migration should be evaluated as history becomes substantial.

## Source Overlap

Additional providers should not be added solely to increase volume. New sources should be evaluated for unique evidence, reliability, timeliness, and fantasy-football value.