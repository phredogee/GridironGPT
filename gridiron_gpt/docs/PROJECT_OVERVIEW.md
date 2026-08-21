# GridironGPT Project Overview

## Vision

GridironGPT is a fantasy-football intelligence platform powered by **Gridiron Cortex**. It converts NFL news, structured football evidence, market context, historical production, projections, and live draft state into explainable player intelligence and fantasy decision support.

GridironGPT is the football product layer. Cortex owns reusable intelligence and reasoning; GridironGPT owns football-specific ingestion, fantasy workflows, draft state, presentation, and commissioner features.

## Current System

```text
NFL sources / nflverse / market data
                ↓
         provider adapters
                ↓
        IngestionService
                ↓
          RawEvent contract
                ↓
          Gridiron Cortex
                ↓
resolve → classify → propagate → score → explain
                ↓
scorecards + event history + replay
                ↓
GridironGPT product services and Streamlit UI
```

## Fantasy Ranking Pipeline

The production fantasy board combines independent evidence sources and keeps presentation logic downstream of scoring.

```text
Historical production ─┐
Current ADP / market ───┤
Recent role / usage ────┤
Cortex intelligence ────┤→ weighted production ranking
Availability ────────────┤
Projected production ────┘
                         ↓
                frozen draft board
                         ↓
          tiers / value / explanations
                         ↓
               Draft Assistant
```

Projected production is now active in the production ranking model at its configured production weight. Projection values remain visible as projected points and projected PPG in the UI and exports.

## Live Draft Assistant

Draft Mode now maintains explicit live draft state rather than treating drafted players as a flat UI-only list.

```text
DraftBoardState
  ├─ ordered drafted-player history
  ├─ Other Team ownership
  └─ My Team ownership
           ↓
FantasyDraftPoolService
  ├─ remaining population
  ├─ Best Available
  └─ Best Value
           ↓
FantasyRosterNeedsService
           ↓
FantasyRosterAdviceService
           ↓
Draft Assistant advisory context
```

Current live behavior includes:
- Marking players drafted by another team.
- Assigning a drafted player to **My Team**.
- Undo, restore, and reset behavior.
- Removing drafted players from Best Available and Best Value.
- Preserving the frozen production ranking order.
- Tracking starter-oriented roster needs for QB, RB, WR, and TE.
- Displaying advisory badges such as `Fills TE need`.

Roster context is intentionally **advisory only** at this stage. It does not modify production `ranking_score`, Best Available ordering, or Best Value ordering.

## Major Capabilities

### Football Intelligence
- Multi-source ingestion and normalization.
- Duplicate-safe event processing.
- Entity resolution and signal classification.
- Relationship-aware propagation.
- Persistent multidimensional player scorecards.
- Recommendation, confidence, evidence, and explanations.
- Momentum, trends, and decision history.

### Fantasy Decision Support
- Integrated fantasy rankings.
- Current market/ADP context.
- Projected points and projected PPG.
- Position ranks and tiers.
- Draft Value vs. ADP.
- Best Available and Best Value.
- Live draft-state tracking.
- My Team ownership.
- Roster-needs advisory context.
- Excel and PDF ranking exports.

### Persistence and Replay
- Correlated Cortex event history.
- JSON/JSONL repository-backed persistence.
- Persistent player scorecards.
- Replay of prior decisions after process restart.

### Commissioner Suite
- Configurable league settings.
- Team/division management.
- Schedule generation and analytics.
- Rivalry and balance constraints.
- CSV/iCalendar exports.
- Playoff and draft workflows.
- League history and commissioner insights.

## Design Principles

1. Cortex owns reusable intelligence; GridironGPT owns football product behavior.
2. Evidence and provenance come before conclusions.
3. Presentation must not become a second scoring engine.
4. Missing evidence is not negative evidence.
5. Draft-state context must remain separate from production player ranking.
6. A player's football ranking should not change simply because a fantasy roster already filled that position.
7. Roster-aware advice may influence presentation or future recommendation layers without silently rewriting the production board.
8. Important decisions should be explainable and replayable.
9. Infrastructure remains replaceable behind contracts.
10. The full regression suite defines the protected development boundary.

## Quality Baseline

Current verified full-suite checkpoint:

```text
869 passed
```

This checkpoint includes the production projection-weight path, unified ranking consumers, tested live draft-pool filtering, ownership-aware `DraftBoardState`, roster-needs evaluation, and advisory Draft Assistant integration.

## Current Development Direction

The next Draft Assistant milestone is a separate **Best Fit Right Now** advisory layer. It may consider roster need, production rank, tier, Draft Value, and positional scarcity, but it should remain downstream of the authoritative production ranking score.
