# GridironGPT Roadmap

## Vision

Build **Gridiron Cortex**, an explainable football intelligence engine capable of transforming raw NFL information into structured, persistent, and actionable fantasy football intelligence.

Gridiron Cortex is the core intellectual property of the project.

GridironGPT, dashboards, APIs, draft tools, league integrations, and future applications should remain clients of Cortex rather than owning intelligence logic themselves.

The long-term architecture is:

```text
NFL Data Sources
      ↓
Data Ingestion
      ↓
Gridiron Cortex
      ↓
Gridiron Codex / Persistent Knowledge
      ↓
Applications / APIs / Dashboards
```

---

# Current Status

| Phase | Area | Status |
|---|---|---|
| A | Cortex Foundation | ✅ Complete |
| B | Intelligence & Reasoning | ✅ Complete |
| C | Data Ingestion | ▶ Next |
| D | Gridiron Codex | Planned |
| E | Intelligence Expansion | Planned |
| F | Natural Language Intelligence | Planned |
| G | Platform | Planned |
| H | Commercialization | Long-term |

Current automated test baseline:

```text
274 passed
```

---

# Phase A — Cortex Foundation ✅

## Objective

Extract football intelligence from the application layer and establish Gridiron Cortex as an independent engine.

## Completed

### Core Engine

- Cortex Facade
- Cortex Engine orchestration
- Entity Resolver
- Signal Processor
- Relationship Engine
- Score Engine
- Recommendation Engine
- Explanation Engine
- Prediction Engine

### Persistent Knowledge

- Event Repository
- Player Scorecard Repository
- Relationship Repository
- Knowledge Service
- JSONL persistence
- Event deduplication
- Scorecard history
- Relationship history

### Engine Models

Structured models now represent:

- Raw events
- Canonical events
- Source evidence
- Entities
- Signals
- Impacts
- Score updates
- Player scorecards
- Recommendations
- Predictions
- Relationships
- Evidence chains
- Evidence graphs
- Intelligence context

### Application Boundary

`CortexFacade` provides the primary application-facing entry point into the engine.

Applications should not need direct knowledge of Cortex persistence implementations or internal reasoning components.

## Status

**COMPLETE**

---

# Phase B — Intelligence & Reasoning ✅

## Objective

Transform Cortex from a weighted scoring pipeline into a domain-aware football reasoning engine.

Phase B established the ability to interpret evidence, reason through football relationships, propagate effects, update multidimensional player intelligence, detect uncertainty, and explain resulting recommendations.

---

## B1 — Evidence Intelligence

### Completed

- Structured source evidence
- Canonical event aggregation
- Multi-source corroboration
- Source-count tracking
- Evidence confidence
- Corroboration confidence
- Contradiction detection
- Contradiction severity
- Confidence penalties
- Conflicting-source attribution
- Neutral-source exclusion from contradiction attribution

Cortex can distinguish corroborating evidence from genuinely conflicting evidence rather than treating every source as equally contradictory.

---

## B2 — Knowledge Graph

### Completed

- Knowledge Service
- Persistent entity relationships
- Knowledge Graph Manager
- Outgoing relationship discovery
- Incoming relationship discovery
- Relationship history
- Neighbor discovery
- Graph traversal
- Relationship path discovery
- Cycle-safe traversal

Relationships are persisted independently from the reasoning engine and accessed through the Cortex knowledge layer.

---

## B3 — NFL Relationship Graph

### Completed

- nflverse player catalog integration
- nflverse depth-chart integration
- Latest depth-chart snapshot selection
- Active-roster filtering
- Fantasy-position filtering
- GSIS ID player matching
- Normalized-name fallback matching
- Depth-rank filtering
- Depth-aware offensive relationships
- Relationship refresh service
- Relationship diffing
- Stale relationship detection
- Idempotent refresh behavior

Initial broad relationship generation produced approximately:

```text
2,940 relationships
```

Depth-aware generation reduced this to approximately:

```text
579 active fantasy-relevant relationships
```

This significantly reduces graph noise while retaining high-value offensive dependencies.

### Supported Relationship Types

