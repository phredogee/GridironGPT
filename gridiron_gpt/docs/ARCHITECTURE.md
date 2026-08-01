# GridironGPT Architecture

## Gridiron Cortex Intelligence Architecture

GridironGPT is a fantasy football intelligence platform powered by **Gridiron Cortex**, a modular reasoning engine that transforms raw NFL information into structured, persistent, and explainable fantasy football intelligence.

The architecture intentionally separates football-domain concerns from reusable intelligence concerns.

### GridironGPT Owns the Football Domain

GridironGPT is responsible for:

- NFL data ingestion
- nflverse / nflreadpy integration
- player catalogs
- roster interpretation
- depth-chart interpretation
- player aliases and identity normalization
- football-specific relationship construction
- Streamlit presentation
- fantasy football workflows

### Gridiron Cortex Owns Intelligence

Gridiron Cortex is responsible for:

- evidence processing
- canonical event reasoning
- entity resolution
- signal interpretation
- confidence calibration
- contradiction detection
- knowledge graph traversal
- relationship semantics
- impact propagation
- multidimensional scoring
- trend analysis
- prediction
- recommendation
- explanation
- persistent intelligence

The architectural goal is to keep application interfaces thin while preserving Cortex as the project's primary intelligence engine.

---

# System Overview

```text
NFL Data Sources
       │
       ├── News / RSS
       ├── nflverse
       ├── Rosters
       ├── Depth Charts
       ├── Statistics
       └── Future Providers
       │
       ▼
GridironGPT Ingestion Layer
       │
       ▼
Normalized Football Events
       │
       ▼
┌──────────────────────────────────┐
│          GRIDIRON CORTEX         │
│                                  │
│  Observe                         │
│     ↓                            │
│  Understand                      │
│     ↓                            │
│  Reason                          │
│     ↓                            │
│  Evaluate                        │
│     ↓                            │
│  Predict                         │
│     ↓                            │
│  Decide                          │
│     ↓                            │
│  Explain                         │
│     ↓                            │
│  Remember                        │
└──────────────────────────────────┘
       │
       ▼
Structured Fantasy Intelligence
       │
       ├── Recommendations
       ├── Player Scorecards
       ├── Predictions
       ├── Propagated Impacts
       ├── Evidence Chains
       ├── Evidence Graphs
       ├── Timelines
       └── Explanations
       │
       ▼
GridironGPT Interfaces
```

---

# Architectural Principles

## Cortex Owns Intelligence

Scoring, reasoning, propagation, prediction, confidence, recommendation, and explanation logic belong inside Cortex.

Application code should consume Cortex results rather than reproduce Cortex decisions.

---

## GridironGPT Owns Football Context

Football-specific data interpretation belongs in GridironGPT.

Examples include:

- NFL roster interpretation
- depth-chart analysis
- fantasy-position filtering
- football-specific player matching
- player aliases
- nflverse adapters
- relationship construction

Cortex consumes structured entities, events, evidence, and relationships without needing to understand the organization of external NFL datasets.

---

## Evidence Before Conclusions

Recommendations should be traceable to observable evidence.

Cortex should be able to answer:

```text
What happened?
What evidence supports it?
Do the sources agree?
How confident are we?
Who is affected?
How did the effect propagate?
How did player intelligence change?
What is likely to happen next?
Why is the recommendation justified?
```

---

## Explainability Is Part of the Engine

Explainability is not presentation-layer decoration.

Cortex produces structured explanation artifacts that applications can render without reconstructing reasoning independently.

---

## Persistent Intelligence

Cortex maintains historical state instead of evaluating every event in isolation.

Persistent knowledge currently includes:

- processed events
- player scorecards
- scorecard history
- entity relationships
- relationship history

This enables Cortex to reason about changes over time.

---

# Cognitive Architecture

Cortex organizes intelligence processing around a sequence of reasoning faculties:

```text
Observe
   ↓
Understand
   ↓
Reason
   ↓
Evaluate
   ↓
Predict
   ↓
Decide
   ↓
Explain
   ↓
Remember
```

These faculties correspond to concrete engine components rather than being presentation-only concepts.

---

# Observe

## Question

```text
What happened?
```

