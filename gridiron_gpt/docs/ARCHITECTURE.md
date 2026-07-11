# GridironGPT Architecture

RawEvent
      │
      ▼
 EntityResolver
      │
      ▼
 Entity
      │
      ▼
 SignalProcessor
      │
      ▼
 Signal
      │
      ▼
 RelationshipEngine
      │
      ▼
 Impact
      │
      ▼
 ScoreEngine
      │
      ▼
 PlayerScorecard
      │
      ▼
 RecommendationEngine
      │
      ▼
 Recommendation
      │
      ▼
 ExplanationEngine
      │
      ▼
 EngineResult
      │
      ▼
 Storage

### Architecture
- Established a strongly typed domain model for the Cortex intelligence pipeline.
- Laid the foundation for replacing dictionary-based communication between engine modules.
## Application Structure

Gridiron Cortex is the intelligence engine. GridironGPT is the first application running on top of that engine.

```text
Gridiron Cortex
    ↓
Cortex Engine
    ↓
Typed Domain Models
    ↓
Applications
    ├── Streamlit UI
    ├── CLI
    └── Future API

## Package Structure

```text
gridiron_gpt/
├── gridiron_cortex/
│   ├── engine/
│   └── models/
├── apps/
├── docs/
├── streamlit_app.py
└── test_engine_pipeline.py

## System Philosophy

GridironGPT is built around a single principle:

> **The intelligence engine is the product.**

User interfaces, APIs, dashboards, and future applications are clients of **Gridiron Cortex**, the central football intelligence engine.

---

# High-Level Architecture

```
                     External Data Sources
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
      ESPN RSS          NFL APIs           Future Sources
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                              ▼
                     Data Ingestion Layer
                              │
                              ▼
                   Cleaning & Deduplication
                              │
                              ▼
                    Signal Extraction Layer
                              │
                              ▼
                    Gridiron Cortex Engine
         ┌─────────────────────────────────────────┐
         │                                         │
         │ Signal Engine                           │
         │ Relationship Engine                     │
         │ Recommendation Engine                   │
         │ Confidence Engine                       │
         │ Memory Engine (future)                  │
         │ Forecast Engine (future)                │
         │ Query Engine                            │
         └─────────────────────────────────────────┘
                              │
                              ▼
                       Gridiron Codex
                Historical Knowledge Repository
                              │
                              ▼
                   User Applications & APIs
```

---

# Gridiron Cortex

Gridiron Cortex is the core intelligence engine responsible for reasoning about football information.

Its responsibilities include:

* Signal processing
* Signal persistence
* Story deduplication
* Relationship propagation
* Player scoring
* Recommendation generation
* Confidence calculations
* Historical reasoning
* Natural language intelligence

Everything that represents proprietary football intelligence belongs inside Cortex.

---

## Graph-Based Signal Propagation

Gridiron Cortex uses a dedicated propagation subsystem to determine how a signal affecting one entity should influence related entities.

The propagation subsystem separates graph traversal from impact creation.

### Components

#### `KnowledgeGraphManager`

Location:

```text
gridiron_cortex/knowledge/knowledge_graph_manager.py
```

Responsibilities:

* Queries entity relationships through `KnowledgeService`.
* Returns incoming, outgoing, or bidirectional neighbors.
* Builds cycle-safe relationship graphs.
* Finds relationship paths between entities.
* Identifies entities affected within a configurable graph depth.

The manager provides graph data but does not calculate fantasy impact scores.

#### `PropagationPlanner`

Location:

```text
gridiron_cortex/propagation/propagation_planner.py
```

Responsibilities:

* Traverses outgoing entity relationships.
* Supports configurable multi-hop propagation.
* Prevents cycles during traversal.
* Calculates cumulative relationship strength.
* Calculates cumulative relationship confidence.
* Applies hop-based decay.
* Produces typed `PropagationCandidate` objects.
* Keeps the strongest path when an entity is reachable through multiple routes.
* Preserves the relationship chain used to explain each propagation result.

#### `PropagationCandidate`

Location:

```text
gridiron_cortex/models/propagation.py
```

A propagation candidate represents one entity that may be affected by a signal.

Fields include:

```text
entity_id
entity_name
entity_type
team
hop_count
relationship_strength
relationship_confidence
propagation_weight
reason
```

#### `RelationshipEngine`

Location:

```text
gridiron_cortex/engine/relationship_engine.py
```

Responsibilities:

* Creates the direct impact for the player mentioned in a signal.
* Calls `PropagationPlanner` when graph propagation is configured.
* Converts propagation candidates into `Impact` objects.
* Multiplies the original signal impact by the candidate propagation weight.
* Retains the original relationship repository behavior as a fallback.

### Propagation Flow

```text
Raw Event
    ↓
Entity Resolution
    ↓
Signal Processing
    ↓
Relationship Engine
    ↓
Propagation Planner
    ↓
Knowledge Graph Manager
    ↓
Outgoing Relationship Traversal
    ↓
Propagation Candidates
    ↓
Weighted Impact Objects
    ↓
Score Engine
    ↓
Recommendations and Explanations
```

### Propagation Weight

The propagation weight is calculated using:

