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