The observation layer begins with a `RawEvent`.

Typical event information includes:

```text
headline
source
player
team
timestamp
additional source metadata
```

Raw events are normalized before deeper reasoning occurs.

---

# Evidence Aggregation

Multiple reports may describe the same underlying football development.

Cortex supports aggregation into a `CanonicalEvent`.

Conceptually:

```text
ESPN report ───────┐
NFL report ────────┤
NBC report ────────┤
                   ▼
             CanonicalEvent
                   │
                   ▼
            Evidence Analysis
```

Source evidence retains provenance rather than collapsing reports into untraceable text.

---

# Evidence Analysis

Cortex evaluates the quality and consistency of evidence supporting an event.

Evidence reasoning includes:

- source count
- corroboration
- source agreement
- source conflict
- evidence confidence
- supporting evidence
- contradictory evidence

This allows Cortex to distinguish:

```text
single report
```

from:

```text
multiple independent reports describing the same event
```

and from:

```text
multiple reports that disagree about the event
```

---

# Contradiction Detection

The contradiction subsystem evaluates evidence for incompatible indicators.

Examples:

```text
Player returns to full practice.
```

versus:

```text
Player ruled out with injury.
```

Contradiction results contain:

```text
has_conflict
severity
confidence_penalty
conflicting_sources
explanation
```

Only sources contributing contradictory positive or negative evidence are attributed as conflicting.

Neutral sources are not automatically labeled contradictory simply because they belong to the same canonical event.

Contradiction penalties feed downstream reasoning and recommendation confidence.

---

# Understand

## Question

```text
What does the event mean?
```

The understanding layer converts observations into football-relevant signals.

Primary responsibilities include:

- entity resolution
- player enrichment
- signal classification
- sentiment interpretation
- semantic signal categorization
- evidence-aware confidence

---

# Entity Resolution

`EntityResolver` identifies entities referenced by an event.

Current primary entity type:

```text
player
```

Entities may contain:

```text
name
team
entity type
confidence
source
```

Player enrichment can supplement resolved entities using the GridironGPT player catalog.

---

# Signal Processing

`SignalProcessor` converts an event into a structured `Signal`.

Signals contain information such as:

```text
headline
entities
sentiment
impact_score
positive_hits
negative_hits
confidence
signal_type
signal_category
source_count
sources
corroboration_confidence
evidence
```

Signals therefore represent more than generic positive or negative sentiment.

They carry semantic meaning used by downstream scoring and reasoning.

---

# Signal Categories

Current Cortex reasoning supports semantic categories such as:

```text
recovery
injury
opportunity
performance
availability
general news
```

Signal category matters because different football developments should affect different dimensions of player intelligence.

Example:

```text
Recovery
   ↓
Health ↑
Risk ↓
Momentum ↑
```

rather than blindly changing every score dimension equally.

---

# Confidence Calibration

Cortex distinguishes raw classifier confidence from evidence-supported confidence.

Confidence may incorporate:

- signal confidence
- evidence strength
- corroboration
- source count
- agreement
- contradiction penalties

This prevents a strong keyword match from automatically becoming a high-confidence football conclusion when supporting evidence is weak or contradictory.

---

# Reason

## Question

```text
Who else is affected, and why?
```

The Reason faculty contains the relationship and propagation architecture.

Major components:

```text
KnowledgeService
      ↓
KnowledgeGraphManager
      ↓
PropagationPlanner
      ↓
RelationshipSemantics
      ↓
RelationshipEngine
      ↓
Impact
```

---

# Knowledge Service

`KnowledgeService` is the central access layer for persistent Cortex knowledge.

It hides repository implementations from the engine and application layers.

Current responsibilities include:

### Events

```text
has_event()
save_event()
```

### Player Scorecards

```text
get_latest_scorecard()
get_scorecard_history()
save_scorecard()
```

### Relationships

```text
save_relationship()
get_outgoing_relationships()
get_incoming_relationships()
get_relationship_history()
```

This abstraction allows storage implementations to evolve without requiring Cortex reasoning components to depend directly on JSONL or future database technology.

---

# Knowledge Graph

`KnowledgeGraphManager` provides graph-oriented access to persisted relationships.

Capabilities include:

