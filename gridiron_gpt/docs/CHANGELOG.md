# Changelog

### Added

- Training-camp football concepts.
- Depth-chart concepts.
- Whole-phrase matching to prevent substring false positives.
- Role ownership rules to prevent concept overlap and double-counting.

### Verified

- 169 automated tests passing.

---

## Unreleased

### Added

- EvidenceChain model
- EvidenceGraph model
- Structured reasoning traces
- Causal evidence graphs
- Explain v2 and Explain v2.5
- Semantic multi-hop propagation
- Relationship semantics
- Predict faculty integration

### Changed

- Refactored Cortex into cognitive faculty packages.
- PropagationPlanner now applies relationship semantics.
- ExplanationEngine now generates:
  - Plain explanations
  - Evidence chains
  - Evidence graphs

### Verified

- 152 automated tests passing.


### Changed

- Introduced the eight Cortex cognitive faculty packages:
  Observe, Understand, Reason, Evaluate, Predict, Decide, Explain, and Remember.
- Moved entity resolution and signal processing into Understand.
- Moved relationship processing into Reason.
- Moved score processing into Evaluate.
- Moved recommendation generation into Decide.
- Moved explanation generation into Explain.
- Added compatibility imports under `gridiron_cortex.engine`.
- Preserved existing behavior with all targeted tests passing.

### Changed

- Moved the RSS event pipeline into the Cortex Observe faculty.
- Established `gridiron_cortex.observe` as the permanent home for data acquisition and normalization components.
- Retained `gridiron_cortex.intake` as a temporary backward-compatibility package.
- Preserved all existing behavior with 114 tests passing.

### Added

### Added

- Added the Cortex Predict faculty.
- Added the `Prediction` domain model.
- Added a deterministic rule-based `PredictionEngine`.
- Integrated Predict into `CortexEngine` after Evaluate and before Decide.
- Added predictions to `EngineResult`.
- Added isolated prediction and pipeline test coverage.

### Changed

- Wired `PredictionEngine` into the Cortex facade.
- Updated the engine pipeline to produce short-term player forecasts.
- Preserved all existing behavior with 120 tests passing.

---
## 2026-07-14 — Intelligence Engine Stabilization & nflverse Integration

## Version 0.7.0 — Statistical Intelligence Engine

### Testing

111 automated tests passing

### Added

- Added multi-source RSS ingestion support.
- Integrated ESPN NFL RSS.
- Integrated NBC ProFootballTalk RSS.
- Integrated RotoWire NFL RSS.
- Added nflreadpy adapter for structured NFL data.
- Added nflverse normalization pipeline.
- Added weekly statistical signal generation.
- Added opportunity and production signal classification.
- Added confidence scoring for generated statistical signals.
- Added week-gap detection to avoid comparing non-consecutive appearances.
- Added normalization tests.
- Added nflreadpy adapter tests.
- Added signal factory tests.
- nflreadpy / nflverse integration
- Weekly statistical signal generation
- Rolling baseline analysis
- Signal aggregation
- Trend classification (Emerging, Confirmed, Sustained, Volatile)
- Aggregated signal → RawEvent adapter
- Multi-source RSS ingestion (ESPN, NBC ProFootballTalk, RotoWire)
- demo_cortex.py for end-to-end statistical pipeline demonstrations

### Improved

- Player matcher now favors precision over recall.
- Removed surname-only aliases that produced false positives.
- Increased confidence thresholds for ambiguous matches.
- RSS matching now avoids incorrect matches such as:
- Hall → Breece Hall
- Likely → Isaiah Likely
- Jackson → every player named Jackson
- Position-aware thresholds
- Player matching accuracy
- Regular-season filtering
- Signal confidence calculations

### Fixed

- Restored legacy compatibility imports.
- Fixed pipeline compatibility wrappers.
- Fixed onboarding virtual environment detection.
- Eliminated obsolete phredenv assumptions.
- Suppressed third-party SWIG deprecation warnings.
- Modernized pytest configuration.

### Verification

- 99 automated tests passing.
- ESPN RSS verified.
- NBC RSS verified.
- RotoWire RSS verified.
- nflverse adapter verified.
---
## 2026-07-13

### Major Milestone

Gridiron Cortex now processes live RSS news through the complete intelligence pipeline.