- `throws_to`
- `hands_off_to`
- `backs_up`
- `target_competitor`
- `depth_chart_competitor`

The architecture remains extensible for future relationship types.

---

## B4 — Relationship Semantics

### Completed

Cortex applies different propagation behavior depending on the football meaning of a relationship.

Supported semantic behaviors include:

- Positive cooperative relationships
- Negative cooperative relationships
- Opportunity competition
- Depth-chart competition
- Backup opportunity effects
- Direction-reversing propagation

Examples:

```text
QB positive signal
      ↓ throws_to
WR positive effect
```

```text
WR positive signal
      ↓ target_competitor
Competing WR negative effect
```

```text
Starter negative signal
      ↓ backs_up
Backup positive opportunity effect
```

Relationship semantics prevent Cortex from treating every graph edge as equivalent.

---

## B5 — Propagation Engine

### Completed

- `PropagationCandidate` model
- Graph-based `PropagationPlanner`
- Multi-hop traversal
- Hop-count tracking
- Hop-decay weighting
- Relationship-strength weighting
- Relationship-confidence weighting
- Semantic multipliers
- Direction-reversing relationships
- Strongest-path selection
- Cycle protection
- Team metadata propagation
- Propagation reasoning metadata

Propagated impacts retain:

- Hop count
- Relationship strength
- Relationship confidence
- Propagation weight
- Explanation reason

This allows downstream systems to explain not only **what changed**, but **how the effect reached the player**.

---

## B6 — Signal Intelligence

### Completed

Signals now carry semantic football meaning beyond simple positive/negative sentiment.

Cortex can classify events into categories used by downstream scoring logic.

Examples include:

- Recovery
- Injury
- Opportunity
- Performance
- Availability
- General news

Structured signal evidence also supports confidence and corroboration reasoning.

---

## B7 — Multidimensional Player Scoring

### Completed

Player intelligence is no longer represented by only one generic score.

Current scorecard dimensions include:

- Overall
- Opportunity
- Health
- Hype
- Risk
- Momentum

Signal categories determine which dimensions are affected.

Example:

```text
Recovery signal
      ↓
Health ↑
Risk ↓
Momentum ↑
Overall ↑
```

Propagated impacts also retain semantic category behavior, allowing downstream players to receive contextually appropriate score changes.

All scores remain bounded within the Cortex score range.

---

## B8 — Reasoning & Intelligence Context

### Completed

- Intelligence Context
- Engine Context
- Trend analysis
- Contradiction analysis
- Reasoning Engine
- Confidence calibration
- Prediction integration
- Recommendation intelligence

Reasoning can account for:

- Current score state
- Score movement
- Evidence confidence
- Contradictory evidence
- Trends
- Propagated effects
- Prediction outlook

Recommendations therefore represent the combined result of multiple Cortex faculties rather than a single threshold calculation.

---

## B9 — Explainability

### Completed

Cortex produces structured reasoning artifacts through:

- Evidence Chains
- Evidence Graphs
- Recommendation reasons
- Propagation explanations
- Prediction explanations

Relationship-aware explanations preserve propagation metadata.

Example:

```text
Observe
  ↓
Positive recovery report for QB
  ↓
Understand
  ↓
Recovery signal
  ↓
Reason
  ↓
Receiver receives propagated impact
(1-hop propagation)
  ↓
Evaluate
  ↓
Score changes
  ↓
Predict
  ↓
Future outlook
  ↓
Decide
  ↓
Recommendation
```

This establishes explainability as part of the engine architecture rather than a presentation-layer feature.

---

## B10 — Phase B Integration Gate

A dedicated end-to-end integration test now verifies the complete reasoning path:

```text
RawEvent
   ↓
CortexFacade
   ↓
Entity Resolution
   ↓
Signal Classification
   ↓
Knowledge Graph
   ↓
Relationship Propagation
   ↓
Multidimensional Scoring
   ↓
Prediction / Recommendation
   ↓
Relationship-Aware Explanation
```

Phase B closed with:

```text
274 passed
```

## Status

**COMPLETE**

---

# Phase C — Data Ingestion ▶

## Objective