- outgoing relationship lookup
- incoming relationship lookup
- neighbor discovery
- graph traversal
- relationship path discovery
- cycle-safe traversal

The graph represents football dependencies rather than generic social connections.

---

# Entity Relationship Model

Relationships contain information including:

```text
source_entity_id
source_entity_name
source_entity_type

target_entity_id
target_entity_name
target_entity_type

relationship_type
strength
confidence
reason

source_team
target_team

first_seen
last_updated
active
```

Strength and confidence intentionally represent different concepts.

```text
Strength
    → How strongly should this relationship influence propagation?

Confidence
    → How certain is Cortex that this relationship is valid?
```

---

# NFL Relationship Construction

GridironGPT constructs football-specific relationships using player catalog and nflverse depth-chart information.

The relationship builder:

1. Loads the current NFL season.
2. Loads nflverse depth-chart history.
3. Selects each team's latest available snapshot.
4. Filters to fantasy-relevant positions.
5. Matches depth-chart players against the active player catalog.
6. Uses GSIS IDs when available.
7. Falls back to normalized player names.
8. Applies depth-rank limits.
9. Constructs high-value football relationships.

This replaced the earlier broad teammate graph.

Development comparison:

```text
Broad prototype graph:     ~2,940 relationships
Depth-aware graph:            579 relationships
NFL teams represented:         32
```

The smaller graph is intentional.

Cortex should prefer meaningful football relationships over graph density.

---

# Current NFL Relationship Types

The current depth-aware builder produces:

```text
throws_to
hands_off_to
backs_up
target_competitor
depth_chart_competitor
```

Examples:

```text
Jalen Hurts
    ↓ throws_to
A.J. Brown
```

```text
Jalen Hurts
    ↓ hands_off_to
Saquon Barkley
```

```text
Tank Bigsby
    ↓ backs_up
Saquon Barkley
```

```text
A.J. Brown
    ↓ target_competitor
DeVonta Smith
```

---

# Dynamic Relationship Refresh

NFL relationships are not treated as permanent.

`RelationshipRefreshService` compares newly proposed graph state with currently active relationships.

A refresh classifies relationships as:

```text
new
changed
unchanged
stale
```

Only meaningful changes are persisted.

Unchanged relationships are not repeatedly appended to storage.

Stale relationships can be deactivated while historical state remains available.

This provides idempotent graph refresh behavior.

Example refresh:

```text
proposed=579
current=579
new=0
changed=0
unchanged=579
stale=0
written=0
```

This allows roster and depth-chart changes to update the active graph without destroying historical relationship information.

---

# Relationship Semantics

Relationship type determines how a source signal affects its target.

Cortex does not assume every edge moves in the same direction.

---

## `throws_to`

```text
QB → WR / TE
```

Quarterback developments generally affect receiving options in the same direction.

---

## `hands_off_to`

```text
QB → RB
```

Quarterback and offensive context influence rushing opportunity with moderate strength.

---

## `backs_up`

Backup relationships use inverse semantics.

Conceptually:

```text
Starter improves
      ↓
Backup opportunity decreases
```

and:

```text
Starter declines
      ↓
Backup opportunity increases
```

---

## `target_competitor`

```text
Receiver ↔ Receiver
Receiver ↔ Tight End
```

Opportunity movement for one receiving option can create inverse opportunity pressure on another.

---

## `depth_chart_competitor`

Used for players competing for positional workload.

Current primary use is running-back competition.

---

## Additional Semantic Support

The semantic registry also supports relationship types including:

```text
passes_to
teammate
plays_for
coached_by
competes_with
```

Unknown relationship types fall back to neutral semantic behavior for compatibility with existing relationship data.

---

# Propagation Planner

`PropagationPlanner` converts graph paths into propagation candidates.

A propagation candidate includes:

```text
entity
team
hop count
relationship strength
relationship confidence
propagation weight
reasoning path
```

---

# Propagation Weight

Conceptually:

```text
propagation weight
    =
relationship strength
    ×
relationship confidence
    ×
semantic multiplier
    ×
hop decay
```

Semantic multipliers may be negative.

This allows competitive relationships to reverse the direction of a signal.

---

# Hop Decay

