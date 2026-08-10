# Gridiron Cortex Domain Model

## Purpose

The domain model defines the core data objects that flow through the Cortex intelligence engine.

Every engine module consumes one or more of these models and produces another. These models represent the canonical language of the engine and should be preferred over dictionaries or loosely structured data.

---

# Pipeline

RawEvent
    ↓
EntityResolver
    ↓
Entity
    ↓
SignalProcessor
    ↓
Signal
    ↓
RelationshipEngine
    ↓
Impact
    ↓
ScoreEngine
    ↓
PlayerScorecard
    ↓
RecommendationEngine
    ↓
Recommendation
    ↓
ExplanationEngine
    ↓
EngineResult

---

# Models

## RawEvent

Purpose

Represents a normalized event entering Cortex from any external source.

Created By

- RSS ingestion
- APIs
- Manual input
- Future streaming services

Consumed By

- EntityResolver

Key Fields

| Field | Description |
|--------|-------------|
| headline | Event headline or summary |
| source | Originating provider |
| player | Primary player if known |
| team | Team abbreviation |
| event_type | Injury, practice, transaction, etc. |
| published_at | Event timestamp |
| url | Original source URL |

---

## Entity

Purpose

Represents a resolved fantasy football entity.

Created By

- EntityResolver

Consumed By

- SignalProcessor
- RelationshipEngine

Key Fields

| Field | Description |
|--------|-------------|
| entity_type | player, team, coach, etc. |
| name | Canonical name |
| team | Team affiliation |
| confidence | Resolution confidence |
| source | How the entity was identified |

---

## Signal

Purpose

Represents Cortex's interpretation of an event.

Created By

- SignalProcessor

Consumed By

- RelationshipEngine

Key Fields

| Field | Description |
|--------|-------------|
| headline | Original headline |
| sentiment | positive, neutral, negative |
| impact_score | Numerical signal strength |
| confidence | Classification confidence |
| positive_hits | Positive keywords found |
| negative_hits | Negative keywords found |

---

## Impact

Purpose

Represents the fantasy impact generated from a signal.

Created By

- RelationshipEngine

Consumed By

- ScoreEngine

Key Fields

| Field | Description |
|--------|-------------|
| entity_name | Impacted entity |
| impact_score | Numerical effect |
| impact_type | direct or propagated |
| reason | Why the impact exists |

---

## PlayerScorecard

Purpose

Represents Cortex's current intelligence profile for a player.

Created By

- ScoreEngine

Consumed By

- RecommendationEngine

Key Fields

| Field | Description |
|--------|-------------|
| overall_score | Overall player value |
| opportunity_score | Expected opportunity |
| health_score | Injury outlook |
| hype_score | Market perception |
| risk_score | Downside risk |
| momentum_score | Recent trajectory |

---

## ScoreUpdate

Purpose

Represents a single score adjustment applied to a PlayerScorecard.

Created By

- ScoreEngine

Consumed By

- RecommendationEngine

Key Fields

| Field | Description |
|--------|-------------|
| score_delta | Score change |
| previous_score | Previous value |
| new_score | Updated value |
| score_category | Score dimension affected |
| reason | Cause of change |

---

## Recommendation

Purpose

Represents Cortex's actionable fantasy advice.

Created By

- RecommendationEngine

Consumed By

- CLI
- Streamlit Dashboard
- APIs
- Future LLM integrations

Key Fields

| Field | Description |
|--------|-------------|
| action | BUY, HOLD, SELL, WATCH |
| confidence | Recommendation confidence |
| reasons | Supporting evidence |
| timeframe | Current, weekly, season |
| recommendation_type | Redraft, Dynasty, Best Ball |

---

## EngineResult

Purpose

Represents the complete output of a Cortex execution.

Created By

- CortexEngine

Consumed By

- User interfaces
- APIs
- Reports
- Dashboards
- Testing

Contains

- RawEvent
- Entity list
- Signal
- Impact list
- Score updates
- Recommendations
- Human-readable explanation

---

# Design Principles

- Models represent business concepts, not implementation details.
- Every model has a single responsibility.
- Engine modules communicate using typed models rather than dictionaries.
- External data sources are normalized into RawEvent before entering the engine.
- PlayerScorecard is the authoritative state for player intelligence.
- Recommendations are derived from scorecards, not directly from raw events.
- EngineResult is the only object returned by CortexEngine.
