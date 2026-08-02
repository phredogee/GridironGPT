# GridironGPT Known Issues

This document tracks active technical limitations, unresolved architectural concerns, and areas requiring future validation. Completed work belongs in `CHANGELOG.md`.

---

# Data Ingestion

## Source Coverage

The unified ingestion architecture is operational for ESPN NFL RSS, RotoWire NFL RSS, and nflverse weekly player statistics. Player matching, multi-player extraction, canonical evidence identity, structured-stat interpretation, historical context, and team opportunity share are implemented.

### Remaining Work

- Injury-report-specific structured ingestion
- Transactions
- Practice participation
- Snap counts / route participation where reliable data is available
- Red-zone usage
- Team statistics where they materially improve player context
- Evaluate additional providers for reliability, licensing, and fantasy relevance

Additional sources should be added for evidence value, not simply source count.

---

## Ingestion Reliability

This is the primary active Phase C risk.

External providers do not yet share a complete production-oriented reliability layer.

### Needed

- Retry handling
- Exponential backoff
- Timeouts
- Rate-limit awareness
- Source failure isolation
- Cache strategy
- Partial recovery
- Structured ingestion logging
- Source health monitoring

A failed external provider should not prevent unrelated providers from supplying Cortex with events.

---

## Ingestion Observability

The system does not yet provide complete operational metrics for ingestion.

Needed metrics include:

- Events received
- Events accepted
- Events rejected
- Duplicate events
- Canonical events created
- Source failures
- Last successful ingestion
- Processing latency
- Events by provider

---

# Player Matching

The matcher prioritizes precision while supporting suffixless aliases, football names, possessive normalization, and multi-player extraction.

## Known Limitations

- Ambiguous surnames may intentionally be ignored.
- Headlines without identifiable player names may be skipped.
- Rare nickname/provider aliases may still be absent.
- Some current/deep-roster players may lag nflverse catalog coverage.
- Some nflverse depth-chart entries do not contain GSIS IDs.

The relationship builder mitigates missing GSIS IDs with normalized player-name fallback matching.

---

# Statistical Reasoning

Structured weekly player statistics now have a dedicated quantitative interpretation path.

Implemented context includes:

- Rolling prior-game baselines
- Workload deltas
- Production deltas
- Carry share
- Target share
- Pass-attempt share
- Opportunity-share trend adjustment
- Explainable statistical evidence

## Remaining Limitations

The current weights remain deterministic heuristics rather than historically calibrated fantasy models.

Future improvements may include:

- Rolling-window configuration
- Position-specific thresholds
- Strength-of-schedule adjustments
- Opponent normalization
- Snap share
- Route participation
- Red-zone usage
- Efficiency metrics
- Historical outcome calibration

---

# Signal Confidence Calibration

Cortex supports evidence-aware confidence, corroboration, contradiction penalties, and additional confidence from statistical history, but values remain heuristic.

### Future Work

- Historical accuracy tracking
- Source reliability weighting
- Probabilistic calibration
- Provider-specific reliability
- Signal-category calibration
- Confidence-vs-outcome analysis

---

# Contradiction Detection

Contradiction detection is implemented and integrated into Cortex reasoning.

Current behavior supports positive/negative evidence conflict, conflict severity, confidence penalties, source attribution, and neutral-source exclusion.

## Remaining Limitation

Detection remains primarily rule/keyword driven and may miss semantically incompatible reports expressed with different wording.

Future work includes semantic contradiction classification, temporal precedence, injury-status state models, source chronology, and superseding reports.

---

# Relationship Graph

The NFL relationship graph is depth-aware and dynamically refreshable. Current construction uses nflverse player catalog and depth charts, active-roster status, latest team snapshots, fantasy-position filtering, and depth-rank filtering.

Development graph size is approximately 579 active relationships across all 32 NFL teams.

## Relationship Refresh Scheduling

Refresh/diff logic is implemented, but orchestration still requires an external trigger. Scheduling should eventually vary by offseason, training camp, preseason, regular season, trade deadline, and injury-driven depth changes.