Propagation weakens as effects travel farther from the original event.

Current decay behavior:

```text
0 hops → 1.00
1 hop  → 0.85
2 hops → 0.65
3 hops → 0.40
4+     → 0.20
```

This prevents distant graph relationships from receiving the same influence as directly connected players.

---

# Strongest Path Selection

Multiple paths may connect a source entity to the same target.

Cortex evaluates candidate paths and retains the path with the greatest absolute propagation weight.

Absolute weight is important because:

```text
strong negative effect
```

can be as meaningful as:

```text
strong positive effect
```

---

# Multi-Hop Semantic Reasoning

Semantics are evaluated edge by edge.

Example:

```text
Player A
   │
   │ competitive
   ▼
Player B
   │
   │ cooperative
   ▼
Player C
```

If the first relationship reverses signal direction, the second relationship evaluates that reversed impact.

Cortex therefore reasons over the path rather than merely multiplying static graph values.

---

# Impact Model

`RelationshipEngine` converts direct and propagated reasoning into `Impact` objects.

Impacts may be:

```text
direct
propagated
```

Propagated impacts retain:

```text
hop_count
relationship_strength
relationship_confidence
propagation_weight
reason
```

This metadata survives into downstream explanation systems.

---

# Evaluate

## Question

```text
How does this change player intelligence?
```

The evaluation faculty applies impacts to persistent player scorecards.

---

# Multidimensional Player Scorecard

Current dimensions:

```text
overall_score
opportunity_score
health_score
hype_score
risk_score
momentum_score
```

Players begin from a neutral baseline and evolve as Cortex processes evidence.

Scores remain bounded within the configured Cortex range.

---

# Category-Aware Scoring

Score updates depend on the semantic meaning of the signal.

Examples:

```text
Recovery
   ↓
overall ↑
health ↑
risk ↓
momentum ↑
```

```text
Injury
   ↓
overall ↓
health ↓
risk ↑
momentum ↓
```

Opportunity-oriented events can affect opportunity differently from health-oriented events.

This replaced the earlier behavior in which the same impact delta was applied broadly across multiple score dimensions.

---

# Propagated Semantic Scoring

Semantic scoring applies to downstream players as well as directly mentioned players.

Example:

```text
QB recovery
    ↓
throws_to
    ↓
WR propagated recovery impact
    ↓
WR health / risk / momentum context updated
```

The propagated player's scorecard therefore retains the meaning of the original football development rather than receiving only an untyped numeric delta.

---

# Scorecard History

Scorecard snapshots are persisted over time.

History enables:

- trend analysis
- trajectory analysis
- historical comparisons
- score-change explanations
- timeline visualization
- future learning and calibration

---

# Intelligence Layer

After scoring, Cortex builds a broader intelligence context.

Current intelligence components include:

```text
TrendAnalyzer
ContradictionDetector
ReasoningEngine
IntelligenceEngine
```

`IntelligenceContext` can contain:

```text
contradiction
trend
reasoning
confidence
```

This provides downstream recommendation logic with interpreted intelligence rather than only raw scores.

---

# Predict

## Question

```text
What is likely to happen next?
```

`PredictionEngine` generates forward-looking player intelligence.

Prediction information includes:

```text
projected trend
projected score
score delta
confidence
horizon
reasons
```

Predictions are advisory intelligence and remain explainable through evidence artifacts.

---

# Decide

## Question

```text
What action should a fantasy manager consider?
```

`RecommendationEngine` generates fantasy recommendations.

Current recommendation vocabulary includes:

```text
BUY
SELL
WATCH
HOLD
MONITOR
```

Recommendations can account for:

- score movement
- intelligence context
- prediction
- trend
- contradiction
- confidence

Contradictory evidence can reduce recommendation confidence or cause aggressive recommendations to become more cautious.

---

# Explain

## Question

```text
Why?
```

Explainability is generated in several forms.

---

## Plain-Language Explanation

Provides a human-readable summary of the recommendation and major contributing factors.

---

## Evidence Chains

Evidence chains provide an ordered cognitive trace:

```text
Observe
   ↓
Understand
   ↓
Reason
   ↓
Evaluate
   ↓
Predict
   ↓
Decide
```

