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

**In progress — core ingestion and source-expansion milestones complete**

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

**Complete**

Implemented:

- Canonical-event repository abstraction
- Append-only JSON canonical-event persistence
- Repository-backed `EvidenceAggregator`
- Restart-safe canonical identity
- Cross-source corroboration
- Duplicate-evidence suppression
- Player-aware event fingerprints for multi-player articles
- Shared article provenance with distinct player event identity

The repository is the authoritative source for canonical evidence identity rather than process-local aggregator memory.

#### C3 — Source Expansion & Statistical Context

**Complete**

Implemented:

- Named ESPN NFL RSS adapter
- Named RotoWire NFL RSS adapter
- Live multi-source ingestion smoke test
- Player suffix and possessive alias hardening
- Multi-player article extraction
- nflverse / nflreadpy weekly player-stat adapter
- Dedicated structured-stat interpretation path
- Historical rolling player baselines
- Workload and production deltas
- Team carry share
- Team target share
- QB pass-attempt share
- Opportunity-share trend adjustments
- Explainable statistical context preserved in signal evidence

Live RSS resolution improved during C3 from approximately **64% to 76%** after alias hardening while retaining non-fantasy NFL entities for future relationship reasoning.

Structured statistical events bypass news-keyword sentiment so factual box-score evidence is interpreted quantitatively rather than as headline sentiment.

Current structured evidence path:

```text
nflverse weekly player data
        ↓
NFLVersePlayerStatsAdapter
        ↓
SourceRecord
        ↓
EventNormalizer
        ↓
RawEvent
        ↓
StatisticalEventInterpreter
        ↓
Current performance
+ prior-week baseline
+ workload deltas
+ team opportunity share
        ↓
Cortex Signal
```

Focused C3.7 regression gate: **43 passing tests** across team-share context, contextual statistical reasoning, structured-stat interpretation, nflverse adaptation, and signal processing.

### Next Phase C Focus

The remaining Phase C work is operational rather than another statistical heuristic layer:

- Ingestion reliability
- Retry/backoff and timeout handling
- Provider failure isolation
- Source health reporting
- Ingestion observability
- Additional source categories where they materially improve evidence coverage

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
