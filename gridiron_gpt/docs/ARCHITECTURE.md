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

## Fantasy Ranking Architecture

The fantasy ranking pipeline combines independent evidence sources instead of allowing a single provider or presentation layer to dictate rankings.

```text
Historical fantasy production ─┐
2026 ADP / market evidence ────┤
Recent role / usage ───────────┤
Cortex player intelligence ────┼→ input adapter → weighted scorer
Canonical availability ────────┘                    ↓
                                      anchor-evidence validation
                                                   ↓
                                      sorted ranking population
                                                   ↓
                                      rank-aware explanation
```

### Ranking evidence

- **Baseline** — normalized historical fantasy production.
- **Market** — current-season ADP normalized across the configured draft pool.
- **Role** — recent observed usage, normalized within position with source provenance.
- **Cortex** — latest available Cortex player scorecard intelligence.
- **Availability** — canonical football-state availability evidence.

Missing evidence is treated as unavailable evidence rather than negative evidence. The scorer renormalizes around available weighted inputs.

### Anchor-evidence rule

Availability, role, or neutral Cortex state cannot manufacture a meaningful fantasy ranking by themselves. A player must have primary ranking evidence such as historical production or current market/ADP evidence before secondary context can influence the result.

This keeps prospects with legitimate current market evidence rankable while excluding roster-only players whose only positive signal is that they exist and are available.

### Cross-source identity

Historical and ADP display names are conservatively normalized before matching canonical players. Cortex scorecards prefer canonical player IDs and can fall back to a conservative name/team match for legacy scorecards whose identifiers predate canonical football-state IDs.

### Ranking explanations

`FantasyRankingExplanationService` explains the score that already exists; it does not rescore the player. `FantasyRankingPopulationService` exposes `explained_overall` alongside the existing `overall` and `by_position` views.

Explanations can identify:
- strong or elite primary evidence,
- materially weak evidence,
- neutral Cortex evidence,
- source provenance,
- explicitly missing evidence,
- the player's final rank and ranking score.

Availability remains visible as evidence but is not described as an elite fantasy strength. Neutral Cortex scores are not presented as negative evidence.

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

### New ranking evidence
Normalize the source into the ranking input contract, preserve provenance, and add it through the scorer rather than directly modifying final rank order.

### New intelligence stage
Add it behind the Cortex facade/pipeline contracts and publish observable events where the stage contributes to the decision trail.

### New persistence backend
Implement repository contracts without changing scoring/reasoning consumers.

### New UI surface
Consume facade/domain services or presentation models. Avoid reading engine implementation details directly from Streamlit pages.

## Testing Boundary

Current verified full regression checkpoint:

```text
780 passed
```

The regression suite includes automatic ingestion into Cortex, downstream fail-open behavior, runtime composition, persistent scorecards/event history, restart behavior, Replay reconstruction, fantasy ranking evidence integration, anchor-evidence validation, and ranking explanation semantics.

## v1.0 Architectural Status

The core architecture is in stabilization rather than subsystem expansion. Before release/merge:

1. Keep contributor documentation synchronized with the implemented boundaries.
2. Remove stale presentation metadata and obsolete references.
3. Run the full regression suite after stabilization changes.
4. Perform a Streamlit smoke test across the primary pages.
5. Reconcile the Cortex branch with `main` without reintroducing stale README architecture.
6. Prepare the release/merge boundary.
