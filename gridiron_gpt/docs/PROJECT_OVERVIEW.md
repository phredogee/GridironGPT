# GridironGPT Project Overview

## Vision

GridironGPT is an AI-powered fantasy football intelligence platform that transforms raw NFL information into structured, persistent, explainable fantasy intelligence.

At the center of the platform is **Gridiron Cortex**, the reusable intelligence engine responsible for understanding football events, reasoning over relationships, maintaining historical state, and producing recommendations with traceable evidence.

GridironGPT is one client of Cortex. Future dashboards, APIs, draft tools, league integrations, and other applications should consume Cortex through stable interfaces rather than duplicating intelligence logic.

---

## Core Architecture

```text
External NFL Sources
        ↓
Unified Ingestion Layer
        ↓
Normalization
        ↓
Evidence Aggregation / Canonical Identity
        ↓
Gridiron Cortex
        ↓
Understand → Reason → Evaluate → Predict → Decide → Explain
        ↓
Persistent Memory / Knowledge
        ↓
GridironGPT and Future Clients
```

---

## Gridiron Cortex

Gridiron Cortex is an event-driven football intelligence engine that converts evidence into persistent player and team intelligence.

Core capabilities include:

- Entity resolution
- Football signal classification
- Canonical event aggregation
- Multi-source evidence corroboration
- Relationship-aware propagation
- Multidimensional player scoring
- Trend and contradiction reasoning
- Prediction
- Recommendation generation
- Explainable evidence chains and graphs
- Persistent player scorecards
- Persistent event and relationship history

---

## Current Development Status

### Phase A — Cortex Foundation

**Complete**

Established the independent Cortex engine, repository abstractions, persistence, scorecards, event deduplication, and application boundary.

### Phase B — Intelligence & Reasoning

**Complete**

Established evidence-aware reasoning, NFL relationship graphs, semantic propagation, multidimensional scoring, prediction, recommendation intelligence, and relationship-aware explainability.

### Phase C — Data Ingestion

**In progress**

#### C1 — Ingestion Architecture

**Complete**

Implemented:

- `SourceAdapter`
- `SourceRecord`
- `EventNormalizer`
- `RSSSourceAdapter`
- `IngestionService`
- Ingestion-to-Cortex integration

#### C2 — Deduplication & Evidence Identity

**In progress**

Completed milestones:

- **C2.1 Canonical persistence** — repository abstraction and append-only JSONL canonical-event persistence.
- **C2.2 Repository-backed EvidenceAggregator** — canonical state now survives process restarts, corroborating evidence creates updated snapshots, and duplicate evidence does not create redundant snapshots.

C2.2 validation passed with **18 focused tests** covering evidence aggregation, canonical persistence, restart recovery, corroboration, and duplicate-snapshot prevention.

Current evidence path:

```text
RawEvent
   ↓
EvidenceAggregator
   ↓
Canonical event key
   ↓
CanonicalEventRepository.get()
   ↓
Existing event?
   ├── No  → create canonical event
   └── Yes → merge new evidence
   ↓
Aggregate confidence
   ↓
CanonicalEventRepository.save()
   ↓
CanonicalEvent
```

The repository is now the authoritative source for canonical evidence identity rather than process-local aggregator memory.

---

## Persistence Strategy

Cortex currently uses repository abstractions with JSON/JSONL implementations.

This provides:

- Replaceable storage infrastructure
- Append-only audit history
- Persistent scorecard state
- Persistent relationship state
- Persistent canonical evidence state
- Restart-safe evidence aggregation

Future infrastructure may move to SQLite, PostgreSQL, or cloud-backed persistence without requiring intelligence logic to depend directly on a storage implementation.

---

## Design Principles

1. **Cortex owns intelligence.** Applications remain thin clients.
2. **Evidence comes before conclusions.** Recommendations must trace back to observable inputs.
3. **Preserve provenance.** Cortex should know where evidence originated and how it affected a conclusion.
4. **Persist history.** Intelligence changes should remain auditable over time.
5. **Use football semantics.** Relationships and signal meaning matter more than generic weighting alone.
6. **Avoid duplicate intelligence effects.** Multiple providers reporting the same development should strengthen evidence, not repeatedly change scores.
7. **Keep infrastructure replaceable.** Repository contracts should isolate Cortex from storage implementations.
8. **Protect the engine boundary.** Gridiron Cortex remains the reusable intelligence core.

---

## Long-Term Direction

Planned platform capabilities include:

- Additional structured NFL data sources
- Ingestion reliability and source-health monitoring
- Gridiron Codex historical knowledge
- Draft-class intelligence
- Historical prediction evaluation
- REST API access
- League-specific fantasy intelligence
- Advanced dashboard and graph visualization

The long-term objective is for Cortex to answer:

> Why does this football event matter, who does it affect, how confident are we, and what should a fantasy manager do about it?
