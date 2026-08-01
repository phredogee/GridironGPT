# GridironGPT Architecture

## Gridiron Cortex Intelligence Architecture

GridironGPT is a fantasy football intelligence platform powered by **Gridiron Cortex**, a modular reasoning engine that transforms raw NFL information into structured, explainable fantasy football intelligence.

GridironGPT owns the football-specific application layer:

- NFL data ingestion
- nflverse integration
- player catalogs
- roster and depth-chart interpretation
- football-specific relationship construction
- Streamlit presentation
- fantasy workflows

Gridiron Cortex owns the reusable intelligence layer:

- evidence processing
- entity resolution
- signal processing
- relationship reasoning
- propagation
- scoring
- prediction
- recommendation
- explanation
- persistent intelligence

The architectural objective is to keep the application thin while allowing Cortex to remain reusable outside of fantasy football.

---

# System Overview

```text
NFL Data Sources
       │
       ▼
GridironGPT Ingestion
       │
       ├── News / RSS
       ├── nflverse
       ├── Rosters
       ├── Depth Charts
       └── Player Statistics
       │
       ▼
Structured Football Events
       │
       ▼
┌──────────────────────────────┐
│       GRIDIRON CORTEX        │
│                              │
│  Observe                     │
│     ↓                        │
│  Understand                  │
│     ↓                        │
│  Reason                      │
│     ↓                        │
│  Evaluate                    │
│     ↓                        │
│  Predict                     │
│     ↓                        │
│  Decide                      │
│     ↓                        │
│  Explain                     │
│     ↓                        │
│  Remember                    │
└──────────────────────────────┘
       │
       ▼
Fantasy Intelligence
       │
       ├── Recommendations
       ├── Player Scorecards
       ├── Predictions
       ├── Propagated Impacts
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

The Cortex engine owns reasoning, scoring, prediction, recommendation, explanation, and persistent intelligence.

GridironGPT should not duplicate Cortex reasoning in the application layer.

---

## GridironGPT Owns Football Context

Football-specific knowledge belongs in GridironGPT.

Examples include:

- NFL roster interpretation
- depth-chart analysis
- fantasy position filtering
- player aliases
- football relationship construction
- league-specific metadata

Cortex receives structured relationships and events without needing to know how NFL datasets are organized.

---

## Explainability Is a First-Class Requirement

Every major intelligence output should be auditable.

Cortex should be able to answer:

```text
What happened?
Why does Cortex believe it?
How confident is Cortex?
Who else is affected?
How did the score change?
What is likely to happen next?
Why is the recommendation justified?
```

---

## Persistent Intelligence

Cortex maintains historical state rather than treating every event independently.

Persistent knowledge currently includes:

- processed events
- player scorecards
- scorecard history
- entity relationships
- relationship history

This allows Cortex to reason about how intelligence changes over time.

---

# Cognitive Architecture

Gridiron Cortex is organized around cognitive faculties.

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

Each faculty answers a different question.

---

# Observe

## Question

```text
What happened?
```

## Responsibilities

- receive raw events
- normalize event input
- aggregate supporting evidence
- enrich player metadata
- reject duplicate events

## Primary Models

```text
RawEvent
CanonicalEvent
```

## Relevant Packages

```text
observe/
evidence/
enrichment/
```

---

# Understand

## Question

```text
What does the event mean?
```

## Responsibilities

- analyze evidence
- evaluate evidence quality
- resolve entities
- classify signals
- determine event sentiment
- calculate direct signal impact
- calibrate confidence

## Processing Flow

```text
RawEvent
    ↓
Player Enrichment
    ↓
Evidence Aggregation
    ↓
CanonicalEvent
    ↓
Evidence Analysis
    ↓
EvidenceAssessment
    ↓
Entity Resolution
    ↓
Signal Processing
    ↓
Confidence Calibration
```

## Confidence Calibration

Cortex combines:

```text
Classifier Confidence
        +
Evidence Confidence
        ↓
