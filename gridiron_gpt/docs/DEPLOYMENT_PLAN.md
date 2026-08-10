# GridironGPT Deployment Plan

## Purpose

This document defines the path from the validated local v1.0 architecture to a production deployment. Production infrastructure should preserve the engine boundaries already proven locally rather than redesigning Cortex around a hosting vendor.

## Current Deployment Readiness

The v1.0 local architecture has verified:
- provider adapters and shared ingestion
- automatic `RawEvent` handoff into Cortex
- fail-open downstream processing
- persistent Cortex event history
- persistent player scorecards
- restart-safe Replay reconstruction
- shared Streamlit Cortex facade composition
- a 702-test regression baseline

Production/cloud deployment remains post-v1 work.

## Logical Production Topology

```text
External NFL Providers
        ↓
Scheduled Ingestion Worker
        ↓
IngestionService
        ↓
RawEvent
        ↓
Cortex Processing Worker / Service
        ↓
Durable Repositories
  ├─ event history
  ├─ scorecards
  ├─ deduplication state
  ├─ relationships/history
  └─ ingestion runs
        ↓
GridironGPT Web Application
        ↓
Dashboard / Advisor / Explorer / Replay
```

The exact cloud vendor is intentionally unspecified. Repository and service contracts should make the topology portable.

## Phase 1 — Release Candidate

Before any production deployment:
1. Complete v1.0 documentation stabilization.
2. Run the full regression suite.
3. Perform the Streamlit smoke test.
4. Reconcile the development branch with `main` documentation changes.
5. Establish the v1.0 merge/tag boundary.
6. Record environment/dependency versions used for the release candidate.

## Phase 2 — Environment and Packaging

Define:
- supported Python version
- dependency lock strategy
- application start command
- worker start command
- environment-variable contract
- secrets required by providers/databases
- writable/persistent filesystem assumptions

No secret values should be committed to the repository.

## Phase 3 — Durable Persistence

Replace or wrap local JSON/JSONL repositories where production concurrency or durability requires it.

Requirements:
- preserve repository interfaces
- retain correlation IDs and provenance
- make event history append-safe
- make scorecard updates concurrency-safe
- preserve deduplication guarantees
- support backup and restore
- provide migration tooling from local development state where useful

A database choice should follow these requirements rather than drive Cortex design.

## Phase 4 — Background Ingestion

Move scheduled provider ingestion outside the interactive Streamlit request lifecycle.

Requirements:
- scheduler or worker process
- per-provider timeout/retry policy
- fail-open Cortex handoff semantics
- durable ingestion-run history
- provider freshness metrics
- alerting on sustained provider failures
- safe restart behavior

## Phase 5 — Web Application

Deploy Streamlit or a future web frontend as a read/interaction layer over durable intelligence state.

Requirements:
- health endpoint or platform health check
- environment-specific configuration
- no reliance on process-local state for durable decisions
- controlled caching
- authentication before exposing private league/user data
- session isolation

## Phase 6 — Authentication and Multi-user Support

Before supporting multiple users/leagues:
- define user identity model
- define league ownership/membership
- authorize league-specific reads/writes
- isolate private roster/league data
- define commissioner permissions
- audit sensitive mutations

## Phase 7 — Observability

Production monitoring should cover:
- provider success/failure rates
- provider freshness
- ingestion latency
- Cortex processing failures
- processing latency
- event volume
- deduplication counts
- persistence failures
- Replay/persistence integrity
- application errors

Logs should include correlation IDs where possible so one source event can be traced through ingestion and Cortex.

## Phase 8 — Backup and Recovery

Define:
- database backup schedule
- retention window
- restore procedure
- recovery-time objective
- recovery-point objective
- validation of restored Replay/event history

A recovery test should confirm that historical Cortex decisions remain replayable after restore.

## Security Requirements

- Store secrets in deployment-platform secret management.
- Never log credentials or provider tokens.
- Use least-privilege database credentials.
- Protect write-capable administrative/commissioner operations.
- Keep dependencies patched.
- Separate development and production configuration.
- Review externally reachable ingestion/admin endpoints before exposure.

## Release Strategy

Recommended sequence:

```text
v1.0 local release candidate
        ↓
private/staging deployment
        ↓
live-provider soak test
        ↓
persistence/restart validation
        ↓
monitoring + backup validation
        ↓
production pilot
        ↓
production release
```

## Rollback Strategy

A deployment must be able to roll back application code without discarding persisted Cortex history. Schema/repository migrations should therefore be backward-compatible where practical and backed up before destructive changes.

## Production Acceptance Criteria

A production deployment should not be considered stable until:
1. Scheduled ingestion operates independently of the UI.
2. Durable persistence survives application/worker restarts.
3. Duplicate events remain idempotent.
4. Replay works against production persistence.
5. Provider failures are isolated and observable.
6. Cortex failures do not cause provider refetch storms.
7. Monitoring and alerting are active.
8. Backup and restore have been tested.
9. Authentication/authorization protect user and league data where applicable.
10. A production smoke/regression procedure is documented and repeatable.