### Added

- RSS-to-Cortex event bridge in `gridiron_cortex/intake/event_pipeline.py`
- Live Cortex RSS pipeline in `gridiron_gpt/pipelines/cortex_rss_pipeline.py`
- Command-line RSS pipeline runner
- Normalization of RSS records into typed `RawEvent` objects
- Live event processing through `CortexFacade`
- Persistent scorecard updates from live news
- Focused ingestion pipeline tests

### Changed

- RSS ingestion now sends matched player stories directly into Gridiron Cortex
- Dashboard terminology now distinguishes catalog players from scored players
- Signal processing vocabulary was refined so neutral words such as `practice` are not treated as automatically positive
- Relationship propagation now uses the `PropagationPlanner`

### Verified

- Three RSS feeds successfully processed
- 51 RSS items fetched
- 16 matched items processed by Cortex
- 35 unmatched items safely skipped
- Second pipeline run identified all 16 previously processed items as duplicates
- 20 events persisted in `data/cortex/events.jsonl`
- 27 scorecard snapshots persisted
- 16 unique players received scorecard updates
- Cortex regression suite passing
- Streamlit dashboard operational after live ingestion

### Current Limitations

- Player matching recognized 16 of 51 fetched stories
- Team-only and DST stories are not yet normalized into Cortex events
- Multi-player stories may require stronger entity matching
- RSS ingestion currently requires manual or externally scheduled execution

---
## 2026-07-12

### Added

- Propagation Planner subsystem
- PropagationCandidate model
- Knowledge graph path planning
- Graph-driven relationship propagation
- Dedicated Cortex regression tests

### Changed

- RelationshipEngine now consumes
  PropagationPlanner.

- CortexFacade now owns planner
  construction and dependency wiring.

- SignalProcessor keyword handling
  refined.

### Verified

- 13 dedicated Cortex tests passing
- Knowledge graph traversal
- Multi-hop propagation
- Planner integration
- Streamlit operational

---
## 2026-07-11

### Added

* Added `PropagationCandidate` model in:

  ```text
  gridiron_cortex/models/propagation.py
  ```

* Added `PropagationPlanner` in:

  ```text
  gridiron_cortex/propagation/propagation_planner.py
  ```

* Added graph-based multi-hop signal propagation using `KnowledgeGraphManager`.

* Added configurable hop decay:

  ```text
  hop 0 = 1.00
  hop 1 = 0.85
  hop 2 = 0.65
  hop 3 = 0.40
  hop 4+ = 0.20
  ```

* Added cumulative relationship strength and confidence calculations across multi-hop paths.

* Added cycle-safe graph traversal.

* Added strongest-path selection when an entity is reachable through multiple propagation routes.

* Added relationship-chain reasoning to each propagation candidate.

### Changed

* Updated `RelationshipEngine` to support `PropagationPlanner`.

* Updated propagated impact calculation to use:

  ```text
  signal impact
  × propagation weight
  ```

* Preserved `RelationshipRepository` propagation as a fallback for backward compatibility.

* Added team information to `PropagationCandidate` so propagated candidates can be converted into complete `Impact` objects.

### Fixed

* Fixed incomplete `PropagationPlanner.plan()` implementation that caused:

  ```text
  IndentationError: expected an indented block
  ```

* Corrected propagation import paths:

  ```text
  gridiron_cortex.models.propagation
  gridiron_cortex.propagation.propagation_planner
  ```

* Corrected the expected model name from `PropagationRule` to `PropagationCandidate`.

### Verified

* Verified `PropagationCandidate` imports successfully.

* Verified `PropagationPlanner` imports successfully.

* Verified hop-decay calculations.

* Verified propagation-weight calculations.

* Verified one-hop propagation.

* Verified two-hop propagation.

* Verified cycle protection.

* Verified strongest-path candidate selection logic.

* Verified the propagation planner with an isolated fake knowledge graph.

* Confirmed the test result:

  ```text
  Real propagation planner test passed.
  ```

### Current Limitations

* Propagation behavior does not yet vary by signal category.

* Relationship types currently use generic strength and confidence values.

* Positive and negative signals currently use the same relationship multipliers.

* Propagation chains are not yet displayed in Cortex Inspector.

