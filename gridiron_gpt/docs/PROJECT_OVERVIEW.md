# GridironGPT Project Overview

## Vision

GridironGPT is an AI-powered fantasy football intelligence platform that transforms raw NFL information into structured, persistent, explainable fantasy intelligence.

At the center is **Gridiron Cortex**, the reusable intelligence engine responsible for understanding football events, reasoning over relationships, maintaining historical state, and producing recommendations with traceable evidence.

## Core Architecture

```text
External NFL Sources
        ↓
Unified Ingestion Layer
        ↓
Normalization / Canonical Evidence
        ↓
Gridiron Cortex
        ↓
Understand → Reason → Evaluate → Predict → Decide → Explain
        ↓
Persistent Memory / Knowledge
        ↓
GridironGPT and Future Clients
```

## Current Development Status

### Phase A — Cortex Foundation
**Complete**

### Phase B — Intelligence & Reasoning
**Complete**

### Phase C — Data Ingestion
**Complete**

#### C1 — Ingestion Architecture ✅

- `SourceAdapter` / `SourceRecord`
- `EventNormalizer`
- RSS adapters
- `IngestionService`
- Ingestion-to-Cortex integration

#### C2 — Deduplication & Evidence Identity ✅

- Persistent canonical-event repository
- Restart-safe identity
- Cross-source corroboration
- Duplicate-evidence suppression
- Multi-player article identity

#### C3 — Source Expansion & Statistical Context ✅

- ESPN NFL and RotoWire NFL
- Multi-player extraction
- Player alias hardening
- nflverse / nflreadpy player statistics
- Structured statistical interpretation
- Rolling historical baselines
- Workload/production deltas
- Carry, target, and pass-attempt share
- Explainable opportunity trends

#### C4 — Ingestion Reliability ✅

- Provider execution boundary
- Failure isolation
- Retry and exponential backoff
- Per-attempt timeout handling
- Rate-limit / Retry-After awareness
- Structured provider outcomes
- Provider health states: healthy, degraded, unavailable

#### C5 — Ingestion Observability ✅

- Run-level summary metrics
- Provider diagnostics
- Run duration
- Records/events totals
- Health state attached to diagnostics
- Error type/message reporting
- Unique run IDs and timestamps
- Append-only JSONL ingestion-run history
- Latest-run retrieval

Observable execution path:

```text
Providers
   ↓
Reliable execution boundary
   ↓
ProviderIngestionResult
   ↓
ProviderHealthTracker
   ↓
IngestionRunSummary
   ↓
JsonlIngestionRunRepository
```

A complete run can now answer:

- Which providers ran?
- Which succeeded or failed?
- Which are degraded/unavailable?
- How many records and events were produced?
- How many attempts were required?
- What error occurred?
- How long did the run take?
- What happened in prior ingestion runs?

## Persistence Strategy

Cortex and ingestion use repository abstractions with JSON/JSONL development implementations. Current persisted history includes events, canonical evidence, player scorecards, relationships, and ingestion runs. Storage can later migrate to SQLite, PostgreSQL, or cloud infrastructure without coupling intelligence logic to a specific implementation.

## Design Principles

1. Cortex owns intelligence; providers supply evidence.
2. Evidence comes before conclusions.
3. Preserve provenance and audit history.
4. Persist meaningful state transitions.
5. Use football semantics rather than generic weighting alone.
6. Corroboration strengthens evidence without duplicating score effects.
7. Keep infrastructure replaceable behind contracts.
8. A failing provider must not take down healthy ingestion sources.
9. Operational behavior should be observable, not inferred from logs alone.

## Next Major Direction

Phase C is closed. Future source additions should be evidence-driven rather than extensions of the ingestion architecture itself.

Potential subsequent work includes Gridiron Codex historical knowledge, draft-class intelligence, historical prediction evaluation/calibration, REST API access, league-specific intelligence, and advanced visualization.

The long-term objective remains:

> Why does this football event matter, who does it affect, how confident are we, and what should a fantasy manager do about it?
