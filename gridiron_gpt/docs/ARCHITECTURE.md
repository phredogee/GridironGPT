# GridironGPT Architecture

## 1. Purpose

GridironGPT is a football intelligence application powered by **Gridiron Cortex**.

GridironGPT owns the user-facing application, ingestion workflows, dashboards,
CLI commands, and advisor interfaces.

Gridiron Cortex owns the reusable football intelligence:

- Event normalization
- Entity resolution
- Signal processing
- Knowledge management
- Graph traversal
- Signal propagation
- Persistent player scoring
- Recommendation generation
- Explanation generation

The long-term architectural principle is:

> **GridironGPT is an application. Gridiron Cortex is the intelligence engine.**

---

## 2. Design Principles

The system follows these principles:

1. **Cortex owns intelligence.**
2. **Applications remain thin clients.**
3. **External sources are normalized before entering Cortex.**
4. **Engine components communicate through typed domain models.**
5. **Every recommendation should be explainable.**
6. **Events and score changes must be auditable.**
7. **Persistent intelligence is a first-class capability.**
8. **New features should extend Cortex rather than bypass it.**
9. **Storage, reasoning, and presentation remain separate concerns.**
10. **Live ingestion must tolerate duplicates, unavailable feeds, and partial data.**

---

## 3. High-Level System Architecture

