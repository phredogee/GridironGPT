# GridironGPT Architecture

## System Boundary

GridironGPT is the football product layer. **Gridiron Cortex** is the reusable intelligence engine.

### GridironGPT owns
- NFL provider integration
- Source-record translation and normalization orchestration
- Player catalog and football aliases
- Football-specific data and league concepts
- Fantasy and commissioner workflows
- Runtime composition
- Streamlit presentation and visualization

### Cortex owns
- `RawEvent` intelligence processing
- Entity resolution
- Signal interpretation
- Relationship reasoning and propagation
- Multidimensional scorecards
- Recommendations and confidence
- Explanations and evidence chains
- Event-bus decision history
- Persistence and Replay of Cortex decisions

The architectural rule is that providers do not call engine internals. They produce source records. The shared ingestion layer normalizes those records into the Cortex input contract.

## v1.0 Runtime Architecture

```text
NFL Sources
  ├─ ESPN NFL RSS
  ├─ NBC Sports / ProFootballTalk
  ├─ RotoWire NFL
  └─ nflverse / nflreadpy
          ↓
Provider Adapters
          ↓
IngestionService
  fetch → retry/backoff → normalize
          ↓
RawEvent[]
          ↓
optional event_processor hook
          ↓
CortexFacade.process_event()
          ↓
Entity Resolution
          ↓
Signal Processing
          ↓
Relationship Propagation
          ↓
Score Updates / Player Scorecards
          ↓
Recommendations + Explanations
          ↓
Event Bus
          ↓
Persistent Event History
          ↓
Dashboard / Advisor / Players / Explorer
Inspector / Activity / Replay / Mission Control
```

## Ingestion Boundary

`IngestionService` is the shared provider boundary. It owns provider execution, retry behavior, normalization, ingestion health, and optional downstream event processing.

Runtime composition injects `cortex.process_event` through the service's event-processor hook. This means every normalized event can enter Cortex without adding Cortex dependencies to ESPN, NBC, RotoWire, nflverse, or future adapters.

### Fail-open rule

A downstream Cortex exception must not convert a successful provider fetch into a provider failure. The event-processor hook catches downstream exceptions, logs them, and allows ingestion to succeed. This prevents unnecessary provider retries when the source itself was healthy.

```text
Provider succeeds
      ↓
RawEvent created
      ↓
Cortex unavailable
      ↓
log downstream failure
      ↓
ingestion remains successful
```

## Cortex Processing Contract

`RawEvent` is the boundary object between GridironGPT ingestion and Cortex. Source provenance such as source IDs and provider metadata travels with the event evidence rather than through provider-specific engine APIs.

A Cortex decision can produce:
- resolved entities
- interpreted signal
- direct and propagated impacts
- score updates
- player scorecards
- recommendations
- explanation/evidence chains
- event-bus records for each observable processing stage

Deduplication occurs before duplicate evidence can create duplicate downstream decisions.

## Correlation and Decision History

Each input event has a stable fingerprint/correlation identity. Cortex publishes processing events to its event bus using that correlation so a complete decision trail can be queried later.

```text
RawEvent fingerprint
       ↓
correlation_id
       ↓
Cortex pipeline events
       ↓
cortex_events.jsonl
       ↓
ReplayEngine.by_correlation(...)
```

Replay reads persisted history. It does **not** rerun the original article through Cortex.

## Persistence and Restart Semantics

Core Cortex persistence currently uses repository-backed JSON/JSONL implementations.

Important persisted artifacts include:
- Cortex event history
- player scorecards
- event/deduplication state
- historical score information
- ingestion-run observability

The v1.0 end-to-end test explicitly simulates an application restart by constructing a new `CortexFacade` against the same data directory. The restarted facade reloads persisted event history and scorecard state, and Replay reconstructs the original decision from that persisted history.

This establishes the required invariant:

> A Cortex decision is not only explainable while the process is alive; its decision trail survives restart.

## Runtime Composition

### Streamlit

`streamlit_app.py` creates one `CortexFacade` in Streamlit session state and shares that facade across Cortex-facing pages and services. Pages should receive the facade rather than construct independent engines.

```text
st.session_state.cortex_facade
          ↓
   shared CortexFacade
    ↙     ↓      ↘
Inspector Explorer Activity/other Cortex views
```

The Ingestion Status surface reads persisted ingestion-run history and does not need to instantiate a second Cortex engine.

### Runtime ingestion

`build_runtime_ingestion_service(cortex, ...)` composes the production ingestion service with the supplied facade. `ingest_all(cortex)` uses that runtime composition for the default provider set.

## Manual Inspector Path

The Cortex Inspector intentionally constructs diagnostic `RawEvent` objects and calls `cortex.process_event()` directly when the user chooses to analyze an event. This is not legacy ingestion and should not be removed.

```text
Production path: Provider → IngestionService → RawEvent → Cortex
Diagnostic path: Inspector input → RawEvent → Cortex
```

Both paths share the same Cortex facade contract.

## Intelligence and Propagation

Cortex models football relationships such as passing, rushing, backup, target competition, and depth-chart competition. Propagation applies relationship semantics, strength, confidence, and hop decay. Strongest-path behavior prevents duplicate graph paths from multiplying the same downstream effect.

## Multidimensional Scoring

Persistent player intelligence includes dimensions such as:
- Overall
- Opportunity
- Health
- Hype
- Risk
- Momentum

Scorecards are keyed by engine player identity rather than display name. Presentation code may derive visual summaries but must not become a second scoring engine.

## Presentation Architecture

```text
Cortex/domain services
        ↓
view + visualization models
        ↓
reusable Streamlit components
        ↓
page modules
        ↓
shared app shell/navigation
```

Primary product surfaces include Dashboard, Advisor, Player Intelligence, Trends/Trajectory, Cortex Explorer, Cortex Inspector, Ingestion Status, and Cortex activity/decision views.

## Commissioner Architecture

Commissioner capabilities are deterministic football-product services and remain separate from Cortex intelligence scoring.

```text
League Settings
      ↓
Schedule Generator
      ↓
Constraint / Balance Logic
      ↓
Schedule Analytics / Alternatives
      ↓
Exports / Delivery
```

Other services cover playoff brackets, draft workflows, league history, and commissioner insights.

## Extension Points

### New provider
Implement the provider adapter/source-record contract. Do not add Cortex-specific logic to the adapter.

### New intelligence stage
Add it behind the Cortex facade/pipeline contracts and publish observable events where the stage contributes to the decision trail.

### New persistence backend
Implement repository contracts without changing scoring/reasoning consumers.

### New UI surface
Consume facade/domain services or presentation models. Avoid reading engine implementation details directly from Streamlit pages.

## Testing Boundary

Current verified full regression checkpoint:

```text
702 passed
```

The regression suite includes automatic ingestion into Cortex, downstream fail-open behavior, runtime composition, persistent scorecards/event history, restart behavior, and Replay reconstruction.

## v1.0 Architectural Status

The core architecture is in stabilization rather than subsystem expansion. Before release/merge:

1. Keep contributor documentation synchronized with the implemented boundaries.
2. Remove stale presentation metadata and obsolete references.
3. Run the full regression suite after stabilization changes.
4. Perform a Streamlit smoke test across the primary pages.
5. Reconcile the Cortex branch with `main` without reintroducing stale README architecture.
6. Prepare the release/merge boundary.