## Relationship Calibration

Strength, confidence, semantic multipliers, and hop decay remain heuristic. Statistical opportunity-share data can eventually contribute to relationship calibration.

---

# Multiple Simultaneous Events

Individual and multi-player article processing are covered, but several distinct developments occurring in a short window still require broader validation.

Examples include starter injury, backup promotion, veteran signing, and committee announcement.

Future work: event ordering, temporal precedence, competing-signal resolution, score-update consolidation, and recommendation stability.

---

# Historical Validation

Cortex has not yet been comprehensively replayed against historical NFL seasons.

Future replay should measure signal accuracy, propagation accuracy, recommendation accuracy, prediction accuracy, confidence calibration, relationship effectiveness, scoring performance, and false-positive/false-negative rates.

Historical validation should eventually drive parameter calibration.

---

# Performance and Scalability

Current graph traversal and JSONL persistence are sufficient for development but production-scale performance is not benchmarked.

Benchmark areas include graph traversal latency, ingestion throughput, repository read latency, JSONL growth, memory use, concurrent processing, canonical-event clustering, and historical scorecard queries.

---

# JSONL Persistence

Current local knowledge includes JSON/JSONL repositories for events, canonical events, player scorecards, and relationships.

Known limitations include linear scans, increasing read cost, limited concurrent writes, no transactions, limited queries, and manual archival. Repository abstractions intentionally permit later database/cloud migration.

---

# Cortex Inspector

The Inspector exposes pipeline status, evidence/confidence, cognitive trace, evidence graph, propagation, predictions, scorecards, history, explanations, and diagnostics.

Presentation improvements remain non-blocking: interactive graph nodes, event markers, side-by-side comparison, propagation filtering, graph search, and historical replay.

---

# Legacy Architecture / Standalone Cortex Extraction

Legacy GridironGPT components remain while Cortex extraction continues.

Remaining concerns:

- Retire obsolete semantic/CLI paths after replacement coverage exists
- Complete standalone Cortex repository separation
- Finalize stable public API
- Reduce GridironGPT-specific assumptions inside Cortex
- Formalize extension interfaces and package versioning
- Prevent duplicate implementations between repositories

---

# Resolved During Phase C So Far

The following are no longer active known issues:

- Common `SourceAdapter` / `SourceRecord` ingestion contract
- Common event normalization
- Named ESPN and RotoWire RSS adapters
- nflverse weekly player-stat adapter
- Canonical-event persistence
- Restart-safe evidence aggregation
- Duplicate evidence snapshot prevention
- Cross-source corroboration persistence
- Player-aware identity for multi-player articles
- Multi-player article extraction
- Jr./Sr. suffix matching
- Football-name aliases
- Possessive-name normalization
- Dedicated structured-stat interpretation
- Rolling player statistical baselines
- Workload and production trend context
- Carry-share context
- Target-share context
- Pass-attempt-share context

---

# Current Engineering Status

| Component | Status |
|---|---|
| Cortex Facade | ✅ Complete |
| Knowledge Graph / Propagation | ✅ Complete |
| Multidimensional Scoring | ✅ Complete |
| Prediction / Recommendation / Explanation | ✅ Complete |
| Unified Ingestion Architecture | ✅ Complete |
| Canonical Evidence Persistence | ✅ Complete |
| Cross-Source Corroboration | ✅ Complete |
| Multi-Player Extraction | ✅ Complete |
| NFL News Adapters | ✅ Complete |
| nflverse Player Stats | ✅ Complete |
| Contextual Statistical Reasoning | ✅ Complete |
| Team Opportunity Share | ✅ Complete |
| Source Reliability Layer | ▶ Next |
| Ingestion Observability | Planned |
| Historical Validation | 🔮 Future |
| Learned Relationships | 🔮 Future |

---

# Primary Next Risk

The main question is no longer whether Cortex can normalize and interpret multiple evidence types.

The next risk is:

```text
Can ingestion remain healthy when a provider is slow,
unavailable, rate-limited, or returns malformed data?
```

That is the next Phase C engineering target.