```text
                         External Data Sources
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
           RSS Feeds          ESPN Data          Future Sources
              │                   │            NFLVerse / APIs / Web
              └───────────────────┴───────────────────┘
                                  │
                                  ▼
                         GridironGPT Ingestion
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
              Fetch and Parse             Match Entities
                    │                           │
                    └─────────────┬─────────────┘
                                  ▼
                         RawEvent Normalization
                                  │
                                  ▼
                            CortexFacade
                                  │
                                  ▼
                         Gridiron Cortex Engine
                                  │
              ┌───────────────────┼────────────────────┐
              │                   │                    │
              ▼                   ▼                    ▼
        Signal Processing   Knowledge Graph      Persistent Storage
              │                   │                    │
              └───────────────────┼────────────────────┘
                                  ▼
                      Propagation and Scoring
                                  │
                                  ▼
                 Recommendations and Explanations
                                  │
                                  ▼
                     Applications and Interfaces
              ┌───────────────────┼────────────────────┐
              │                   │                    │
          Streamlit UI           CLI            Roster Advisor


4. Application and Engine Boundaries
GridironGPT Responsibilities

GridironGPT is responsible for:

Fetching RSS, ESPN, injury, roster, and statistical data
Matching source content to players and teams
Normalizing provider-specific records
Running ingestion commands and scheduled pipelines
Rendering Streamlit dashboards
Providing CLI commands
Hosting the Roster Advisor
Managing user-facing configuration
Gridiron Cortex Responsibilities

Gridiron Cortex is responsible for:

Accepting normalized RawEvent objects
Rejecting duplicate events
Resolving football entities
Classifying signals
Discovering related entities
Planning graph-based propagation
Creating direct and propagated impacts
Updating persistent player scorecards
Generating recommendations
Producing explanations
Exposing intelligence through CortexFacade
Boundary Rule

Gridiron Cortex must not depend directly on:

RSS
ESPN
NFLVerse
Sleeper
Streamlit
CLI frameworks
Provider-specific response formats

All external data must enter Cortex as typed domain objects.

5. Package Structure
gridiron_gpt/
├── apps/
│   └── streamlit/
│       └── components/
├── docs/
├── gridiron_cortex/
│   ├── advisor/
│   ├── engine/
│   ├── facade/
│   ├── intake/
│   ├── knowledge/
│   ├── models/
│   ├── propagation/
│   └── storage/
├── gridiron_gpt/
│   ├── data_ingest/
│   ├── pipelines/
│   ├── scripts/
│   ├── storage/
│   └── intelligence/
├── tests/
├── streamlit_app.py
└── pytest.ini
Cortex Package Structure
gridiron_cortex/
├── advisor/
│   └── roster_advisor.py
├── engine/
│   ├── cortex_engine.py
│   ├── entity_resolver.py
│   ├── signal_processor.py
│   ├── relationship_engine.py
│   ├── score_engine.py
│   ├── recommendation_engine.py
│   └── explanation_engine.py
├── facade/
│   └── cortex_facade.py
├── intake/
│   └── event_pipeline.py
├── knowledge/
│   ├── knowledge_service.py
│   └── knowledge_graph_manager.py
├── models/
│   ├── raw_event.py
│   ├── entity.py
│   ├── signal.py
│   ├── impact.py
│   ├── score_update.py
│   ├── player_scorecard.py
│   ├── recommendation.py
│   ├── engine_result.py
│   ├── entity_relationship.py
│   ├── knowledge_graph.py
│   └── propagation.py
├── propagation/
│   └── propagation_planner.py
└── storage/
    ├── event_repository.py
    ├── player_scorecard_repository.py
    ├── relationship_repository.py
    ├── json_event_repository.py
    ├── json_player_scorecard_repository.py
    └── json_relationship_repository.py
6. Live Intelligence Ingestion
6.1 Purpose

The ingestion layer converts external football information into the canonical
event format expected by Gridiron Cortex.

The current verified implementation supports multiple RSS feeds.

6.2 Live RSS Flow
Configured RSS Feeds
        │
        ▼
rss_news_fetcher.py
        │
        ├── Fetch feed entries
        ├── Read headline, summary, URL, and source
        ├── Match known players
        ├── Estimate initial fantasy impact
        ├── Classify article relevance
        └── Generate story hash
        │
        ▼
cortex_rss_pipeline.py
        │
        ├── Skip unmatched player records
        ├── Collect ingestion metrics
        └── Pass matched items to Cortex intake
        │
        ▼
event_pipeline.py
        │
        └── Convert RSS record into RawEvent
        │
        ▼
CortexFacade.process_event()
6.3 RSS Event Normalization

RSS records are mapped into RawEvent fields as follows:

RSS field	RawEvent field
headline	headline
source	source
player	player
team	team
fantasy_impact	event_type
date	published_at
url	url
6.4 Multi-Feed Configuration

RSS sources are configured through environment variables.

Single feed:

GRIDIRON_RSS_URL
GRIDIRON_RSS_SOURCE

Multiple feeds:

GRIDIRON_RSS_FEEDS

The multi-feed format is:

Source Name|https://example.com/feed.xml,Other Source|https://example.com/rss
6.5 Pipeline Runner

The live RSS-to-Cortex pipeline can be executed with:

python -m gridiron_gpt.scripts.run_cortex_rss

The runner reports:

Feeds checked
Items fetched
Items processed
Duplicate events
Unmatched items skipped
Source errors
6.6 Verified Live Run

The first verified multi-feed execution produced:

Metric	Value
Feeds checked	3
RSS items fetched	51
Matched items processed	16
Unmatched items skipped	35
Errors	0
Persisted Cortex events	20
Player scorecard snapshots	27
Unique scored players	16

A second execution correctly identified all 16 previously processed items as
duplicates and produced no duplicate score changes.

7. Canonical Cortex Processing Pipeline
RawEvent
    │
    ▼
Event Fingerprint
    │
    ▼
Duplicate Check
    │
    ├── Duplicate
    │      └── Return EngineResult:
    │          "Duplicate event ignored."
    │
    └── New Event
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
           ├── Direct impact
           └── PropagationPlanner
                    │
                    ▼
          KnowledgeGraphManager
                    │
                    ▼
          PropagationCandidate
           │
           ▼
         Impact
           │
           ▼
       ScoreEngine
           │
           ├── ScoreUpdate
           ├── PlayerScorecard
           └── Scorecard History
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
8. Typed Domain Model

Gridiron Cortex uses dataclasses rather than unstructured dictionaries for
engine communication.

RawEvent

Represents normalized external information entering Cortex.

Fields:

headline
source
player
team
event_type
published_at
url
Entity

Represents a resolved football entity.

Examples:

Player
Team
Future coach entity
Future offensive unit
Future DST entity
Signal

Represents Cortex interpretation of an event.

Fields include:

headline
entities
sentiment
impact_score
positive_hits
negative_hits
confidence
signal_type
Impact

Represents direct or propagated influence on an entity.

ScoreUpdate

Represents a score transition.

previous_score
score_delta
new_score
score_category
reason
PlayerScorecard

Represents persistent player intelligence.

overall_score
opportunity_score
health_score
hype_score
risk_score
momentum_score
last_updated
Recommendation

Represents actionable advice.

Current recommendation actions include:

BUY
WATCH
HOLD
MONITOR
SELL
EngineResult

Represents the complete result of processing one event.

It includes:

Event
Resolved entities
Signal
Impacts
Score updates
Player scorecards
Scorecard history
Recommendations
Explanation
9. Cortex Facade

CortexFacade is the public entry point for the engine.

Applications should use the facade instead of constructing repositories and
engine components directly.

Facade Responsibilities
Construct persistent repositories
Construct KnowledgeService
Construct KnowledgeGraphManager
Construct PropagationPlanner
Construct engine components
Wire dependencies
Expose stable application-facing methods
Current Public Methods
process_event(event)
get_player_scorecard(player_id)
get_player_history(player_id)
get_relationships(entity_id)
get_entity_graph(entity_id, max_depth, direction)
get_affected_entities(entity_id, max_depth)
find_relationship_paths(source_entity_id, target_entity_id, max_depth)
Application Flow
Streamlit / CLI / Advisor
          │
          ▼
     CortexFacade
          │
          ▼
   Internal Cortex Components

The application does not need to know which repositories, engines, or graph
services are used internally.

10. Knowledge Service

KnowledgeService provides a stable interface over persistent football
knowledge.

It coordinates:

Event repository access
Player scorecard access
Relationship repository access
Responsibilities
Check whether an event already exists
Save processed events
Load latest player scorecards
Load scorecard history
Save relationships
Query incoming relationships
Query outgoing relationships

The service separates knowledge access from graph traversal and scoring logic.

11. Knowledge Graph Architecture
11.1 Relationship Model

Relationships connect football entities.

Example:

CJ Stroud
    │
    └── quarterback_receiver
            │
            ▼
        Tank Dell

A relationship contains:

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
11.2 KnowledgeGraphManager

Location:

gridiron_cortex/knowledge/knowledge_graph_manager.py

Responsibilities:

Query immediate neighbors
Query incoming relationships
Query outgoing relationships
Build cycle-safe graphs
Traverse configurable depths
Find relationship paths
Identify affected entities
Deduplicate graph edges
Return typed graph nodes and edges

The manager answers:

What entities are connected?
How are they connected?
How many hops separate them?
What paths exist between them?

It does not create score impacts.

11.3 Graph Models
GraphNode

Represents an entity in a graph.

GraphEdge

Represents a relationship between two graph nodes.

KnowledgeGraph

Contains:

root_entity_id
nodes
edges
RelationshipPath

Contains the relationship chain between two entities.

It calculates:

hop_count
combined_strength
combined_confidence
12. Propagation Architecture
12.1 Separation of Responsibilities

Graph discovery and fantasy impact creation are separate concerns.

KnowledgeGraphManager
        │
        └── Discovers paths and connected entities
                    │
                    ▼
PropagationPlanner
        │
        └── Calculates weighted propagation candidates
                    │
                    ▼
RelationshipEngine
        │
        └── Converts candidates into Impact objects
                    │
                    ▼
ScoreEngine
        └── Applies impacts to persistent scorecards
12.2 PropagationPlanner

Location:

gridiron_cortex/propagation/propagation_planner.py

Responsibilities:

Find reachable entities
Evaluate relationship paths
Calculate hop count
Calculate cumulative relationship strength
Calculate cumulative relationship confidence
Apply hop decay
Select the strongest path
Produce typed PropagationCandidate objects
Preserve a human-readable relationship reason chain

The planner does not create impacts or modify scores.

12.3 PropagationCandidate

Location:

gridiron_cortex/models/propagation.py

Fields:

entity_id
entity_name
entity_type
team
hop_count
relationship_strength
relationship_confidence
propagation_weight
reason
12.4 Propagation Weight

The current formula is:

propagation weight =
combined relationship strength
× combined relationship confidence
× hop decay

Current hop-decay values:

Hop count	Decay
0	1.00
1	0.85
2	0.65
3	0.40
4 or more	0.20

Example:

relationship strength = 0.85
relationship confidence = 0.95
hop decay = 0.85
0.85 × 0.95 × 0.85 = 0.686375

For an original signal impact of -1.0:

-1.0 × 0.686375 = -0.686375
12.5 Multi-Hop Propagation

For multi-hop paths, relationship strength and confidence are multiplied
across every edge.

Example:

Quarterback
    │
    ▼
Receiver
    │
    ▼
Offensive Unit
combined strength =
edge 1 strength × edge 2 strength

combined confidence =
edge 1 confidence × edge 2 confidence

propagation weight =
combined strength × combined confidence × hop decay
12.6 Cycle Protection

The graph manager tracks visited entities while traversing paths.

This prevents loops such as:

Quarterback
    ↓
Receiver
    ↓
Quarterback

from causing infinite traversal.

12.7 Multiple Paths

An entity may be reachable through more than one relationship path.

The planner currently keeps the path with the highest propagation weight.

This prevents duplicate impacts while preserving the strongest known route.

12.8 Backward Compatibility

RelationshipEngine supports three modes:

PropagationPlanner configured
    → graph-based multi-hop propagation

No planner, repository configured
    → legacy one-hop repository propagation

Neither configured
    → direct impacts only
13. Signal Processing

SignalProcessor converts normalized events into typed signals.

Responsibilities
Evaluate the event headline
Detect positive indicators
Detect negative indicators
Determine sentiment
Assign an impact score
Preserve matched keywords
Attach resolved entities

Current sentiment values include:

Positive
Negative
Mixed
Neutral

Signal vocabulary intentionally avoids treating generic words as universally
positive or negative.

For example, practice alone is neutral.

These phrases can carry meaning:

returns to practice
misses practice
full participant
limited in practice
ruled out
first-team

Future versions should use weighted phrases rather than equal keyword counts.

14. Relationship Engine

RelationshipEngine creates direct and propagated Impact objects.

Responsibilities
Create a direct impact for the primary player
Build the primary entity identifier
Request propagation candidates
Multiply signal impact by propagation weight
Convert candidates into typed Impact objects
Preserve propagation explanations
Fall back to one-hop repository propagation when no planner is configured

The relationship engine answers:

What impact should each affected entity receive?

It does not own graph discovery or persistent score updates.

15. Score Engine

ScoreEngine converts impacts into persistent player intelligence.

Responsibilities
Load the most recent player scorecard
Create a baseline scorecard when none exists
Apply direct and propagated score changes
Create ScoreUpdate records
Save immutable scorecard snapshots
Return player scorecard history
Current Scorecard Dimensions
overall_score
opportunity_score
health_score
hype_score
risk_score
momentum_score

The current implementation applies simplified updates across several dimensions.

Future versions should route signals into specific score categories.

Examples:

Injury signal → health and risk
Depth-chart promotion → opportunity
Camp praise → hype and momentum
Suspension → risk and opportunity
Strong schedule → forecast value
16. Persistent Intelligence

Gridiron Cortex maintains durable event, relationship, and scorecard history.

16.1 Event Repository

Current storage:

data/cortex/events.jsonl

Each saved record includes the normalized event plus a stable fingerprint.

16.2 Player Scorecard Repository

Current storage:

data/cortex/player_scorecards.jsonl

Every score change creates a new immutable snapshot.

This supports:

Latest score lookup
Historical score lookup
Momentum trends
Auditing
Recommendation explanations
Future forecasting
16.3 Relationship Repository

Current storage:

data/cortex/relationships.jsonl

Relationships are stored separately from graph traversal.

This allows the graph manager to remain independent of the storage format.

16.4 Deduplication Layers

The system uses two duplicate-protection layers.

Story-Level Deduplication

The ingestion layer generates story hashes and avoids persisting duplicate
headline and URL combinations.

Cortex-Level Deduplication

RawEvent.fingerprint() creates a SHA-256 identity from:

headline
source
player
team
event_type
published_at
url

Before processing, CortexEngine checks the event repository.

Duplicate events return:

Duplicate event ignored.

No score change is applied.

17. Recommendation and Explanation
17.1 RecommendationEngine

The recommendation engine converts score updates into actionable advice.

Current actions:

BUY
WATCH
HOLD
MONITOR
SELL

Recommendation objects include:

entity_name
team
action
confidence
score_delta
reasons
recommendation_type
timeframe
17.2 ExplanationEngine

The explanation engine summarizes:

The event analyzed
Signal sentiment
Recommendation action
Confidence
Score movement
Propagation reasoning

The long-term goal is complete traceability:

Source story
    ↓
Matched entity
    ↓
Signal classification
    ↓
Relationship path
    ↓
Propagation weight
    ↓
Score update
    ↓
Recommendation
18. Roster Advisor

RosterAdvisor is the first conversational interface over Cortex intelligence.

Current supported question types include:

Highest-scoring player
Top BUY candidate
Player recommendation explanation

Example questions:

Who is my top BUY candidate?
Which player has the highest score?
Why is Tank Dell a WATCH?

The advisor uses deterministic Cortex data rather than inventing football
intelligence.

Future advisor intents include:

START_SIT
WAIVER_FORECAST
ROSTER_VALUE_FORECAST
TRADE_ANALYSIS
PLAYER_EXPLANATION
DST_STREAMING
MATCHUP_ANALYSIS

The long-term three-week waiver question will combine:

Available free agents
League scoring settings
Weekly projections
Schedule strength
Opportunity
Injuries
Momentum
Team environment
DST matchup indicators
19. Streamlit Application

The Streamlit application is a client of CortexFacade.

Current interfaces include:

Cortex Inspector
Command Center dashboard
Player Intelligence
Trends
Momentum
Roster Advisor
Command Center

The Command Center displays:

Engine status
Catalog player count
Ranked players
BUY, WATCH, and risk signals
Engine health
Data preprocessing stages
Latest intelligence cards
Future intelligence tools
Cortex Inspector

The Inspector exposes the processing result of an event:

Event
Resolved entities
Signal
Direct impacts
Propagated impacts
Score updates
Recommendations
Explanation
Player Intelligence

The Player Intelligence interface displays:

Latest scorecard
Historical score movement
Momentum
Recent signals
Recommendation state

Applications should not construct repositories or engine components directly.

20. Testing Architecture

The focused Cortex regression suite currently covers:

Cortex facade
Event deduplication
Player scorecard lookup
Knowledge graph construction
Multi-hop path discovery
Hop decay
Propagation weight calculations
Propagation candidate creation
Relationship engine behavior
Planner integration
Score engine updates
Positive signal classification
Negative signal classification
RSS event normalization

The focused Cortex suite reached:

13 passing tests

before the ingestion bridge test was added.

The ingestion bridge test also passed.

Legacy project tests remain separate because some older modules still depend on
retired or partially migrated packages.

21. Extension Points
21.1 New Data Sources

A new source should:

Fetch provider data.
Parse provider-specific fields.
Match football entities.
Convert records into RawEvent.
Call CortexFacade.process_event().

Potential sources:

ESPN
NFL.com
NFLVerse
Sleeper
Team RSS feeds
Injury feeds
Transaction feeds
Draft data
Weather services
21.2 New Entity Types

Potential entities include:

Player
Team
DST
Coach
Offensive line
Position group
Draft class
Stadium
Opponent
Division
21.3 New Relationship Types

Potential relationship types include:

quarterback_receiver
quarterback_tight_end
running_back_offensive_line
coach_player
coach_team
teammate
position_competition
injury_replacement
team_opponent
player_dst_matchup
rookie_draft_capital
21.4 New Propagation Rules

Future planner improvements may include:

Relationship-type modifiers
Signal-type modifiers
Position-specific modifiers
Team environment modifiers
Recency decay
Source quality
Relationship freshness
Negative and positive asymmetry
Learned relationship strengths
Temporal relationships
21.5 New Storage Backends

Current JSONL repositories can later be replaced by:

SQLite
PostgreSQL
Graph databases
Cloud object storage
Event streams
Managed serverless databases

Engine code should depend on repository interfaces rather than JSONL details.

22. Current Limitations

Current architectural limitations include:

Many RSS stories remain unmatched
Team-only stories are skipped
DST entities are not yet fully supported
Multi-player stories require stronger matching
Relationship data is mostly manual
Hop decay is static
Relationship weights are static
Signal vocabulary is rule-based
Score dimension routing is simplified
Ingestion currently runs manually
Feed retries and backoff are not yet implemented
Feed health history is not yet persisted
Forecasting is not yet implemented
League-specific scoring is not yet integrated
Legacy phred/ dependencies remain in parts of GridironGPT
23. Near-Term Architecture Priorities
Live Ingestion Quality
Improve aliases and nickname matching
Support multiple players per article
Recognize team entities
Recognize DST entities
Preserve article summaries
Store unmatched stories for review
Track ingestion run history
Add retry and backoff behavior
Schedule ingestion automatically
Intelligence Quality
Add relationship-specific propagation rules
Route signals into scorecard dimensions
Add source quality weighting
Add temporal signal decay
Improve explanation traceability
Add injury and depth-chart cascades
Application Quality
Surface live ingestion metrics
Show recent processed events
Add Knowledge Graph Explorer
Expand Roster Advisor intents
Add three-week waiver forecasting
Move major tabs into dedicated Streamlit pages
24. Long-Term Architecture

The target platform architecture is:

                       Football Data Sources
                                │
                                ▼
                     Reliable Ingestion Platform
                                │
                                ▼
                          Gridiron Cortex
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
      Knowledge Graph     Forecast Engine     Memory Engine
             │                  │                  │
             └──────────────────┼──────────────────┘
                                ▼
                       Football Intelligence API
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
       GridironGPT UI      Mobile Client      Third-Party Apps
             │
             ▼
        Roster Advisor

Gridiron Cortex is intended to become a reusable football intelligence engine
capable of supporting:

GridironGPT
Draft assistants
Waiver-wire tools
Trade analyzers
Discord or chat bots
Mobile applications
Public or private APIs
Commercial fantasy football products
