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

`FantasyBestFitService` is a contextual recommendation layer downstream of production scoring. It consumes available candidates, My Team roster context, market views, and bounded scarcity input. Production ranking quality remains dominant.

```text
production ranking score ─────────────┐
active roster need ───────────────────┤
Draft Value / market opportunity ─────┤→ FantasyBestFitService
bounded scarcity signal ──────────────┘          ↓
                                         advisory fit score
                                                ↓
                                     FantasyBestFitView
                                                ↓
                                   reason / Draft Assistant
```

**Invariant:** Best Fit may reorder its own advisory list, but it does not mutate `ranking_score`, Best Available order, or Best Value order.

## Position Scarcity and Pick Timing

`FantasyPositionScarcityService` evaluates the cost of waiting at the same position using remaining depth, score drop, and tier cliffs. Production-shaped ranking objects may not carry tiers directly, so `FantasyBestFitView` uses existing market tiers to build temporary advisory-only candidates without mutating the authoritative score objects.

`FantasyPickTimingService` converts scarcity plus roster need into `TAKE NOW`, `CAN WAIT`, or `NEUTRAL` guidance.

```text
available same-position pool
        +
market tier context
        ↓
FantasyPositionScarcityService
        ↓
scarcity level / score drop / tier cliff
        ↓
FantasyPickTimingService
        ↓
TAKE NOW / CAN WAIT / NEUTRAL
```

Pick Timing answers whether the same-position pool can tolerate waiting. It does not estimate whether a specific player will survive to the user's next selection.

## Draft Turn and Wait Risk Architecture

`FantasyDraftSettings` validates league size and draft slot. `FantasyDraftTurnService` calculates snake-draft turns from those settings and the live drafted count. `FantasyWaitRiskViewService` combines that turn state with consensus ADP and delegates to `FantasyWaitRiskService`.

```text
DraftBoardState drafted count ───────────────┐
FantasyDraftSettings                         │
  ├─ league size                             │
  └─ draft slot                              │
        ↓                                    │
FantasyDraftTurnService                      │
  ├─ current overall pick                    │
  └─ next user selection                     │
                                             │
Consensus ADP ───────────────────────────────┤
                                             ↓
                               FantasyWaitRiskViewService
                                             ↓
                                  FantasyWaitRiskService
                                             ↓
                                  WaitRiskResult
                                             ↓
                                  presentation adapter
```

The presentation layer is state-aware:

- Before the user's turn, it reports **availability at the upcoming pick**.
- On the user's turn, it reports **Wait Risk** for passing until the following user selection.

This intentionally remains separate from Pick Timing. A player can be `CAN WAIT` from a positional-scarcity perspective while still carrying `HIGH WAIT RISK` because market ADP suggests that specific player will not return.

## Draft Assistant Data Flow

```text
Production Rankings
        ↓
Frozen Draft Board
        ↓
DraftBoardState ──────────────────────────────┐
        ↓                                     │
FantasyDraftPoolService                       │
  ├─ Best Available                           │
  └─ Best Value                               │
                                              │
My Team IDs ──────────────────────────────────┘
        ↓
Roster Needs / Roster Advice
        ↓
Best Fit Right Now
  ├─ Position Scarcity
  ├─ Pick Timing
  └─ Market Availability / Wait Risk
        ↓
Draft Assistant UI
```

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
990 passed
```

The suite covers runtime, persistence, production ranking, projection, tier/value, draft state, draft pool, roster advice, Best Fit, position scarcity, Pick Timing, snake-turn calculation, Wait Risk, state-aware presentation contracts, and production-shaped integration behavior. Live Streamlit validation confirms snake progression and the distinction between pre-turn availability and on-the-clock Wait Risk while the production board remains stable.