Propagated Reason steps preserve information such as:

```text
1-hop propagation
propagation weight
relationship reason
```

---

## Evidence Graphs

Evidence graphs represent causal dependencies between reasoning artifacts.

Evidence graphs and football propagation graphs solve different problems:

```text
Evidence Graph
    → Why does Cortex believe this conclusion?

Relationship Graph
    → Which football entities are affected?
```

Both are retained because explainability and football dependency reasoning are distinct architectural concerns.

---

# Remember

## Question

```text
What should Cortex retain?
```

Current persistent knowledge includes:

- processed events
- player scorecards
- player scorecard history
- entity relationships
- relationship history

Persistence supports both operational state and auditability.

---

# Persistence Architecture

Current Cortex storage:

```text
data/cortex/
├── events.jsonl
├── player_scorecards.jsonl
└── relationships.jsonl
```

---

## Events

Used for:

- event history
- event fingerprinting
- duplicate detection
- auditability

---

## Player Scorecards

Used for:

- current player intelligence
- historical score trends
- prediction inputs
- timeline analysis

---

## Relationships

Used for:

- active graph construction
- graph history
- multi-hop propagation
- relationship audits

Relationship persistence remains append-only.

Dynamic refresh prevents unchanged graph snapshots from being written repeatedly.

---

# Repository Abstraction

Cortex reasoning depends on repository contracts rather than specific persistence technologies.

This provides a migration path from:

```text
JSONL
```

to future infrastructure such as:

```text
PostgreSQL
Supabase
managed cloud databases
graph storage
```

without requiring reasoning components to be rewritten.

---

# Additional Application Persistence

GridironGPT also uses Supabase-backed persistence for selected application workflows.

Application persistence and Cortex knowledge persistence remain separate architectural concerns.

External persistence should fail gracefully so network outages do not make the entire user interface unavailable.

---

# Engine Orchestration

`CortexEngine` coordinates the reasoning pipeline.

Conceptually:

```text
RawEvent
    ↓
PlayerEnrichment
    ↓
EvidenceAggregator
    ↓
CanonicalEvent
    ↓
EvidenceAnalyzer
    ↓
EntityResolver
    ↓
SignalProcessor
    ↓
ConfidenceCalibrator
    ↓
RelationshipEngine
    ↓
PropagationPlanner
    ↓
ScoreEngine
    ↓
PredictionEngine
    ↓
IntelligenceEngine
    ↓
RecommendationEngine
    ↓
ExplanationEngine
    ↓
EngineResult
```

The engine's primary responsibility is orchestration.

Domain-specific behavior should remain in specialized components rather than accumulating inside `CortexEngine`.

---

# Engine Result

`EngineResult` is the primary output contract for Cortex processing.

It exposes structured outputs including:

```text
event
entities
signal
canonical_event
evidence_assessment
confidence_result
impacts
score_updates
player_scorecards
player_snapshots
scorecard_history
predictions
intelligence
recommendations
evidence_chains
evidence_graphs
explanation
```

Interfaces can therefore render Cortex intelligence without independently reconstructing reasoning.

---

# Cortex Facade

Applications primarily enter Cortex through:

```text
CortexFacade
```

The facade constructs and connects infrastructure including:

```text
KnowledgeService
KnowledgeGraphManager
PropagationPlanner
CortexEngine
repositories
reasoning services
prediction services
```

Default local knowledge directory:

```text
data/cortex
```

The facade provides the architectural boundary applications should prefer over directly constructing internal Cortex components.

---

# Standalone Cortex Package

Gridiron Cortex has also been extracted toward a standalone repository/library:

```text
gridiron-cortex
```

The standalone direction provides:

- stable Cortex API
- independent testing
- extension interfaces
- package documentation
- CI
- reusable intelligence architecture

GridironGPT remains the NFL/fantasy application and domain layer.

During the extraction/refactor period, the GridironGPT repository continues to contain its in-repository Cortex implementation while boundaries stabilize.

---

# Plugin Direction

The standalone Cortex architecture provides extension points for domain-specific behavior.

The long-term objective is:

```text
Generic Cortex Intelligence
          +
Football Domain Plugin
          =
Gridiron Cortex for GridironGPT
```