```text
cumulative relationship strength
× cumulative relationship confidence
× hop decay
```

Current hop-decay values are:

| Hop count | Decay |
| --------: | ----: |
|         0 |  1.00 |
|         1 |  0.85 |
|         2 |  0.65 |
|         3 |  0.40 |
| 4 or more |  0.20 |

For a one-hop relationship with:

```text
strength = 0.95
confidence = 0.99
```

the propagation weight is:

```text
0.95 × 0.99 × 0.85 = 0.799425
```

If the original signal impact is `-1.0`, the propagated impact becomes:

```text
-1.0 × 0.799425 = -0.799425
```

### Multi-Hop Propagation

For multi-hop paths, relationship strength and confidence are multiplied across every edge in the path.

Example:

```text
Joe Burrow
    ↓ quarterback_receiver
Ja'Marr Chase
    ↓ offensive_unit
Cincinnati Bengals Offense
```

The second-hop candidate uses:

```text
path strength =
first relationship strength
× second relationship strength

path confidence =
first relationship confidence
× second relationship confidence

propagation weight =
path strength
× path confidence
× second-hop decay
```

This causes influence to decrease as it travels farther from the source entity.

### Cycle Protection

The planner tracks all entities visited along each path.

An entity already visited within the current path is not revisited. This prevents loops such as:

```text
Quarterback
    ↓
Receiver
    ↓
Quarterback
```

from producing infinite traversal.

### Multiple Paths

An entity may be reachable through multiple relationship paths.

When this occurs, the planner currently retains the candidate with the highest propagation weight. This prevents duplicate score impacts while preserving the strongest known relationship path.

### Explanation Support

Each propagation candidate includes a reason chain describing the relationships traversed.

Example:

```text
Hop 2; weight=0.386;
quarterback_receiver: Primary quarterback-to-receiver dependency.
->
offensive_unit: Elite receiver materially affects the offense.
```

This information can be surfaced by the explanation engine and Cortex Inspector to show why an entity’s score changed.

### Backward Compatibility

`RelationshipEngine` still supports direct propagation through `RelationshipRepository`.

Behavior is selected in this order:

```text
PropagationPlanner configured
    → use graph-based multi-hop propagation

No planner, repository configured
    → use legacy one-hop repository propagation

Neither configured
    → create direct impacts only
```

This allows graph propagation to be introduced without immediately breaking existing engine construction or tests.

---

# Cortex Subsystems

## Signal Engine

Responsible for:

* News ingestion
* Injury processing
* Roster moves
* Practice reports
* Contract updates
* Signal normalization
* Signal scoring

Output:

Structured football signals.

---

## Relationship Engine

Maintains relationships between football entities.

Examples:

* Quarterback → Receiver
* Running Back → Offensive Line
* Coach → Offensive Scheme
* Defense → Opposing Skill Players

Responsible for propagating impacts across connected entities.

---

## Recommendation Engine

Generates:

* BUY
* HOLD
* WATCH
* SELL

Recommendations are explainable and confidence scored.

---

## Confidence Engine

Determines confidence based on:

* Signal agreement
* Source quality
* Historical accuracy
* Signal freshness
* Relationship strength

---

## Query Engine

Supports natural language questions such as:

* Why is Tank Dell a BUY?
* Compare two players.
* Show today's momentum leaders.
* Explain recommendation changes.

---

# Gridiron Codex

Codex is the long-term football knowledge repository.

Stores:

* Draft classes
* Player history
* Team history
* Coaching history
* Offensive systems
* Historical statistics
* Injury timelines

Codex provides historical context that Cortex reasons over.

---

# Signal Flow

```
News
Injury
Roster Move
Practice Report
        │
        ▼
Signal Extraction
        │
        ▼
Deduplication
        │
        ▼
Signal Scoring
        │
        ▼
Relationship Propagation
        │
        ▼
Player Score Updates
        │
        ▼
Historical Snapshot
        │
        ▼
Recommendation Engine
        │
        ▼
Natural Language Queries
        │
        ▼
Dashboard / CLI / API
```

---

# Design Principles

* Cortex owns intelligence.
* Codex owns long-term knowledge.
* Applications remain thin clients.
* Every recommendation should be explainable.
* Historical reasoning is a first-class capability.
* New features should integrate into Cortex rather than bypass it.

## Persistent Intelligence Architecture

Gridiron Cortex now maintains durable event and player intelligence history.

The engine no longer treats each event as an isolated request. Before processing, Cortex checks whether the event has already been seen. If the event is new, Cortex processes it, updates the player scorecard, and stores an immutable scorecard snapshot.

### Processing Flow

```text
RawEvent
    ↓
Event Fingerprint
    ↓
EventRepository
    ├── Duplicate → Return duplicate result
    └── New Event
            ↓
      EntityResolver
            ↓
      SignalProcessor
            ↓
      RelationshipEngine
            ↓
      ScoreEngine
            ├── Load latest PlayerScorecard
            ├── Apply impact
            ├── Create ScoreUpdate
            ├── Save new PlayerScorecard snapshot
            └── Return scorecard history
            ↓
      RecommendationEngine
            ↓
      ExplanationEngine
            ↓
      EngineResult