Build a reliable ingestion layer capable of continuously supplying Cortex with diverse, normalized, deduplicated, and traceable NFL information.

Phase C expands the system from reasoning correctly about events to **reliably acquiring the events Cortex needs to reason about**.

---

## C1 — Source Architecture

Define a common ingestion contract for external sources.

Each source adapter should normalize incoming information into Cortex-compatible events without embedding intelligence or scoring logic in the adapter.

Target architecture:

```text
External Source
      ↓
Source Adapter
      ↓
Normalization
      ↓
Deduplication
      ↓
Canonical Event / RawEvent
      ↓
CortexFacade
```

---

## C2 — Existing Source Consolidation

Audit and normalize existing ingestion paths.

Current/known sources include:

- ESPN RSS
- NBC Sports
- nflverse / nflreadpy
- Existing statistical pipelines

Goals:

- Consistent source metadata
- Consistent timestamps
- Consistent player/team identifiers
- Common error handling
- Shared ingestion interfaces
- Removal of duplicated ingestion logic

---

## C3 — Additional NFL Sources

Evaluate and add high-value sources where appropriate.

Potential categories:

- NFL news
- Injury reports
- Transactions
- Practice participation
- Depth charts
- Rosters
- Player statistics
- Team statistics
- Snap counts
- Usage
- Targets
- Carries
- Red-zone activity

Source selection should prioritize reliability, structured data, licensing considerations, and fantasy relevance.

---

## C4 — Ingestion Reliability

Implement production-oriented source handling.

Planned capabilities:

- Retry behavior
- Exponential backoff
- Rate-limit awareness
- Source failure isolation
- Timeout handling
- Cache strategy
- Source health reporting
- Partial ingestion recovery
- Structured ingestion logging

One failed provider should not prevent other sources from reaching Cortex.

---

## C5 — Deduplication & Canonicalization

Improve event identity across multiple providers.

Goals:

- Cross-source duplicate detection
- Event fingerprints
- Canonical event grouping
- Source provenance
- Corroboration tracking
- Timestamp normalization
- Player identity normalization
- Team identity normalization

Multiple providers reporting the same football event should strengthen evidence rather than produce repeated independent score changes.

---

## C6 — Ingestion Observability

Expose pipeline health and ingestion state.

Planned metrics:

- Events received
- Events accepted
- Events rejected
- Duplicate events
- Canonical events created
- Source failures
- Last successful ingestion
- Processing latency
- Events by provider

These metrics should eventually feed the Streamlit pipeline-status interface and future operational APIs.

---

## Phase C Success Criteria

Phase C is complete when Cortex can reliably consume multiple NFL information sources through a common ingestion architecture while preserving provenance and preventing duplicate events from incorrectly affecting intelligence.

A successful pipeline should resemble:

```text
ESPN ─────────┐
NBC Sports ───┤
NFL Data ─────┤
nflverse ─────┤
Stats ────────┘
       ↓
Unified Ingestion Layer
       ↓
Normalize
       ↓
Deduplicate / Corroborate
       ↓
Canonical Event
       ↓
Gridiron Cortex
```

---

# Phase D — Gridiron Codex

## Objective

Create the long-term football knowledge repository consumed by Cortex.

### Player Knowledge

- Career history
- Draft history
- College information
- Injury history
- Team history
- Historical roles
- Historical fantasy production

### NFL Knowledge

- Draft classes
- Coaching trees
- Offensive systems
- Defensive systems
- Team history
- Organizational changes

### Historical Data

- Historical rankings
- Seasonal trends
- Fantasy finishes
- Position trends
- Rule changes
- Historical relationships

Gridiron Codex should provide durable football context while Cortex remains responsible for reasoning.

---

# Phase E — Intelligence Expansion

## Forecast Engine

Improve future player movement forecasting using:

- Historical trends
- Current momentum
- Injury risk
- Team situation
- Coaching changes
- Opportunity changes
- Usage trends

## Memory Engine

Maintain historical context for:

- Players
- Teams
- Coaches
- Recommendations
- Signals
- Predictions

## Learning Engine

Evaluate previous Cortex decisions.

Measure:

- Recommendation accuracy
- Prediction accuracy
- Confidence calibration
- Signal quality
- Relationship effectiveness
- Recommendation success rate

---

# Phase F — Natural Language Intelligence

Expose Cortex reasoning through football-oriented questions.

Examples:

- Why is Tank Dell a BUY?
- What caused this player's score to change?
- Compare Breece Hall vs. Jahmyr Gibbs.
- Which players are gaining momentum?
- Explain today's biggest risers.
- Which players are most affected by injuries?
- What evidence supports this recommendation?
- How did this signal propagate through the team?
- Compare this season with previous seasons.

Natural-language interfaces should consume structured Cortex intelligence rather than independently inventing recommendations.

---

# Phase G — Platform

## Player Intelligence API

Expose structured Cortex capabilities for applications.

Potential endpoints:

- Player intelligence
- Recommendations
- Scorecards
- Score history
- Evidence
- Relationships
- Propagation paths
- Predictions

## Public API

- REST API
- Authentication
- Rate limiting
- API documentation
- Versioning

## Dashboard

- Advanced analytics
- Trend visualization
- Historical graphs
- Team dashboards
- Knowledge graph visualization
- Propagation inspection
- Pipeline health

## Fantasy Integrations

Potential integrations include:

- League metadata
- Fantasy rosters
- Draft state
- Waivers
- League-specific recommendations

## Mobile

Potential capabilities:

- Notifications
- Daily digest
- Draft companion
- Dynasty mode

---

# Phase H — Commercialization

## Premium Features

- Dynasty intelligence
- Keeper analysis
- League-specific recommendations
- Advanced draft assistant
- Personalized alerts

## Platform Opportunities

- Cortex API
- White-label intelligence
- Fantasy platform integrations
- Sports media integrations

Commercialization should preserve **Gridiron Cortex as the protected intelligence engine** while exposing controlled interfaces to consumers and partners.

---

# Future Cortex Research

Potential future intelligence capabilities include:

- Relationship confidence learning
- Automatic relationship discovery
- Historical relationship effectiveness
- Relationship time decay
- Coaching relationships
- Offensive-line dependencies
- Injury cascades
- Team-level reasoning
- League-wide cascading impacts
- Multiple simultaneous signal propagation
- Learned signal weighting
- Confidence calibration from historical outcomes
- Graph visualization
- Historical counterfactual analysis

These are research directions rather than immediate roadmap commitments.

---

# Guiding Principles

## 1. Cortex Owns Intelligence

Scoring, reasoning, propagation, prediction, confidence, and recommendation logic belong inside Gridiron Cortex.

Applications should remain thin.

## 2. Evidence Before Conclusions

Recommendations should be traceable to observable evidence.

## 3. Preserve Provenance

Cortex should be able to explain where information came from and how it affected a decision.

## 4. Prefer Domain Meaning Over Generic Math

Football relationships should determine how signals propagate.

A backup relationship is not equivalent to a receiver relationship.

## 5. Avoid Graph Noise

More relationships are not automatically better relationships.

Depth, role, confidence, and fantasy relevance should determine graph construction.

## 6. Persist History

Cortex should retain enough historical state to explain how intelligence changed over time.

## 7. Design for Replaceable Infrastructure

JSONL is appropriate for the current stage, but repositories should remain abstract enough to support future database or cloud-backed implementations.

## 8. Protect the Engine Boundary

Gridiron Cortex is the project's primary intellectual property.

External applications and integrations should consume Cortex through stable interfaces rather than duplicating its internal reasoning logic.

---

# Long-Term Goal

Gridiron Cortex should answer:

> **Why does this football event matter, who does it affect, how confident are we, and what should a fantasy manager do about it?**

The desired output is not merely:

```text
Tank Dell +2.3
```

It is structured intelligence:

```text
Tank Dell
Recommendation: BUY

Why:
Recovery evidence improved health and reduced risk.
Multiple sources increased confidence.
Houston relationship context increased expected opportunity.
Recent momentum is positive.

Cortex can trace each conclusion back to the evidence and
reasoning path that produced it.
```

That is the transition from a fantasy scoring application into an explainable football intelligence platform.
