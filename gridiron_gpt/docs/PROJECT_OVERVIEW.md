# GridironGPT Project Overview

## Vision

GridironGPT is a fantasy-football intelligence platform powered by **Gridiron Cortex**. It converts NFL news, structured football evidence, market context, historical production, projections, and live draft state into explainable player intelligence and fantasy decision support.

GridironGPT is the football product layer. Cortex owns reusable intelligence and reasoning; GridironGPT owns football-specific ingestion, fantasy workflows, draft state, presentation, and commissioner features.

## Fantasy Ranking and Draft Pipeline

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
             ┌────────┼────────┐
             ↓        ↓        ↓
      Best Available  Best Value  Best Fit Right Now
```

Projected production is active in the production ranking model at its configured weight. The live advisory layers consume that authoritative board rather than rewriting it.

## Live Draft Assistant

`DraftBoardState` tracks ordered picks plus **My Team** vs. **Other Team** ownership. `FantasyDraftPoolService` removes drafted players while preserving board order. `FantasyRosterNeedsService` and `FantasyRosterAdviceService` evaluate the user's roster separately from league availability.

**Best Fit Right Now** is now implemented as a separate advisory service and presentation view. It blends production ranking quality with modest roster-need and Draft Value context, then provides a concise explanation. The service reads `ranking_score` but never mutates it.

Current live behavior includes:
- Mark drafted players or assign picks to **My Team**.
- Undo, restore, and reset draft state.
- Remove drafted players from Best Available, Best Value, and Best Fit candidate pools.
- Preserve the frozen production ranking order.
- Track starter-oriented QB/RB/WR/TE roster needs.
- Display roster-need badges.
- Display **Best Fit Right Now** recommendations that respond to My Team composition.

## Major Capabilities

### Football Intelligence
- Multi-source ingestion and normalization.
- Entity resolution, signal interpretation, relationship propagation, and multidimensional scorecards.
- Persistent recommendations, confidence, evidence, explanations, trends, and decision history.

### Fantasy Decision Support
- Integrated production rankings with ADP, role, Cortex, availability, and projections.
- Position ranks, tiers, and Draft Value.
- Best Available and Best Value.
- Live draft-state and My Team ownership.
- Roster-needs advisory context.
- Best Fit Right Now advisory recommendations.
- Excel and PDF ranking exports.

### Persistence and Replay
- Correlated Cortex event history.
- JSON/JSONL repository-backed persistence.
- Persistent player scorecards.
- Replay of prior decisions after process restart.

### Commissioner Suite
- Configurable league settings, teams/divisions, schedules, rivalry/balance constraints, exports, playoffs, draft workflows, league history, and commissioner insights.

## Design Principles

1. Cortex owns reusable intelligence; GridironGPT owns football product behavior.
2. Evidence and provenance come before conclusions.
3. Presentation must not become a second production scoring engine.
4. Missing evidence is not negative evidence.
5. Draft-state context remains separate from production player ranking.
6. Contextual advice may reorder an advisory view without silently rewriting the authoritative board.
7. Important decisions should be explainable and replayable.
8. Infrastructure remains replaceable behind contracts.
9. The full regression suite defines the protected development boundary.

## Quality Baseline

Current verified full-suite checkpoint:

```text
878 passed
```

This checkpoint includes Best Fit service tests, Best Fit view-model tests, live Draft Assistant integration, roster-aware behavior, and the previously protected production ranking/draft functionality.

## Current Development Direction

The next Draft Assistant milestone is **positional scarcity / tier-drop awareness**: quantify how much worse the next realistic option at a position becomes if the user waits. Scarcity remains advisory-only and will be tested independently before it influences Best Fit explanations or fit scoring.
