# GridironGPT Known Issues

This document tracks known technical limitations, unresolved architectural concerns, and areas requiring future validation.

Items that have been completed should be moved to `CHANGELOG.md` rather than retained here.

Current automated test baseline:

```text
274 passed
```

---

# Data Ingestion

## Source Coverage

Current ingestion does not yet provide the breadth of NFL information required for the long-term Cortex vision.

Existing or partially implemented sources include:

- ESPN / RSS
- NBC Sports
- RotoWire
- nflverse / nflreadpy
- statistical pipelines

### Remaining Work

- Standardize source adapters
- Add additional reliable NFL sources
- Normalize provider metadata
- Normalize timestamps
- Improve injury-report ingestion
- Improve transaction ingestion
- Add practice-participation data
- Expand usage and statistical data
- Evaluate team and beat-reporter sources

This is a primary focus of Phase C.

---

## Ingestion Reliability

External providers do not yet share a unified reliability architecture.

### Needed

- Retry handling
- Exponential backoff
- Timeouts
- Rate-limit awareness
- Source failure isolation
- Cache strategy
- Partial recovery
- Structured ingestion logging
- Source health monitoring

A failed external provider should not prevent unrelated providers from supplying Cortex with events.

---

## Cross-Source Deduplication

Cortex supports event fingerprinting and canonical evidence aggregation, but cross-provider event identity still requires improvement.

Multiple sources reporting the same football development should become:

```text
ESPN ───────┐
NBC ────────┤
NFL ────────┤
            ▼
       Canonical Event
```

rather than producing multiple independent score changes.

### Remaining Work

- Cross-source event fingerprints
- Headline similarity
- Time-window matching
- Player/entity-aware clustering
- Canonical event identity
- Duplicate headline clustering
- Provenance preservation

---

## Ingestion Observability

The system does not yet provide complete operational metrics for ingestion.

Future metrics should include:

- Events received
- Events accepted
- Events rejected
- Duplicate events
- Canonical events created
- Source failures
- Last successful ingestion
- Processing latency
- Events by provider

---

# Player Matching

The current matcher prioritizes precision over recall.

## Known Limitations

- Ambiguous surnames may intentionally be ignored.
- Headlines without identifiable player names may be skipped.
- Nickname and alias coverage is incomplete.
- Provider naming differences can still cause failed matches.
- Some nflverse depth-chart entries do not contain GSIS IDs.

The relationship builder currently mitigates missing GSIS IDs by falling back to normalized player-name matching.

### Future Improvements

- Expanded alias catalog
- Historical aliases
- Provider-specific aliases
- Improved suffix handling
- More robust normalized identity model
- Persistent canonical player IDs

---

# Statistical Signal Generation

Current statistical signal generation remains relatively simple.

Existing logic primarily compares recent statistical appearances.

### Future Improvements

- Rolling 3-game baselines
- Rolling seasonal averages
- Position-specific thresholds
- Strength-of-schedule adjustments
- Opponent normalization
- Snap-share trends
- Route participation
- Target share
- Carry share
- Red-zone usage
- Efficiency metrics

These inputs should eventually strengthen Cortex signal classification and opportunity reasoning.

---

# Signal Confidence Calibration

Cortex now supports evidence-aware confidence, corroboration, and contradiction penalties, but the underlying values remain heuristic.

### Current Limitation

Confidence has not been calibrated against a large historical outcome dataset.

### Future Work

- Historical accuracy tracking
- Source reliability weighting
- Bayesian or probabilistic calibration
- Provider-specific reliability
- Signal-category calibration
- Confidence-vs-outcome analysis

The objective is for a Cortex confidence value to eventually have measurable historical meaning.

---

# Contradiction Detection

Contradiction detection is implemented and integrated into Cortex reasoning.

Current behavior supports:

- Positive/negative evidence conflict
- Conflict severity
- Confidence penalties
- Conflicting-source attribution
- Neutral-source exclusion

## Remaining Limitations

Detection is currently keyword-driven.

This can miss semantic contradictions where different wording describes incompatible football states.

Examples:

```text
Expected to suit up Sunday
```

versus:

```text
Not likely to be available this weekend
```

Neither necessarily requires identical injury keywords.

### Future Improvements

- Semantic contradiction classification
- Temporal contradiction handling
- Injury-status state models
- Source chronology
- Superseding reports
- Structured status comparison

---

# Relationship Graph

The NFL relationship graph is now depth-aware and dynamically refreshable.

Current graph construction uses:

- nflverse player catalog
- nflverse depth charts
- active roster status
- latest available team depth-chart snapshots
- fantasy-position filtering
- depth-rank filtering

Current development graph size is approximately:

```text
579 active relationships
```

across all 32 NFL teams.

---

## Relationship Refresh Scheduling

