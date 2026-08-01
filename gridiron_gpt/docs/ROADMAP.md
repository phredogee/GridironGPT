# GridironGPT Roadmap

## Vision

Build **Gridiron Cortex**, an AI-powered football intelligence engine capable of transforming raw NFL information into explainable fantasy football recommendations.

The long-term goal is to create a platform where Gridiron Cortex serves as the core intelligence engine while GridironGPT, APIs, dashboards, and future applications become clients of that engine.

---

# Roadmap

## Phase 1 — Foundation ✅

- Cortex Engine
- Relationship Engine
- Score Engine
- Recommendation Engine
- Explanation Engine
- Persistent Player Scorecards
- Multi-source RSS ingestion
- nflverse adapter
- Statistical signal generation

Status

COMPLETE

---

## Phase 2 — Intelligence & Reasoning (Current)

Transform Cortex from a scoring pipeline into a domain-aware football reasoning engine.

### Completed

#### Knowledge Layer

- Knowledge Service
- Persistent entity relationships
- Knowledge Graph Manager
- Graph traversal
- Neighbor discovery
- Relationship path discovery
- Cycle-safe graph construction
- Relationship history

#### NFL Relationship Graph

- nflverse player catalog integration
- nflverse depth-chart integration
- Latest depth-chart snapshot filtering
- Active-roster filtering
- GSIS ID player matching
- Depth-aware offensive relationships
- Position and depth-rank filtering
- Persistent NFL relationship graph

Initial relationship generation was reduced from approximately **2,940 broad roster relationships to 579 depth-aware relationships**.

Current supported relationship semantics include:

- `throws_to`
- `hands_off_to`
- `backs_up`
- `target_competitor`
- `depth_chart_competitor`

#### Propagation Engine

- `PropagationCandidate` model
- Graph-based `PropagationPlanner`
- Multi-hop traversal
- Hop-decay weighting
- Relationship-strength weighting
- Relationship-confidence weighting
- Semantic propagation multipliers
- Direction-reversing competitive relationships
- Strongest-path selection
- Propagation reasoning chains
- RelationshipEngine integration
- Team metadata propagation

Cortex can now reason differently about cooperative and competitive football relationships.

Example:

```text
QB positive signal
    ↓ throws_to
WR positive effect

WR positive signal
    ↓ target_competitor
WR competitor negative effect

---

## Phase 3

### Planned

Player Intelligence API

- Why is Player X a BUY?
- Explain score changes
- Explain propagated impacts

Draft Intelligence

- Rookie ingestion
- Draft capital modeling
- Opportunity competition

Sleeper Integration

- Fantasy metadata
- Rosters
- League information

Historical Trend Analysis

- Multi-week momentum
- Seasonal trajectories
- Historical comparisons

---

## Completed

✔ Knowledge Service

✔ Knowledge Graph Manager

✔ Propagation Planner

✔ Graph traversal

✔ Relationship path discovery

✔ Propagation candidates

---

## Relationship-aware scoring

- Position modifiers
- Team modifiers
- Coach influence
- Injury cascades
- Offensive line effects

---

## Long-Term Vision

Replace generic weighted graph traversal with a domain-aware reasoning engine capable of understanding:

* football relationships
* organizational relationships
* positional dependencies
* offensive and defensive systems
* coaching hierarchy
* roster construction
* draft capital
* opportunity shifts
* fantasy football impact

The objective is for Gridiron Cortex to reason about football events instead of simply propagating numeric scores.

---

## Future Cortex Features

* Relationship confidence learning
* Automatic relationship discovery
* Graph visualization
* Explainable propagation paths
* Time-decay of relationships
* Historical relationship effectiveness
* Confidence calibration
* Signal conflict resolution
* Multiple simultaneous signal propagation
* Team-level reasoning
* League-wide cascading impacts

---

## Success Criteria

A completed propagation engine should be able to explain answers such as:

> "Tank Dell is a BUY because his recovery improves the Texans passing offense, increases projected target share, and raises confidence in Houston's offensive efficiency."

rather than simply reporting:

```text
Tank Dell +2.3
```

This marks the transition from a weighted scoring engine to an explainable football intelligence engine.

---
# Phase 3 — Gridiron Codex

Create the long-term football knowledge repository.

## Player Knowledge

* Career history
* Draft history
* College information
* Injury history
* Team history

## NFL Knowledge

* Draft classes
* Coaching trees
* Offensive systems
* Defensive systems
* Team history

## Historical Data

* Historical rankings
* Seasonal trends
* Fantasy finishes
* Position trends
* Rule changes

---

# Phase 4 — Intelligence Expansion

## Forecast Engine

Predict future player movement based on:

* Historical trends
* Current momentum
* Injury risk
* Team situation
* Coaching changes

## Memory Engine

Maintain historical context for:

* Players
* Teams
* Coaches
* Recommendations
* Signals

## Learning Engine

Evaluate previous recommendations.

Measure:

* Accuracy
* Confidence calibration
* Signal quality
* Recommendation success rate

---

# Phase 5 — Natural Language Intelligence

Support questions such as:

* Why is Tank Dell a BUY?
* Compare Breece Hall vs Jahmyr Gibbs.
* Which players are gaining momentum?
* Explain today's biggest risers.
* Show players most affected by injuries.
* Compare this season to previous years.

---

# Phase 6 — Platform

## Public API

* REST API
* Authentication
* Rate limiting
* API documentation

## Dashboard

* Advanced analytics
* Trend visualizations
* Historical graphs
* Team dashboards

## Mobile

* Notifications
* Daily digest
* Draft companion
* Dynasty mode

---

# Phase 7 — Commercialization

## Premium Features

* Dynasty intelligence
* Keeper analysis
* League-specific recommendations
* Advanced draft assistant

## Enterprise

* Cortex API
* White-label platform
* Fantasy platform integrations
* Sports media integrations

---

# Guiding Principles

Every new feature should strengthen Gridiron Cortex.

The application layer should remain thin while Cortex owns the intelligence, reasoning, scoring, and recommendation logic.

Gridiron Codex will become the long-term football knowledge repository consumed by Cortex.

The engine—not the interface—is the primary intellectual property of the project.
