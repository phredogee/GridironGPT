# GridironGPT Roadmap

## Vision

Build **Gridiron Cortex**, an explainable football intelligence engine that transforms NFL evidence into persistent, contextual, actionable fantasy-football intelligence.

GridironGPT and future applications remain clients of Cortex rather than owning intelligence logic themselves.

```text
NFL Evidence
    ↓
Unified Ingestion
    ↓
Gridiron Cortex
    ↓
Football Knowledge / Historical Context
    ↓
Fantasy Decisions
    ↓
Applications / APIs / Dashboards
```

---

# Current Status

| Phase | Area | Status |
|---|---|---|
| A | Cortex Foundation | ✅ Complete |
| B | Intelligence & Reasoning | ✅ Complete |
| C | Data Ingestion | ✅ Complete |
| D | Football Knowledge & Context | ▶ Next |
| E | Intelligence Calibration | Planned |
| F | Fantasy Decision Engine | Planned |
| G | Product / API Integration | Planned |
| H | Production & Cloud | Long-term |

Phase C closed with a focused reliability/observability regression gate of:

```text
43 passed
```

The full project test suite should continue to be run at major phase boundaries.

---

# Phase A — Cortex Foundation ✅

Established the independent Cortex engine and its application boundary, including orchestration, entity resolution, signal processing, relationship reasoning, multidimensional scoring, prediction, recommendation, explainability, and persistent repositories.

---

# Phase B — Intelligence & Reasoning ✅

Established domain-aware football reasoning, including canonical evidence, corroboration, contradiction detection, the NFL knowledge graph, semantic multi-hop propagation, category-aware scoring, trend reasoning, prediction/recommendation integration, and relationship-aware explanations.

---

# Phase C — Data Ingestion ✅

Established a resilient, normalized, observable multi-source ingestion layer.

## C1 — Ingestion Architecture ✅

- `SourceAdapter` / `SourceRecord`
- `EventNormalizer`
- RSS adapter foundation
- `IngestionService`
- Ingestion-to-Cortex integration

## C2 — Deduplication & Evidence Identity ✅

- Persistent canonical-event repository
- Restart-safe canonical identity
- Duplicate-evidence suppression
- Cross-source corroboration
- Shared article provenance
- Player-specific identity for multi-player articles

## C3 — Source Expansion & Statistical Context ✅

- ESPN NFL RSS
- RotoWire NFL RSS
- nflverse / nflreadpy weekly player statistics
- Player alias hardening
- Multi-player extraction
- Structured statistical interpretation
- Rolling historical baselines
- Workload and production deltas
- Carry share, target share, and pass-attempt share
- Explainable opportunity trends

## C4 — Ingestion Reliability ✅

- Provider execution boundary
- Failure isolation
- Retry and exponential backoff
- Per-attempt timeout handling
- Rate-limit / Retry-After awareness
- Structured provider outcomes
- Provider health states: healthy, degraded, unavailable

## C5 — Ingestion Observability ✅

- Run-level summaries
- Provider diagnostics
- Run duration
- Record/event totals
- Error reporting
- Run IDs and timestamps
- Append-only JSONL ingestion-run history
- Latest-run retrieval

Phase C established the principle that a provider failure degrades ingestion rather than taking down the pipeline.

---

# Phase D — Football Knowledge & Context ▶

## Objective

Teach Cortex the durable football state surrounding incoming events so it can reason about more than an isolated headline or box score.

Phase D should enrich the existing Cortex pipeline rather than create a second intelligence system.

## D1 — Canonical NFL State

Create queryable current-state models for players, teams, rosters, depth-chart roles, active/inactive status, position, and role.

First target question:

> What is this player's current football situation?

## D2 — Availability & Injury State

Represent current availability explicitly rather than only through news sentiment. Support chronology and superseding reports.

## D3 — Transactions & Role Movement

Track signed, released, traded, waived, promoted, demoted, practice-squad, and depth-chart transitions. These changes should update football context and relationships.

## D4 — Opportunity Context

Expand durable role indicators where reliable data exists: snap share, route participation, target share, carry share, red-zone usage, and team opportunity concentration.

## D5 — Schedule & Opponent Context

Add upcoming opponent, home/away, bye week, and evidence-based matchup context for forward-looking reasoning.

## D6 — Rookie / Draft-Class Knowledge

Capture draft year, round/pick, college, position, team, and rookie status.

## D7 — Gridiron Codex Foundation

Establish durable historical knowledge for career history, team history, injury history, role history, seasonal production, historical relationships, and coaching/system context.

### Phase D Success Criteria

Phase D is complete when Cortex can combine a new event with reliable current and historical football context and explain which contextual facts affected its reasoning.

---

# Phase E — Intelligence Calibration

Measure whether Cortex's rules and predictions are actually useful through historical replay, outcome tracking, confidence calibration, signal-quality measurement, relationship-effectiveness measurement, and parameter calibration.

---

# Phase F — Fantasy Decision Engine

Turn Cortex intelligence into concrete fantasy decisions: draft intelligence, waivers/FAAB, start/sit, trades, player comparison, breakout/risk detection, handcuffs, roster weakness, and league-aware recommendations.

---

# Phase G — Product / API Integration

Expose stable Cortex capabilities to clients through player/recommendation/evidence APIs, rankings, waiver and draft interfaces, dashboard modernization, and league integrations while preserving the private engine boundary.

---

# Phase H — Production & Cloud

Move proven capabilities into continuously operating infrastructure: scheduling, durable database storage, queues/workers, caching, secrets, monitoring, backups, authentication, deployment, and cost controls.

Cloud complexity should follow proven product value rather than precede it.

---

# Guiding Principles

1. Cortex owns intelligence.
2. GridironGPT owns football-domain integration.
3. Evidence comes before conclusions.
4. Preserve provenance and history.
5. Prefer football semantics over generic math.
6. Avoid graph and source noise.
7. Keep infrastructure replaceable.
8. A provider failure must not take down unrelated evidence.
9. New phases should enrich the existing reasoning pipeline, not create parallel intelligence systems.
10. Calibrate heuristics with historical outcomes before making them more complex.

---

# Long-Term Goal

Gridiron Cortex should answer:

> **What happened, what does the player's football context tell us about it, who else is affected, how confident are we, what is likely to happen next, and what should a fantasy manager do?**