Calibrated Confidence
```

The current confidence calibrator weights:

```text
Classifier confidence: 60%
Evidence confidence:   40%
```

The calibrated value becomes the confidence used by downstream reasoning.

## Relevant Models

```text
EvidenceAssessment
ConfidenceResult
Entity
Signal
```

---

# Reason

## Question

```text
What else is affected?
```

## Responsibilities

- relationship lookup
- knowledge-graph traversal
- relationship semantics
- direct impact generation
- semantic multi-hop propagation
- path selection
- competitive relationship reasoning

## Relevant Packages

```text
reason/
propagation/
knowledge/
remember/
```

---

# Knowledge Layer

Persistent Cortex knowledge is accessed through:

```text
KnowledgeService
```

The service hides concrete repository implementations from the engine and application.

```text
CortexEngine / CortexFacade
          │
          ▼
    KnowledgeService
       /     |      \
      /      |       \
 Events   Scorecards  Relationships
```

This separation allows repository implementations to change without modifying engine reasoning.

---

# Knowledge Graph Manager

`KnowledgeGraphManager` converts persisted relationships into traversable graph structures.

Current capabilities include:

- outgoing relationship lookup
- incoming relationship lookup
- neighbor discovery
- graph construction
- path discovery
- cycle-safe traversal
- bounded graph depth

Example:

```text
Jalen Hurts
    │
    ├── throws_to ──> A.J. Brown
    │
    ├── throws_to ──> DeVonta Smith
    │
    └── hands_off_to ──> Saquon Barkley
```

---

# NFL Relationship Intelligence

GridironGPT supplies football-specific relationships to Cortex.

Cortex itself does not interpret NFL depth-chart files.

The application layer converts nflverse data into generic Cortex `EntityRelationship` objects.

## Data Flow

```text
nflverse Player Catalog
        +
nflverse Depth Charts
        ↓
GridironGPT Relationship Builder
        ↓
EntityRelationship
        ↓
Knowledge Service
        ↓
Relationship Repository
        ↓
KnowledgeGraphManager
        ↓
PropagationPlanner
        ↓
Relationship Semantics
        ↓
Impact
```

---

# NFL Player Catalog

GridironGPT builds its player catalog from `nflreadpy`.

The catalog currently contains more than 3,000 NFL player records.

Available metadata includes:

- full player name
- football name
- first and last name
- team
- position
- depth-chart position
- roster status
- jersey number
- experience
- college
- rookie year
- entry year
- draft club
- draft number
- GSIS ID
- ESPN ID
- Sleeper ID
- PFR ID
- Yahoo ID
- Rotowire ID
- headshot URL
- generated aliases

The catalog supports:

- player matching
- entity enrichment
- Cortex Inspector player selection
- NFL relationship generation

---

# Depth-Chart Intelligence

Depth charts are loaded using:

```python
nflreadpy.load_depth_charts()
```

The nflverse table is historical and contains many snapshots.

Relevant fields include:

```text
dt
team
player_name
gsis_id
pos_grp
pos_name
pos_abb
pos_slot
pos_rank
```

GridironGPT selects only the most recent available snapshot for each team before constructing the active relationship graph.

This prevents stale depth-chart positions from becoming active Cortex relationships.

## Depth Ranking

`pos_rank` supplies current positional ordering.

Example:

```text
QB
1  Jalen Hurts
2  Tanner McKee

RB
1  Saquon Barkley
2  Tank Bigsby
3  Will Shipley

WR
1  A.J. Brown
2  DeVonta Smith
3  Jahan Dotson
```

---

# NFL Relationship Builder

Football-specific relationship construction is implemented in:

```text
gridiron_gpt/intelligence/relationship_builder.py
```

The builder combines:

- active roster status
- fantasy-relevant positions
- latest team depth chart
- GSIS identity matching
- normalized-name fallback
- positional ranking
- role-specific relationship rules

## Fantasy Positions

The current graph focuses on:

```text
QB
RB
WR
TE
```

## Depth Limits

The first production relationship model limits graph construction to primary fantasy-relevant roles.

Conceptually:

```text
QB → primary depth options
RB → primary depth options
WR → primary receiving options
TE → primary receiving options
```

This significantly reduces graph noise.

The first broad prototype generated approximately:

```text
2,940 relationships
```

Depth-aware filtering reduced the initial persisted graph to approximately:

```text
579 relationships
```

distributed across all 32 NFL teams.

---

# Relationship Model

Cortex represents graph edges with:

```text
EntityRelationship
```

Each relationship stores:

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
    → How certain is Cortex that the relationship is valid?
```

---

# Relationship Semantics

Relationship types determine how signal direction changes during propagation.

Current semantic relationships include:

## `throws_to`

```text
QB → WR / TE
```