Dynamic relationship refresh and diffing are implemented.

The remaining limitation is **orchestration**.

Refreshes currently need an external trigger rather than being managed by a production scheduling system.

### Future Work

Determine appropriate refresh schedules for:

- Offseason roster movement
- Training camp
- Preseason
- Regular season
- Trade deadline
- Injury-driven depth changes

This should be addressed alongside Phase C ingestion orchestration.

---

# Relationship Calibration

Current relationship values are heuristic.

Propagation currently considers:

- Relationship strength
- Relationship confidence
- Relationship semantics
- Hop decay

These values have not yet been calibrated against historical fantasy outcomes.

### Future Inputs

Potential calibration data includes:

- Snap counts
- Route participation
- Target share
- Carry share
- Red-zone usage
- Coaching tendencies
- Historical fantasy production
- Depth-chart movement
- Player efficiency

---

# Relationship Semantics Coverage

Semantic propagation is implemented for the current primary offensive relationship graph.

Current important semantics include:

```text
throws_to
hands_off_to
backs_up
target_competitor
depth_chart_competitor
```

## Remaining Limitation

The semantic model does not yet cover the full football ecosystem.

Potential future relationships include:

```text
offensive_line_supports
coached_by
coordinator_for
injury_replacement_for
rookie_competes_with
blocks_for
defends_against
team_context
```

New relationship types should only be introduced when they provide meaningful fantasy intelligence.

Graph density should not be increased simply for completeness.

---

# Static Hop Decay

Current propagation decay is heuristic:

```text
Hop 0 = 1.00
Hop 1 = 0.85
Hop 2 = 0.65
Hop 3 = 0.40
Hop 4+ = 0.20
```

### Future Work

- Configurable decay profiles
- Relationship-specific decay
- Signal-specific decay
- Historically calibrated decay
- Learned decay functions

The current values are acceptable for development but should eventually be validated empirically.

---

# Multidimensional Scoring Calibration

Cortex now supports category-aware multidimensional scoring.

Current dimensions include:

```text
overall
opportunity
health
hype
risk
momentum
```

## Remaining Limitation

Dimension weights and category effects remain heuristic.

Future historical validation should determine whether:

- Recovery affects health appropriately
- Injury affects risk appropriately
- Opportunity signals affect opportunity appropriately
- Propagated signals should use different dimensional weights
- Overall score weighting accurately reflects fantasy value

---

# Multiple Simultaneous Events

The engine is well tested for individual event processing, but complex simultaneous developments require additional validation.

Examples:

```text
Starting RB injured
Backup promoted
Team signs veteran RB
Coach announces committee
```

All may occur within a short time window.

### Future Work

- Event ordering
- Event aggregation
- Competing signal resolution
- Temporal precedence
- Score-update consolidation
- Recommendation stability

---

# Historical Validation

The Cortex reasoning system has not yet been comprehensively replayed against historical NFL seasons.

This is one of the largest remaining validation requirements.

### Future Work

Replay historical data and measure:

- Signal accuracy
- Propagation accuracy
- Recommendation accuracy
- Prediction accuracy
- Confidence calibration
- Relationship effectiveness
- Category-specific scoring performance
- False-positive rate
- False-negative rate

Historical validation should eventually drive parameter calibration rather than relying primarily on manually selected values.

---

# Relationship Learning

Relationship strengths and semantic multipliers are currently engineered rather than learned.

Future versions may estimate relationship influence using:

- Historical fantasy scoring
- Snap counts
- Target share
- Route participation
- Carry share
- Player usage
- Coaching tendencies
- Depth-chart history
- Machine learning

Learned relationships should supplement explainability rather than create opaque graph behavior.

---

# Performance and Scalability

Current graph traversal and JSONL persistence are sufficient for development.

Production-scale performance has not yet been benchmarked.

### Benchmark Areas

- Graph traversal latency
- Graph size scalability
- Propagation throughput
- Repository read latency
- JSONL growth
- Memory usage
- Concurrent event processing
- Canonical-event clustering
- Historical scorecard queries

Performance optimization should be driven by measured bottlenecks rather than premature infrastructure changes.

---

# JSONL Persistence

Cortex currently stores local knowledge in:

```text
data/cortex/
├── events.jsonl
├── player_scorecards.jsonl
└── relationships.jsonl
```

This is appropriate for the current development stage but is not intended to be the final production persistence architecture.

## Known Limitations

- Linear file scans
- Increasing read cost as history grows
- Limited concurrent-write support
- No transactional guarantees
- Limited query capabilities
- Manual archival requirements

Repository abstractions are intentionally designed to permit future migration to database-backed storage.

---

# Cortex Inspector

The Cortex Inspector currently visualizes:

- Pipeline status
- Evidence and confidence
- Cognitive trace
- Evidence graph
- Propagation
- Predictions
- Player scorecards
- Score history
- Explanations
- Diagnostics

The Propagation view exposes:

- Direct impacts
- Downstream propagated impacts
- Hop count
- Propagation weight
- Relationship strength
- Relationship confidence
- Propagation reasoning

## Remaining Inspector Limitations

The Inspector does not yet provide:

- Interactive node-based graph visualization
- Clickable propagation nodes
- Live animated pipeline execution
- Side-by-side player comparison
- Event markers over historical score charts
- Filtering by propagation depth
- Filtering by relationship type
- Graph-level search
- Historical propagation replay

These are presentation limitations rather than core Cortex blockers.

---

# External Dependency Reliability

GridironGPT depends on external systems including:

- RSS providers
- nflverse / nflreadpy
- Supabase
- Future NFL data providers

Network or provider failures remain an operational concern.

### Desired Behavior

External failures should result in:

```text
degraded functionality
```

rather than:

```text
application failure
```

Phase C should establish consistent failure-isolation patterns across ingestion providers.

---

# Legacy Architecture

Some legacy GridironGPT components remain while Cortex extraction and migration continue.

Examples may include:

- Legacy relationship definitions
- Older semantic pipelines
- Duplicate CLI functionality
- Transitional application imports

### Remaining Migration Work

- Retire obsolete semantic pipeline components
- Remove duplicate CLI modules where appropriate
- Complete remaining PHRED migration work
- Continue standalone Cortex repository separation
- Eliminate application dependencies on Cortex internals where facade access is sufficient

Legacy components should only be removed after replacement paths are covered by tests.

---

# Standalone Cortex Extraction

Gridiron Cortex is moving toward an independently reusable engine/library.

## Remaining Concerns

- Finalize stable public API
- Reduce GridIronGPT-specific assumptions inside Cortex
- Formalize extension/plugin interfaces
- Establish package versioning
- Determine long-term repository ownership of shared models
- Prevent duplicated implementations between repositories

The extraction should not interrupt active GridironGPT development.

---

# Not Currently Considered Blockers

The following capabilities are desirable but are **not required for Phase C**:

- Interactive knowledge-graph visualization
- Machine-learned relationships
- Historical replay UI
- Mobile application
- Public Cortex API
- Dynasty-specific intelligence
- Full Gridiron Codex
- Automated parameter learning

These should not distract from establishing a reliable ingestion architecture.

---

# Resolved During Phase B

The following previous limitations are now resolved and should not be treated as active known issues:

- Persistent relationship graph
- Graph traversal
- Multi-hop propagation
- Cycle protection
- Strongest-path selection
- Semantic relationship propagation
- Direction-reversing competitive propagation
- Relationship-aware propagation weights
- Dynamic relationship diffing
- Stale relationship detection
- Idempotent relationship refresh
- Category-aware scoring
- Multidimensional player scorecards
- Propagated semantic scoring
- Contradiction detection
- Contradiction confidence penalties
- Conflicting-source attribution
- Relationship-aware explanation chains
- Propagation metadata in explanations
- End-to-end Phase B integration validation

---

# Current Engineering Status

| Component | Status |
|---|---|
| Cortex Facade | ✅ Complete |
| Knowledge Service | ✅ Complete |
| Knowledge Graph | ✅ Complete |
| Graph Traversal | ✅ Complete |
| Relationship Persistence | ✅ Complete |
| Relationship Refresh | ✅ Complete |
| Propagation Planner | ✅ Complete |
| Multi-Hop Propagation | ✅ Complete |
| Cycle Protection | ✅ Complete |
| Strongest Path Selection | ✅ Complete |
| Semantic Propagation | ✅ Complete |
| Multidimensional Scoring | ✅ Complete |
| Contradiction Detection | ✅ Complete |
| Prediction Integration | ✅ Complete |
| Recommendation Intelligence | ✅ Complete |
| Explanation Integration | ✅ Complete |
| Phase B Integration Gate | ✅ Complete |
| Unified Ingestion Architecture | ▶ Phase C |
| Source Reliability Layer | ▶ Phase C |
| Cross-Source Deduplication | ▶ Phase C |
| Historical Validation | 🔮 Future |
| Learned Relationships | 🔮 Future |

---

# Current Test Baseline

Phase B closed with:

```text
274 passed
```

Any Phase C architectural work should preserve this baseline while adding ingestion-specific tests.

---

# Primary Next Risk

The primary engineering risk has shifted.

During Phase B, the major risk was:

```text
Can Cortex reason correctly?
```

The next risk is:

```text
Can Cortex reliably receive clean, timely,
non-duplicated information from multiple
external NFL sources?
```

That is the primary problem Phase C is intended to solve.