* Full engine-level integration with persistent knowledge data still requires testing.

---
## Version 0.2.0
### 2026-07-10

### Major Milestone
**Persistent Intelligence Architecture**

Gridiron Cortex transitioned from a stateless event processor into a persistent intelligence engine capable of maintaining historical player knowledge.

---

### Added

#### Persistent Player Intelligence

- Introduced `PlayerScorecardRepository` abstraction.
- Implemented `JsonPlayerScorecardRepository`.
- Added immutable player scorecard snapshots.
- ScoreEngine now loads the latest player scorecard before applying new impacts.
- ScoreEngine automatically saves updated scorecards after processing.
- Added historical score retrieval for each player.
- EngineResult now includes:
  - `player_scorecards`
  - `scorecard_history`

---

#### Event Persistence

- Introduced `EventRepository` abstraction.
- Implemented `JsonEventRepository`.
- Added normalized event storage.
- Added SHA-256 event fingerprint generation.
- Added duplicate event detection.
- Duplicate events are rejected before entity resolution begins.

---

#### Cortex Engine

- CortexEngine now supports repository injection.
- Added pre-processing duplicate detection.
- Engine now returns early for duplicate events.
- Player scorecards are now generated by the engine instead of the UI.
- Streamlit now renders engine-owned intelligence objects.

---

#### Streamlit

Created modular Cortex Inspector components:

- Branding
- Pipeline Status
- Signal Summary
- Player Scorecard
- Player Timeline
- Recommendation Card
- Explanation Panel
- Engine Diagnostics

Added Player Timeline displaying historical score evolution.

---

#### Models

Expanded domain model with persistent intelligence support.

Updated:

- EngineResult
- PlayerScorecard
- RawEvent

---

### Refactoring

- Moved intelligence ownership from the UI into Cortex.
- Score calculations now occur exclusively within ScoreEngine.
- Streamlit components no longer generate placeholder scorecards.
- Applications consume EngineResult as a presentation model.

---

### Repository Structure

Added:

```
gridiron_cortex/storage/

    event_repository.py

    json_event_repository.py

    player_scorecard_repository.py

    json_player_scorecard_repository.py
```

Added persistent storage:

```
data/cortex/

    events.jsonl

    player_scorecards.jsonl
```

---

### Architectural Improvements

- Introduced persistent player intelligence.
- Introduced event deduplication.
- Added immutable score history.
- Added repository abstraction layer.
- Established separation between reasoning and presentation.
- Continued migration toward reusable intelligence engine architecture.

---

### Current Status

Completed:

- Typed domain models
- Cortex processing pipeline
- Persistent player scorecards
- Event fingerprinting
- Duplicate detection
- Historical score tracking
- Timeline visualization
- Modular Streamlit architecture

---

### Next Milestones

Planned:

- Relationship memory
- Knowledge graph
- Confidence history
- Event replay
- Timeline visualizations
- Historical analytics
- SQLite/PostgreSQL repository implementations
- REST API

####### 2026-07-09######

### Engine Architecture

- Created `engine/` package.
- Added `CortexEngine` orchestration pipeline.
- Added placeholder modules for entity resolution, signal processing, relationship propagation, score updates, recommendations, and explanations.
- Verified the engine pipeline runs end-to-end with a sample Tank Dell event.

# Version 0.2.0 – Engine Domain Model

## Added
- Introduced typed engine models:
  - RawEvent
  - Entity
  - Signal
  - Impact
  - PlayerScorecard
  - ScoreUpdate
  - Recommendation
  - EngineResult

### Architecture
- Established a strongly typed domain model for the Cortex intelligence pipeline.
- Laid the foundation for replacing dictionary-based communication between engine modules.

## Typed Engine Refactor

- Refactored engine modules to use typed domain models.
- Updated `EntityResolver` to return `Entity` objects.
- Updated `SignalProcessor` to return a `Signal`.
- Updated `RelationshipEngine` to return `Impact` objects.
- Updated `ScoreEngine` to return `ScoreUpdate` objects.
- Updated `RecommendationEngine` to return `Recommendation` objects.
- Updated `CortexEngine` to return `EngineResult`.
- Verified the full engine pipeline still runs successfully.

## Streamlit Component Restructure