Potential extension areas include:

- event classification
- entity resolution
- signal scoring
- relationship behavior
- recommendation policy

This boundary remains an architectural direction rather than a requirement for current Phase C ingestion work.

---

# Cortex Inspector

The Cortex Inspector is the primary engineering interface for observing Cortex behavior.

Current views include:

```text
Summary
Evidence & Confidence
Cognitive Trace
Evidence Graph
Propagation
Intelligence
Explanation
Diagnostics
```

---

## Propagation View

Displays information including:

- direct impacts
- propagated impacts
- downstream entities
- hop count
- propagation weight
- relationship strength
- relationship confidence
- propagation reasoning

---

## Intelligence View

Displays information including:

- predictions
- player snapshots
- score evolution
- historical timeline

---

## Diagnostics

Provides access to internal engine artifacts for development, debugging, and auditability.

---

# Pipeline Status

The Cortex Inspector exposes major pipeline stages:

```text
Evidence
Confidence
Entities
Signal
Propagation
Scores
Prediction
Recommendation
Explanation
```

This provides immediate visibility into which Cortex faculties produced output for an event.

---

# Phase B Integration Gate

Phase B introduced a dedicated end-to-end integration test proving that the complete reasoning pipeline works as a system.

The validated path is:

```text
RawEvent
   ↓
CortexFacade.process_event()
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

The Phase B architecture milestone closed with:

```text
274 automated tests passing
```

This integration gate is important because isolated subsystem tests cannot prove that reasoning metadata survives the complete pipeline.

---

# Testing Strategy

Automated tests cover areas including:

- Cortex facade
- engine pipeline
- structured evidence pipeline
- evidence analysis
- confidence calibration
- contradiction detection
- entity resolution
- signal processing
- semantic signal classification
- knowledge graph traversal
- relationship repository behavior
- relationship refresh
- relationship semantics
- propagation planning
- multi-hop propagation
- score engine
- multidimensional scoring
- prediction
- reasoning
- recommendation
- explanation
- evidence chains
- evidence graphs
- Streamlit component imports
- ingestion pipelines

Current baseline:

```text
274 passed
```

The test suite acts as the primary regression gate during the ongoing Cortex extraction and architectural refactor.

---

# Legacy Relationship Architecture

GridironGPT previously used:

```text
data/relationships.json
```

with relationship types such as:

```text
qb_to_wr1
qb_to_wr2
qb_to_te1
qb_to_rb
```

and direct multiplier-based recursion.

The legacy architecture remains useful as historical context and potential manual override material, but the Cortex knowledge graph is the preferred reasoning architecture.

The current design separates:

```text
relationship type
relationship strength
relationship confidence
semantic behavior
hop decay
graph traversal
```

instead of encoding most behavior into a single static multiplier.

---

# Current Limitations

## Relationship Calibration

Current relationship strengths, confidence values, and semantic multipliers are heuristic.

They have not yet been calibrated against large-scale historical fantasy outcomes.

Future calibration may incorporate:

- snap share
- route participation
- target share
- carries
- red-zone usage
- player efficiency
- historical fantasy scoring
- coaching tendencies

---

## Historical Validation

The reasoning and propagation architecture has not yet been comprehensively replayed against historical NFL seasons.

Future validation should measure:

- propagation accuracy
- recommendation quality
- prediction quality
- confidence calibration
- relationship effectiveness
- signal-category performance

---

## Defensive and Organizational Relationships

The active graph focuses primarily on offensive fantasy relationships.

Potential future expansion includes:

```text
offensive line → quarterback
offensive line → running back
coach → player
coordinator → offense
rookie → incumbent
injury replacement
team → player
defensive secondary → receiver
pass rush → quarterback
```

Graph expansion should remain selective to avoid reintroducing unnecessary relationship noise.

---

## Relationship Data Freshness

Dynamic refresh is implemented, but refresh scheduling and ingestion orchestration are not yet productionized.

Phase C should determine when roster/depth-chart refreshes occur and how source failures are handled.

---

## Source Coverage

Cortex can reason over multi-source evidence, but the ingestion layer does not yet provide the breadth and operational reliability needed to fully exploit that capability.

This is the primary architectural focus of Phase C.

---

# Reliability Principles

External dependencies must not make the entire application unavailable.

Examples include:

- Supabase
- RSS providers
- nflverse
- future NFL APIs
- future LLM providers

External integrations should support:

- failure isolation
- graceful degradation
- retries where appropriate
- rate-limit awareness
- observability
- caching where useful

These concerns become a primary implementation focus during Phase C.

---

# Phase C — Data Ingestion Architecture

Phase C moves the architecture upstream.

Phase B established:

```text
Cortex can reason correctly about an event.
```

Phase C must establish:

```text
Cortex can reliably receive the events it needs.
```

---

# Target Ingestion Boundary

External source adapters should not contain Cortex intelligence logic.

The desired contract is:

```text
External Provider
      ↓
