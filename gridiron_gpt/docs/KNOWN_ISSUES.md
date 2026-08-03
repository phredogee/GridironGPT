# GridironGPT Known Issues

This document tracks active technical limitations, unresolved architectural concerns, and areas requiring future validation. Completed work belongs in project history rather than remaining listed as an active blocker.

---

# Data Coverage

The Phase C ingestion architecture is complete and operational for ESPN NFL RSS, RotoWire NFL RSS, and nflverse weekly player statistics.

Remaining evidence gaps are now **coverage questions**, not ingestion-architecture blockers.

Potential additions include:

- Structured injury reports
- Transactions
- Practice participation
- Snap counts
- Route participation
- Red-zone usage
- Team statistics where they materially improve player context

Additional providers should be added only when they provide meaningful evidence value, reliable access, and acceptable licensing/usage terms.

---

# External Provider Limitations

The ingestion reliability layer now supports retries, exponential backoff, timeouts, rate-limit awareness, source isolation, structured provider outcomes, health state, and run observability.

Remaining limitations:

- Python thread-based attempt timeouts cannot forcibly terminate a blocked underlying provider call.
- Individual HTTP/provider clients should still use request-level network timeouts where supported.
- Provider-specific rate-limit detection must be implemented by adapters when a source exposes throttling information.
- Provider health is currently development-oriented and may later require durable cross-process persistence.

---

# Player Matching

The matcher prioritizes precision while supporting suffixless aliases, football names, possessive normalization, and multi-player extraction.

Known limitations:

- Ambiguous surnames may intentionally be ignored.
- Headlines without identifiable player names may be skipped.
- Rare nickname/provider aliases may still be absent.
- Some deep-roster players may lag current catalog coverage.
- Some nflverse depth-chart entries do not contain stable IDs.

Normalized-name fallback mitigates missing identifiers where practical.

---

# Statistical Reasoning

Structured player statistics have a dedicated quantitative interpretation path with rolling baselines, workload/production deltas, and team opportunity share.

The remaining limitation is **calibration**.

Current statistical weights are deterministic heuristics rather than historically validated fantasy models.

Future improvements may include:

- Position-specific thresholds
- Configurable rolling windows
- Strength-of-schedule adjustment
- Opponent normalization
- Snap share
- Route participation
- Red-zone usage
- Efficiency metrics
- Historical outcome calibration

This belongs primarily to Phase E — Intelligence Calibration.

---

# Football State / Context

Cortex can reason over events, relationships, and persisted score state, but it does not yet expose a complete canonical representation of a player's current football situation.

This is the primary Phase D gap.

Needed context includes:

- Current roster/team state
- Depth-chart role
- Active/inactive status
- Injury/availability state
- Transaction history and role movement
- Schedule/opponent context
- Durable player/team history

---

# Injury / Availability State

Injury-related news can be interpreted as signals, but availability is not yet modeled as a durable state machine with chronology and superseding reports.

Examples that should eventually be represented explicitly:

```text
healthy
limited
questionable
doubtful
out
injured reserve / PUP
suspended
returning
```

This is planned for Phase D.

---

# Transactions and Role Movement

Roster and depth-chart relationships exist, but signed/released/traded/waived/promoted/demoted transitions are not yet represented as first-class durable football state changes.

Phase D should make these transitions update current context and, where appropriate, relationship state.

---

# Signal Confidence Calibration

Cortex supports evidence-aware confidence, corroboration, contradiction penalties, and statistical-history context, but confidence values remain heuristic.

Future work:

- Historical accuracy tracking
- Source reliability weighting
- Provider-specific reliability
- Signal-category calibration
- Confidence-vs-outcome analysis
- Probabilistic calibration where useful

---

# Contradiction Detection

Contradiction detection supports polarity conflict, severity, confidence penalties, source attribution, and neutral-source exclusion.

Remaining limitations:

- Detection remains primarily rule/keyword driven.
- Temporal precedence is limited.
- Superseding status reports are not yet modeled explicitly.
- Semantically incompatible reports may be missed when wording differs substantially.

Phase D availability state and Phase E historical calibration should improve this area.

---

# Relationship Graph

The NFL relationship graph is depth-aware, persistent, dynamically refreshable, and semantically propagated.

Current development graph size is approximately 579 active relationships across all 32 NFL teams.

Remaining limitations:

- Refresh orchestration still requires an external trigger.
- Strength/confidence values remain heuristic.
- Semantic coverage does not yet include the full football ecosystem.
- Opportunity-share data is not yet used to calibrate relationship strength.

Potential future relationships should be added only when they provide meaningful fantasy intelligence.

---

# Multiple Simultaneous Events

Single events and multi-player articles are covered, but several distinct developments occurring in a short time window still require broader validation.

Example:

```text
Starting RB injured
Backup promoted
Team signs veteran RB
Coach announces committee
```

Future work includes temporal precedence, competing-signal resolution, score-update consolidation, and recommendation stability.

---

# Historical Validation

Cortex has not yet been comprehensively replayed against historical NFL seasons.

This is the central Phase E requirement.

Historical replay should measure:

- Signal accuracy
- Propagation accuracy
- Recommendation accuracy
- Prediction accuracy
- Confidence calibration
- Relationship effectiveness
- Category-specific scoring behavior
- False-positive and false-negative rates

---

# Persistence / Scalability

JSON/JSONL repositories are appropriate for the current development stage but are not intended as the final production persistence architecture.

Known limitations:

- Linear file scans
- Increasing read cost as history grows
- Limited concurrent-write support
- No transactional guarantees
- Limited query capabilities
- Manual archival requirements

Repository abstractions intentionally permit later database/cloud migration.

---

# Standalone Cortex Extraction

Gridiron Cortex is moving toward an independently reusable engine/library.

Remaining concerns:

- Finalize stable public API
- Reduce GridironGPT-specific assumptions inside Cortex
- Formalize extension/plugin interfaces
- Establish package versioning
- Determine long-term repository ownership of shared models
- Prevent duplicated implementations between repositories

The extraction should not interrupt active GridironGPT development.

---

# Current Engineering Status

| Component | Status |
|---|---|
| Cortex Foundation | ✅ Complete |
| Intelligence & Reasoning | ✅ Complete |
| Unified Ingestion Architecture | ✅ Complete |
| Canonical Evidence / Deduplication | ✅ Complete |
| Source Reliability | ✅ Complete |
| Ingestion Observability | ✅ Complete |
| Football Knowledge & Context | ▶ Phase D |
| Historical Calibration | Planned |
| Fantasy Decision Engine | Planned |
| Production Persistence / Cloud | Future |

---

# Primary Next Risk

The primary engineering question has shifted again.

It is no longer:

```text
Can Cortex reliably receive clean evidence?
```

Phase C established that architecture.

The next question is:

```text
Can Cortex combine new evidence with a reliable,
current representation of the player's real football situation?
```

That is the primary problem Phase D is intended to solve.
