Project Vision

Gridiron is an AI-powered fantasy football intelligence platform designed to transform raw NFL information into actionable fantasy football insights.

Rather than acting as a simple chatbot, the platform continuously ingests football news, roster transactions, injuries, draft information, historical statistics, and other league signals to generate explainable recommendations for fantasy managers.

At the center of the platform is Gridiron Cortex, a proprietary intelligence engine responsible for analyzing information, tracking player momentum, propagating impacts across related players and teams, and producing confidence-based recommendations.

The long-term vision is to build the most trusted fantasy football intelligence engine rather than simply another fantasy football application.

Major Components
Gridiron Cortex

# Gridiron Cortex

## The Intelligence Engine Behind GridironGPT

Gridiron Cortex is an event-driven football intelligence engine that transforms news, injuries, roster transactions, and other football signals into persistent player intelligence.

Unlike traditional fantasy football applications that react only to current events, Cortex maintains historical knowledge, remembers previously processed information, and explains why recommendations change over time.

GridironGPT is one application built on top of the Cortex engine.

---

## Core Capabilities

- Entity Resolution
- Signal Processing
- Relationship Propagation
- Player Scoring
- Recommendation Generation
- Explainable Intelligence
- Persistent Player Memory
- Historical Score Tracking
- Event Deduplication
- Timeline Generation

---

## Design Principles

- Intelligence belongs in the engine.
- Applications remain presentation layers.
- Every recommendation should be explainable.
- Every score should be reproducible.
- Historical knowledge should never be lost.
- Storage implementations should be replaceable.

---

## Current Architecture

```
News / Events
      │
      ▼
Gridiron Cortex
      │
      ├── Entity Resolution
      ├── Signal Processing
      ├── Relationship Engine
      ├── Score Engine
      ├── Recommendation Engine
      └── Explanation Engine
      │
      ▼
Persistent Memory
      │
      ├── Event Repository
      └── Player Scorecard Repository
      │
      ▼
Applications

    • Streamlit

    • CLI

    • Future REST API

    • Future Mobile Clients
```

---

## Current Status

### Completed

- Modular engine architecture
- Typed domain models
- Persistent scorecard history
- Event fingerprinting
- Duplicate event detection
- Explainable recommendations
- Modular Streamlit interface
- Player timeline visualization

### In Progress

- Relationship memory
- Knowledge graph
- Confidence tracking
- Historical analytics

### Planned

- REST API
- SQLite/PostgreSQL persistence
- Draft intelligence
- Predictive scoring
- Long-term knowledge graph

############

Responsibilities include:

Signal ingestion
News classification
Entity extraction
Relationship propagation
Confidence scoring
Recommendation generation
Historical trend analysis
Natural language reasoning
User Applications

Interfaces powered by Cortex.

Examples:

CLI
Streamlit Dashboard
REST API
Future mobile application
Future Components

Gridiron Codex

A historical football knowledge platform containing:

NFL history
Draft classes
Coaching trees
Offensive/defensive schemes
Player career timelines
Franchise history
Historical comparisons

Codex serves as the long-term knowledge repository consumed by Cortex.

class CortexEngine:
    def process_event(self, event: RawEvent) -> EngineResult:
        ...

    def get_player_scorecard(self, player_id: str) -> PlayerScorecard:
        ...

    def explain_recommendation(self, player_id: str) -> RecommendationExplanation:
        ...
