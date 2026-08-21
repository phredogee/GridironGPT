# GridironGPT Architecture

## System Boundary

GridironGPT is the football product layer. **Gridiron Cortex** is the reusable intelligence engine.

### GridironGPT owns
- NFL provider integration and source translation.
- Football-specific data and league concepts.
- Fantasy ranking inputs and draft-day workflows.
- Runtime composition.
- Streamlit presentation.
- Commissioner features.

### Cortex owns
- `RawEvent` intelligence processing.
- Entity resolution and signal interpretation.
- Relationship reasoning and propagation.
- Multidimensional scorecards.
- Recommendation confidence and explanations.
- Event-bus decision history.
- Persistence and Replay of Cortex decisions.

Providers do not call engine internals. They produce source records that the shared ingestion layer normalizes into the Cortex input contract.

## Runtime Architecture

```text
NFL Sources
    ↓
Provider Adapters
    ↓
IngestionService
    ↓
RawEvent[]
    ↓
CortexFacade.process_event()
    ↓
Resolve → Interpret → Propagate → Score
    ↓
Scorecards + Recommendations + Explanations
    ↓
Persistent Event History / Replay
    ↓
GridironGPT product services + Streamlit
```

Downstream Cortex failures are fail-open at the ingestion boundary so a healthy provider fetch is not retried because intelligence processing failed.

## Production Fantasy Ranking Architecture

The production board combines independent evidence sources. Missing evidence is unavailable evidence rather than negative evidence, and available weights are renormalized.

```text
Historical fantasy production ─┐
Current ADP / market ──────────┤
Recent role / usage ───────────┤
Cortex player intelligence ────┤
Canonical availability ────────┤→ weighted scorer
Projected fantasy production ──┘        ↓
                                  anchor validation
                                         ↓
                               sorted production board
                                         ↓
                         tiers / value / explanations
```

### Ranking evidence
- **Baseline** — normalized historical fantasy production.
- **Market** — current-season ADP/market evidence.
- **Role** — recent usage and opportunity evidence.
- **Cortex** — latest player intelligence.
- **Availability** — canonical football-state availability.
- **Projection** — normalized projected fantasy production at its configured production weight.

Projected points and projected PPG are also exposed directly in the UI and exports. Projection influence is part of the production ranking model; presentation code must not apply a second projection adjustment.

### Anchor-evidence rule

Secondary context cannot manufacture a meaningful fantasy ranking by itself. A player must have primary ranking evidence such as historical production or current market evidence before contextual signals can influence the final score.

## Single Authoritative Ranking Source

The production `FantasyRankingDataService` / ranking population is the authoritative source for player order across the current UI and CLI paths. Legacy competing ranking formulas must not be reintroduced as alternate definitions of GridironGPT ranking.

```text
Production ranking population
        ↓
Overall / position views
        ↓
Tier + market metadata
        ↓
Best Available / Best Value / CLI presentation
```

## Live Draft-State Architecture

Live draft behavior is intentionally separated from player scoring.

### DraftBoardState

`DraftBoardState` owns ordered draft state and ownership.

```text
DraftBoardState
  picks[]
    ├─ player_id
    └─ ownership
         ├─ OTHER_TEAM
         └─ MY_TEAM
```

It preserves pick order for Undo Last behavior while exposing both `drafted_ids` and `my_team_ids`. Restore and reset operate on this state. Streamlit session state stores the live board state for the current session.

### FantasyDraftPoolService

Draft-pool filtering is a pure downstream service:

```text
production population + drafted IDs
              ↓
    FantasyDraftPoolService
      ├─ remaining_population
      ├─ best_available_scores
      └─ best_value_scores
```

The service removes drafted players but does not rescore the remaining population. Best Available preserves production ranking order. Best Value preserves the existing positive Draft Value calculation and ordering.

### Roster Needs

`FantasyRosterNeedsService` evaluates **My Team** separately from the league draft pool. Current starter-oriented defaults are:

```text
QB 1
RB 2
WR 2
TE 1
```

The targets are configurable and report current count, target, and remaining deficit. Extra players never create a negative deficit.

### Advisory Layer

`FantasyRosterAdviceService` converts roster deficits into presentation-safe advice such as:

```text
Roster Needs: WR (1) · TE (1)
Fills WR need
Fills TE need
```

This layer is deliberately downstream of scoring.

**Invariant:** roster state does not modify production `ranking_score`, Best Available order, or Best Value order.

This protects a key architectural distinction: a player can remain highly ranked while being a poor fit for a specific roster at a specific moment.

## Draft Assistant Data Flow

```text
Production Rankings
        ↓
Frozen Draft Board
        ↓
DraftBoardState ───────────────┐
        ↓                      │
FantasyDraftPoolService        │
  ├─ Best Available            │
  └─ Best Value                │
                               │
My Team IDs ───────────────────┘
        ↓
FantasyRosterNeedsService
        ↓
FantasyRosterAdviceService
        ↓
Draft Assistant UI
```

The next planned layer, **Best Fit Right Now**, should sit beneath the Draft Assistant as an advisory recommendation service rather than rewriting the production ranking model.

## Ranking Explanations and Market Views

`FantasyRankingExplanationService` explains a score that already exists; it does not rescore the player. Tier and market services derive position rank, tier, ADP context, and Draft Value from the production population.

Draft Value remains conceptually:

```text
consensus ADP - production overall rank
```

Because production overall rank already includes the configured ranking evidence, Draft Value must not independently reapply those inputs.

## Persistence and Replay

Core Cortex persistence uses repository-backed JSON/JSONL implementations. Important artifacts include event history, player scorecards, deduplication state, score history, and ingestion-run observability.

Replay reads persisted decision history and reconstructs a prior decision; it does not rerun the original article through Cortex.

## Presentation Architecture

```text
Cortex/domain services
        ↓
presentation/advisory services
        ↓
reusable Streamlit components/pages
```

Presentation code may format, filter, annotate, and explain domain output. It should not become a competing intelligence or ranking engine.

## Commissioner Architecture

Commissioner services remain deterministic football-product services separate from Cortex intelligence scoring. They cover league settings, scheduling, constraints, analytics, exports, playoffs, draft workflows, and league history.

## Extension Rules

### New ranking evidence
Normalize the source, preserve provenance, and add it through the production scorer rather than directly changing final rank order.

### New draft advice
Consume production ranking output plus draft/roster context. Keep the advice layer separate from `ranking_score` unless a deliberate scoring-model change is explicitly tested and approved.

### New persistence backend
Implement repository contracts without changing scoring/reasoning consumers.

### New UI surface
Consume facade/domain/advisory services rather than embedding domain rules directly in Streamlit.

## Testing Boundary

Current verified full regression checkpoint:

```text
869 passed
```

The regression suite now covers ingestion/runtime handoff, persistence and Replay, integrated ranking evidence, projection-weight production behavior, tier/value consumers, CLI ranking-source unification, draft-pool filtering, ownership-aware draft state, roster-needs evaluation, and roster-advice presentation semantics.
