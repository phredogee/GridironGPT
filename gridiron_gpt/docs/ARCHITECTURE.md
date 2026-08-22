# GridironGPT Architecture

## System Boundary

GridironGPT is the football product layer. **Gridiron Cortex** is the reusable intelligence engine. Cortex owns reusable reasoning, scorecards, recommendation confidence, explanations, event history, persistence, and Replay. GridironGPT owns NFL integrations, football-domain concepts, fantasy ranking inputs, draft workflows, runtime composition, Streamlit presentation, and commissioner features.

## Runtime Architecture

```text
NFL Sources → Provider Adapters → IngestionService → RawEvent[]
    → CortexFacade.process_event()
    → Resolve → Interpret → Propagate → Score
    → Scorecards + Recommendations + Explanations
    → Persistent Event History / Replay
    → GridironGPT product services + Streamlit
```

Downstream Cortex failures are fail-open at the ingestion boundary so a healthy provider fetch is not retried because intelligence processing failed.

## Production Fantasy Ranking Architecture

Independent evidence sources feed one authoritative production scorer. Missing evidence is unavailable rather than negative, and available weights are renormalized.

```text
Historical production ─┐
Current ADP / market ───┤
Recent role / usage ────┤
Cortex intelligence ────┤→ weighted scorer → anchor validation → production board
Availability ────────────┤                                      ↓
Projected production ────┘                              tiers / value / explanations
```

Projection influence is part of the production ranking model at its configured weight; presentation code must not apply a second production adjustment.

## Single Authoritative Ranking Source

`FantasyRankingDataService` and its ranking population are authoritative for current UI and CLI ordering. Best Available preserves this order. Best Value derives market opportunity from it. Advisory services consume it downstream.

## Live Draft-State Architecture

`DraftBoardState` owns ordered pick history and `MY_TEAM` / `OTHER_TEAM` ownership. `FantasyDraftPoolService` removes drafted players without rescoring remaining players.

```text
production population + drafted IDs
              ↓
    FantasyDraftPoolService
      ├─ remaining_population
      ├─ best_available_scores
      └─ best_value_scores
```

`FantasyRosterNeedsService` evaluates My Team separately with starter-oriented defaults of QB 1, RB 2, WR 2, and TE 1. `FantasyRosterAdviceService` converts deficits into presentation-safe summaries and badges.

## Best Fit Right Now

`FantasyBestFitService` is a contextual recommendation layer downstream of production scoring. It consumes available candidates, My Team roster context, and market views. Its initial conservative heuristic keeps production ranking quality dominant while allowing modest active-roster-need and capped Draft Value adjustments.

```text
production ranking score ─────────────┐
active roster need ───────────────────┤→ FantasyBestFitService
Draft Value / market opportunity ─────┘          ↓
                                         advisory fit score
                                                ↓
                                     FantasyBestFitView
                                                ↓
                                   reason / Draft Assistant
```

`FantasyBestFitView` converts recommendations into UI-ready explanations such as `fills active roster need` and `positive draft value`.

**Invariant:** Best Fit may reorder its own advisory list, but it does not mutate `ranking_score`, Best Available order, or Best Value order.

## Draft Assistant Data Flow

```text
Production Rankings
        ↓
Frozen Draft Board
        ↓
DraftBoardState ──────────────────────┐
        ↓                             │
FantasyDraftPoolService               │
  ├─ Best Available                   │
  └─ Best Value                       │
                                      │
My Team IDs ──────────────────────────┘
        ↓
Roster Needs / Roster Advice
        ↓
Best Fit Right Now
        ↓
Draft Assistant UI
```

The next planned advisory input is **positional scarcity / tier-drop awareness**. It should quantify the cost of waiting at a position without becoming a second production ranking engine.

## Ranking Explanations and Market Views

Ranking explanations explain an existing score rather than rescoring it. Tier and market services derive position rank, tier, ADP context, and Draft Value from the production population. Draft Value remains conceptually `consensus ADP - production overall rank`.

## Persistence and Replay

Core Cortex persistence uses repository-backed JSON/JSONL implementations for event history, player scorecards, deduplication state, score history, and ingestion-run observability. Replay reconstructs persisted decision history rather than rerunning the original source through Cortex.

## Extension Rules

- New ranking evidence enters through the production scorer with normalization and provenance.
- New draft advice consumes production output plus contextual state and remains separate from `ranking_score` unless an explicit scoring-model change is tested and approved.
- New UI surfaces consume domain/advisory services rather than embedding intelligence rules directly in Streamlit.
- New persistence backends implement repository contracts without changing consumers.

## Testing Boundary

Current verified full regression checkpoint:

```text
878 passed
```

The suite covers the established runtime, persistence, ranking, projection, tier/value, draft-state, draft-pool, roster-needs/advice boundaries plus Best Fit service and view-model behavior. Streamlit smoke validation confirms Best Fit responds to My Team context while the production board remains stable.