Positive quarterback performance generally benefits primary receiving options.

Negative quarterback performance generally reduces receiving outlook.

---

## `hands_off_to`

```text
QB → RB
```

Quarterback/offensive context influences rushing opportunity with moderate strength.

---

## `backs_up`

```text
Backup → Starter
```

This relationship uses inverse semantics.

Example:

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

Opportunity changes propagate inversely.

Example:

```text
A.J. Brown positive opportunity signal
            ↓
DeVonta Smith competitive impact
            ↓
negative opportunity pressure
```

---

## `depth_chart_competitor`

Used for players competing for positional workload.

Current usage focuses primarily on running backs.

---

## Other Supported Semantics

Cortex also supports semantic rules including:

```text
passes_to
teammate
plays_for
coached_by
competes_with
```

Unknown relationship types fall back to neutral behavior so historical relationship data remains compatible.

---

# Propagation Planner

The `PropagationPlanner` transforms knowledge-graph paths into propagation candidates.

A propagation candidate contains:

```text
entity
team
hop count
relationship strength
relationship confidence
propagation weight
reasoning path
```

## Hop Decay

Current hop decay:

```text
0 hops → 1.00
1 hop  → 0.85
2 hops → 0.65
3 hops → 0.40
4+     → 0.20
```

## Propagation Weight

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

The semantic multiplier may be negative.

This allows competitive relationships to reverse signal direction.

---

# Strongest Path Selection

Multiple graph paths may connect the source entity to the same target.

Cortex calculates each path's semantic propagation effect and selects the path with the largest **absolute** weight.

This is important because:

```text
strong negative impact
```

may be just as meaningful as:

```text
strong positive impact
```

---

# Multi-Hop Semantic Reasoning

Propagation semantics are evaluated edge by edge.

Example:

```text
Player A
   │
   │ competitive relationship
   ▼
Player B
   │
   │ cooperative relationship
   ▼
Player C
```

If the first relationship reverses the signal direction, the second relationship evaluates the newly reversed signal.

Cortex therefore reasons over the propagation path rather than simply multiplying static edge values.

---

# Impact Model

The relationship engine converts propagation candidates into `Impact` objects.

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

This allows downstream systems to inspect how Cortex generated an impact rather than receiving only the final score.

---

# Evaluate

## Question

```text
How significant is the event?
```

## Responsibilities

- transform impacts into score changes
- maintain persistent player scorecards
- update intelligence dimensions
- preserve score history

## Player Scorecard

Current score dimensions:

```text
overall_score
opportunity_score
health_score
hype_score
risk_score
momentum_score
```

Player scorecards are persistent.

Each event can therefore alter Cortex's ongoing view of a player rather than producing an isolated result.

---

# Player Scorecard History

Historical scorecard snapshots are stored and returned through `EngineResult`.

This enables:

- score trends
- trajectory analysis
- historical comparisons
- score-change explanations
- Streamlit timeline visualization

The Cortex Inspector currently displays score evolution over time.

---

# Predict

## Question

```text
What is likely to happen next?
```

## Responsibilities

- project player score direction
- determine trend
- estimate future score movement
- attach forecast confidence
- generate prediction reasons

## Prediction Output

Current prediction data includes:

```text
projected trend
projected score
score delta
confidence
horizon
reasons
```

---

# Decide

## Question

```text
What action should be taken?
```

## Responsibilities

Generate fantasy recommendations.

Current recommendation vocabulary includes:

```text
BUY
SELL
WATCH
HOLD
MONITOR
```

Recommendations contain:

- entity
- team
- action
- confidence
- score delta
- reasons

---

# Explain

## Question

```text
Why?
```

Cortex generates multiple forms of explanation.

## Plain-Language Explanation

Human-readable explanation of the recommendation.

## Evidence Chains

Ordered evidence contributing to a decision.

## Evidence Graphs

Causal relationships showing how evidence contributed to an intelligence result.

This is intentionally different from propagation reasoning.

```text
Evidence Graph
    → Why does Cortex believe the event?

Propagation
    → What else is affected because of the event?
```

---

# Remember

## Question

```text
What should Cortex retain?
```

Persistent knowledge currently includes:

- events
- player scorecards
- player scorecard history
- relationships
- relationship history

---

# Persistence Architecture

Current local Cortex storage:

```text
data/cortex/
├── events.jsonl
├── player_scorecards.jsonl
└── relationships.jsonl
```

