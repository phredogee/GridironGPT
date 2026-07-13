# GridironGPT Roadmap

## Vision

Build **Gridiron Cortex**, an AI-powered football intelligence engine capable of transforming raw NFL information into explainable fantasy football recommendations.

The long-term goal is to create a platform where Gridiron Cortex serves as the core intelligence engine while GridironGPT, APIs, dashboards, and future applications become clients of that engine.

---

# Phase 1 — Foundation ✅ Completed

## Core Infrastructure

* Project architecture established
* CLI application
* Streamlit interface
* Ollama integration
* Local LLM support
* Configuration management
* ESPN news ingestion
* RSS ingestion pipeline
* Vector search
* Semantic search
* Player profile generation

## Documentation

* PROJECT_OVERVIEW
* ARCHITECTURE
* CHANGELOG
* COMMANDS
* KNOWN_ISSUES
* ROADMAP

---

# Phase 2 — Gridiron Cortex 🚧 Current Phase

## Cortex Facade

* [x] Create Cortex package
* [x] Establish stable Cortex interface
* [ ] Move all new development behind Cortex
* [ ] Reduce direct dependencies on intelligence modules

## Signal Engine

* [x] Signal persistence
* [x] Signal hashing
* [x] Story deduplication
* [x] Signal propagation
* [ ] Signal weighting improvements
* [ ] Confidence calculations
* [ ] Signal lifecycle tracking

## Recommendation Engine

* [x] Player scoring
* [x] BUY / HOLD / SELL recommendations
* [x] Momentum calculations
* [ ] Explainable recommendation output
* [ ] Recommendation confidence scoring

## Relationship Engine

* [x] Player relationship graph
* [x] Signal propagation
* [ ] Team-level propagation
* [ ] Coaching impact propagation
* [ ] Offensive scheme impacts

## Historical Intelligence

* [x] Score snapshots
* [x] Trend reports
* [x] Momentum tracking
* [ ] Long-term score history
* [ ] Recommendation history
* [ ] Historical comparisons

---

# Phase 4 – Intelligent Graph Propagation

## Status

**In Progress**

The graph-based propagation framework has been completed and validated. Signals can now traverse the knowledge graph using configurable multi-hop propagation, cumulative relationship weighting, and cycle-safe traversal.

---

## Completed

✔ Knowledge Service

✔ Knowledge Graph Manager

✔ Propagation Planner

✔ Graph traversal

✔ Relationship path discovery

✔ Propagation candidates

### Knowledge Graph

* Persistent entity relationship storage
* Graph traversal
* Neighbor discovery
* Relationship path discovery
* Cycle-safe graph construction

### Propagation Engine

* PropagationCandidate model
* Graph-based PropagationPlanner
* Hop-decay weighting
* Multi-hop traversal
* Strongest-path selection
* Relationship reasoning chain generation
* RelationshipEngine integration

---

# Next Milestone

## Relationship-aware scoring

- Position modifiers
- Team modifiers
- Coach influence
- Injury cascades
- Offensive line effects

---

## Planned Relationship Types

* quarterback_receiver
* quarterback_running_back
* running_back_offensive_line
* receiver_offensive_line
* offensive_line_team
* defense_secondary
* defense_pass_rush
* coach_team
* coordinator_offense
* coordinator_defense
* rookie_team
* teammate
* target_competition
* depth_chart
* injury_replacement

---

## Signal Categories

Signals will propagate differently based on their category.

Examples:

* Injury
* Recovery
* Contract
* Trade
* Suspension
* Camp Performance
* Coaching Change
* Scheme Change
* Depth Chart Movement
* Rookie Development
* Fantasy Hype
* Team Performance

---

## Future Propagation Rules

Propagation rules will become directional.

Example:

```text
QB
 ↓
WR

Positive Signal
100%

Negative Signal
85%
```

while

```text
WR
 ↓
QB

Positive Signal
40%

Negative Signal
20%
```

The same relationship may therefore produce different outcomes depending on:

* signal category
* sentiment
* propagation direction

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