- Added `apps/streamlit/` structure.
- Added reusable branding component.
- Began separating Streamlit UI into components and pages.

## Streamlit Design Refresh

- Updated application branding to emphasize Gridiron Cortex as the intelligence engine.
- Reframed GridironGPT as the host application running Cortex.
- Reordered Streamlit navigation so Cortex Inspector appears first.
- Began moving Streamlit UI toward a component-based structure.

## Cortex Package Restructure

- Created `gridiron_cortex/` package.
- Moved `engine/` into `gridiron_cortex/engine/`.
- Moved `models/` into `gridiron_cortex/models/`.
- Updated imports to use the new package path.
- Verified the typed Cortex engine pipeline still runs successfully.

## 2026-06-22

### Added
- Added Momentum Engine for player trend acceleration analysis.
- Added momentum rankings for Top Risers and Top Fallers.
- Added first-snapshot tracking for players with limited historical data.
- Added momentum reporting to the daily pipeline.
- Added Momentum tab to the Streamlit dashboard.

### Changed
- Daily pipeline now generates:
  - RSS ingestion summary
  - Trend report
  - Momentum report
- Dashboard now exposes momentum analytics alongside existing trend analysis.

### Improved
- Expanded player intelligence layer beyond static recommendations.
- Created foundation for future momentum-based rankings and alerts.
- Improved visibility of player movement using historical score snapshots.

---

## 2026-06-21

### Added
- Added `story_dedup.py` for duplicate story detection.
- Added headline normalization for comparing similar news stories.
- Added stable `story_hash` generation for RSS article records.
- Added `story_hash` persistence to `raw_articles`.
- Added `signal_event_hash.py` for signal-level event identity.
- Added `signal_event_hash` wiring through the signal persistence flow.
- Added signal-level deduplication using the existing `unique_signal_event_hash` index.

### Changed
- RSS article records now include `story_hash`.
- Raw articles continue to upsert by `content_hash`, while also storing `story_hash` for future event-level analysis.
- Signals now upsert by `signal_event_hash` to prevent duplicate player-impact events from inflating scores.

### Fixed / Improved
- Prevented repeated ingestion runs from creating duplicate fantasy signals for the same story, player, impact, and date.
- Improved data-quality foundation for future multi-source ingestion.

---

## 2026-06-12

### Added

Article relevance classification
Player score snapshots
Snapshot service
Daily snapshot deduplication

---

## 2026-06-11

### Added

Supabase integration
raw_articles repository
signals repository
propagated_signals repository
ingestion_runs repository
signal persistence service
news persistence service
ingestion tracking

Improved:

Player matcher accuracy
Alias handling
Catalog caching
RSS ingestion pipeline

RSS Improvements:

Multi-player matching
Summary-aware extraction
Confidence tracking
Expanded signal generation

Infrastructure:

Cloud-backed persistence
Event-driven architecture
Historical audit capability

Current Pipeline:

RSS Feed
 ↓
raw_articles
 ↓
signals
 ↓
propagated_signals
 ↓
recommendations

Status:
V4 Foundation Complete

---

## 2026-06-09

### Added

#### Entity Relationship Engine

* Added JSON-driven relationship framework.
* Added support for propagating impacts between related entities.
* Added relationship validation and loading system.
* Added configurable relationship definitions via `data/relationships.json`.

#### Signal Impact API

* Added `generate_signal_impacts()`.
* Added `format_signal_impact_report()`.
* Added support for calculating system-wide impacts from a single signal.

#### Recommendation Integration

* Added propagated impact scoring to recommendation engine.
* Recommendations now support adjusted scores derived from relationship propagation.
* Recommendation rankings can incorporate downstream effects from related entities.

### Refactored

* Moved intelligence components into:

  * `gridiron_gpt/intelligence/`
* Removed duplicate intelligence module locations.
* Standardized import paths throughout intelligence engine.

### Infrastructure

* Cleaned project dependencies.
* Split runtime and development dependencies.
* Added testing support for relationship engine and signal impact API.

### Status

Phase 1 of the Impact Propagation Engine completed.

### V4 Foundation Milestone Reached

- Supabase migration started
- Event persistence implemented
- Historical score tracking implemented
- RSS ingestion operational
- Article classification operational