## Events

Used for:

- event history
- duplicate detection
- auditability

## Player Scorecards

Used for:

- current player intelligence
- historical score trends
- prediction inputs

## Relationships

Used for:

- graph construction
- historical relationship state
- multi-hop propagation

Relationship persistence is append-only.

This improves auditability but requires a controlled refresh process so unchanged relationships are not written repeatedly.

---

# Additional Application Persistence

GridironGPT also uses Supabase-backed repositories for selected application intelligence, including historical player score snapshots.

These systems are separate from Cortex's local JSONL knowledge repositories and serve application/dashboard workflows.

Network-backed persistence must fail gracefully so temporary database outages do not take down the user interface.

---

# Engine Orchestration

The Cortex engine coordinates each faculty.

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
EvidenceAssessment
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

The engine itself should contain minimal domain business logic.

Its primary responsibility is orchestration.

---

# Engine Result

`EngineResult` is the primary output contract for Cortex processing.

It currently exposes:

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

This object allows interfaces such as Streamlit to display Cortex intelligence without independently reproducing engine logic.

---

# Cortex Facade

Applications interact with Cortex primarily through:

```text
CortexFacade
```

The facade constructs and connects:

```text
KnowledgeService
KnowledgeGraphManager
PropagationPlanner
CortexEngine
repositories
reasoning services
prediction services
```

The current default data directory is:

```text
data/cortex
```

---

# Standalone Cortex Package

Gridiron Cortex has also been extracted into a standalone repository/library:

```text
gridiron-cortex
```

The standalone package provides:

- stable public Cortex API
- independent test suite
- plugin interface
- default plugin
- CI
- package documentation
- changelog

The standalone project currently represents the reusable Cortex foundation.

GridironGPT remains the NFL/fantasy-football application and domain layer.

During the extraction/refactor period, the GridironGPT repository still contains its in-repository Cortex package while integration boundaries continue to stabilize.

---

# Plugin Architecture

The standalone Cortex project introduces:

```text
CortexPlugin
```

with a default implementation:

```text
DefaultPlugin
```

The plugin interface provides extension points for domain-specific behaviors such as:

- event classification
- entity resolution
- signal scoring
- relationships
- recommendations

The long-term goal is for GridironGPT's football intelligence to be supplied through domain plugins while the core engine remains generic.

---

# Cortex Inspector

The Cortex Inspector is the primary engineering interface for observing Cortex reasoning.

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

## Summary

Displays:

- signal output
- recommendation

## Evidence & Confidence

Displays:

- classifier confidence
- evidence trust
- calibrated confidence
- consensus
- agreement
- conflict
- source count
- supporting evidence

## Cognitive Trace

Displays the reasoning path through Cortex faculties.

## Evidence Graph

Displays causal evidence relationships.

## Propagation

Displays:

- direct impact
- downstream entity impacts
- hop count
- propagation weight
- relationship strength
- relationship confidence
- propagation reasoning path

## Intelligence

Displays:

- predictions
- player snapshot
- historical player timeline
- score evolution

## Diagnostics

Displays internal engine objects for debugging and auditability.

---

# Pipeline Status

The Cortex Inspector exposes major pipeline-stage status.

Current stages include:

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

This provides a quick indication of which reasoning faculties produced output for an event.

---

# Current NFL Knowledge Graph

The first depth-aware NFL graph has been successfully generated and persisted.

Current development snapshot:

```text
Player catalog:            3,133 players
Broad prototype graph:     ~2,940 relationships
Depth-aware graph:         579 relationships
NFL teams represented:     32
Automated tests:           254 passing
```

The graph has been verified end-to-end through the Cortex Inspector using real NFL roster/depth-chart data.

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

That architecture remains useful as historical context and potential manual override data, but the new Cortex graph is the preferred reasoning architecture.

The newer design separates:

```text
relationship type
relationship strength
relationship confidence
semantic behavior
hop decay
graph traversal
```

rather than encoding most behavior into a single static multiplier.

---

# Current Limitations

## Relationship Refresh

The NFL relationship graph is currently refreshed manually.

Repeated full refreshes write new records because relationship storage is append-only.

Future refresh logic should:

- compare current and proposed graph state
- write only changed relationships
- deactivate stale relationships
- preserve history
- detect roster changes
- detect depth-chart movement

---