Source Adapter
      ↓
Normalization
      ↓
Identity Resolution
      ↓
Deduplication / Corroboration
      ↓
RawEvent / Canonical Event Input
      ↓
CortexFacade
```

Adapters should answer:

```text
What did the provider report?
```

Cortex should answer:

```text
What does it mean?
```

This boundary is critical.

---

# Phase C Source Architecture

Known or existing source categories include:

```text
ESPN / RSS
NBC Sports
nflverse / nflreadpy
rosters
depth charts
statistics
injuries
transactions
practice participation
usage data
```

Phase C should consolidate these behind common ingestion interfaces.

---

# Ingestion Reliability

The ingestion architecture should eventually support:

```text
retry
backoff
timeouts
rate-limit handling
source health
cache strategy
failure isolation
structured logging
partial recovery
```

A provider failure should affect that provider, not the entire Cortex pipeline.

---

# Cross-Source Deduplication

Multiple providers may report the same underlying event.

The ingestion/evidence architecture should converge:

```text
ESPN ──────┐
NBC ───────┤
NFL ───────┤
           ▼
      Same Event
           ↓
     CanonicalEvent
```

rather than:

```text
Same football event
      ↓
three independent score changes
```

Corroboration should increase evidence confidence without multiplying the football effect.

---

# Ingestion Observability

Future operational metrics should include:

```text
events received
events accepted
events rejected
duplicates
canonical events
source failures
last successful ingestion
processing latency
events by provider
```

These metrics can feed the existing pipeline-status presentation layer and future operational APIs.

---

# Gridiron Codex

Gridiron Codex remains the planned long-term football knowledge repository consumed by Cortex.

Potential knowledge includes:

## Players

- career history
- college history
- draft information
- injury history
- team history

## Teams

- roster construction
- coaching history
- offensive systems
- defensive systems
- organizational trends

## Historical Intelligence

- fantasy rankings
- seasonal performance
- player trajectories
- draft classes
- rule changes
- historical relationships

Codex provides durable football knowledge.

Cortex remains responsible for reasoning over that knowledge.

---

# Long-Term Architecture

```text
                    Gridiron Codex
                          │
                          ▼
External NFL Data → GridironGPT Domain Layer
                          │
                          ▼
                    Ingestion Layer
                          │
                          ▼
                  Gridiron Cortex
                  Intelligence Engine
                          │
               ┌──────────┼──────────┐
               ▼          ▼          ▼
            Web App      API      Other Apps
```

Gridiron Cortex remains the primary intelligence engine.

GridironGPT remains the football application powered by Cortex.

Gridiron Codex becomes the durable football knowledge repository.

---

# Architectural Goal

The goal is not simply to produce numeric fantasy scores.

Cortex should be able to reason:

> A positive recovery development improves a player's health outlook, reduces risk, affects connected teammates according to football-specific relationships, changes persistent player intelligence, influences future projections, and produces an explainable fantasy recommendation whose confidence reflects the available evidence.

Instead of merely returning:

```text
Player +2.3
```

Cortex should answer:

```text
What changed?
Why did it matter?
What evidence supports it?
Do the sources agree?
Who else was affected?
How did the effect propagate?
How strongly?
How did player intelligence change?
What happens next?
How confident are we?
What should the fantasy manager do?
Why?
```

That transition—from static scoring to persistent, evidence-aware, explainable football reasoning—is the central architectural purpose of Gridiron Cortex.