## Team Coverage

Relationship counts currently vary significantly by NFL team.

This can occur because:

- active roster and depth-chart datasets do not intersect uniformly
- some depth-chart snapshots contain fewer fantasy-relevant players
- roster statuses change rapidly
- source data freshness varies

Coverage analysis is required before production use.

---

## Relationship Weights

Current relationship strengths and confidence values are heuristic.

They have not yet been calibrated against historical fantasy outcomes.

Future calibration inputs may include:

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

The propagation engine has not yet been fully replayed against historical NFL seasons.

Future validation should measure:

- propagated score accuracy
- recommendation quality
- confidence calibration
- relationship effectiveness
- signal-category performance

---

## Defensive and Organizational Relationships

The current production graph focuses primarily on offensive fantasy relationships.

Future graph expansion should include:

```text
offensive line → quarterback
offensive line → running back
coach → player
coordinator → offense
rookie → incumbent player
injury replacement
team → player
defensive secondary → receiver
pass rush → quarterback
```

---

## Evidence Sources

Evidence aggregation and confidence calibration are operational, but full multi-source corroboration is still being expanded.

Future sources should allow Cortex to distinguish between:

```text
single-source report
multiple-source agreement
conflicting reports
developing story
established consensus
```

---

# Reliability Principles

External systems must not make the entire application unavailable.

Examples include:

- Supabase
- RSS providers
- nflverse
- future APIs
- LLM providers

Interfaces should degrade gracefully when external systems are temporarily unavailable.

---

# Testing Strategy

The project currently maintains more than 250 automated tests.

Tests cover areas including:

- Cortex pipeline
- evidence analysis
- confidence calibration
- entity resolution
- relationship semantics
- propagation planner
- knowledge graph traversal
- score engine
- prediction
- recommendation
- explanation
- player scorecards
- Streamlit component imports
- data ingestion

A Streamlit import smoke test ensures syntax/import errors in critical UI components are detected during the test suite.

---

# Next Architecture Milestone

## Dynamic Relationship Graph Maintenance

The next major relationship milestone is to make graph state dynamic.

GridironGPT should periodically compare current nflverse roster/depth-chart information against Cortex's active relationship graph.

The refresh system should identify:

```text
new relationship
changed relationship
unchanged relationship
stale relationship
```

and only persist meaningful state changes.

Example:

```text
Week 1

RB1: Player A
RB2: Player B

        ↓ injury / depth-chart change

Week 2

RB1: Player B
RB2: Player C
```

Cortex should:

```text
deactivate stale Player B → Player A backup relationship
create Player C → Player B backup relationship
update workload competition relationships
preserve historical relationship state
```

---

# Future Reasoning Architecture

## Signal-Category-Aware Propagation

Relationship effects should eventually depend on the event category.

Example:

```text
QB injury
```

should propagate differently from:

```text
QB strong practice report
```

even across the same `throws_to` relationship.

Potential signal categories include:

- injury
- recovery
- trade
- contract
- suspension
- camp performance
- coaching change
- scheme change
- depth-chart movement
- rookie development
- fantasy hype
- team performance

---

# Gridiron Codex

Gridiron Codex is the planned long-term football knowledge repository consumed by Cortex.

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

---

# Long-Term Architecture

The desired architecture is:

```text
                    Gridiron Codex
                          │
                          ▼
NFL Data ──────> GridironGPT Domain Layer
                          │
                          ▼
                  Gridiron Cortex
                  Intelligence Engine
                          │
               ┌──────────┼──────────┐
               ▼          ▼          ▼
            Web App      API      Other Apps
```

Gridiron Cortex should remain the core intellectual property and reusable reasoning engine.

GridironGPT should remain the football intelligence application powered by Cortex.

---

# Architectural Goal

The ultimate goal is not simply to produce numeric fantasy scores.

Cortex should be able to explain reasoning such as:

> A positive development for a starting wide receiver increases his direct opportunity score, creates competitive pressure on other receiving options, alters downstream player projections, and changes the confidence of the resulting fantasy recommendation.

Instead of merely returning:

```text
Player +2.3
```

the system should be able to answer:

```text
What changed?
Why did it matter?
Who else was affected?
How strongly?
How confident are we?
What should the fantasy manager do?
Why?
```

That transition—from static scoring to persistent, explainable football reasoning—is the central architectural purpose of Gridiron Cortex.
