# Phase F — Fantasy Decision Engine

## Purpose

Phase F converts calibrated Cortex intelligence into explicit, explainable fantasy-football actions.

```text
Calibrated Cortex evidence
    + football context
    + league settings
    + roster context
        ↓
FantasyDecisionEngine
        ↓
Draft / Start-Sit / Waiver / Trade / Roster decisions
```

## Architecture

The decision layer remains outside the private reasoning engine. Cortex provides intelligence; GridironGPT applies league and roster semantics.

### Core Models

- `LeagueContext`
- `PlayerDecisionInput`
- `FantasyDecision`
- `TradeSide`
- `DecisionType`
- `RecommendationAction`

### F1 — League and Roster Context ✅

League context includes scoring format, team count, roster size, starting slots, and FAAB budget. Roster composition is used to identify positional depth needs.

### F2 — Draft Intelligence ✅

Players are ranked from calibrated Cortex score, projected production, replacement value, matchup, usage trend, confidence, availability, and bye status.

Every ranking includes reasons and stable metadata rather than returning a bare number.

### F3 — Start/Sit Decisions ✅

Candidates are ranked for a configurable number of starting slots. Bye-week and unavailable players cannot be selected as starters. Decisions include alternatives and the contextual evidence behind the recommendation.

### F4 — Waivers and FAAB ✅

Free agents are ranked by player value plus roster need. Add/pass actions include explainable reasons and a bounded FAAB recommendation based on value and confidence.

### F5 — Trade Evaluation ✅

Trade sides are compared using aggregate Cortex, projection, and replacement value. The engine returns accept, reject, or hold for near-even deals, along with both side values and the net difference.

### F6 — Roster Construction and Risk ✅

Roster analysis identifies missing starter/depth requirements and surfaces players unavailable because of injury risk or bye week.

### F7 — Explainability and Audit History ✅

Every result is a typed `FantasyDecision` with:

- action
- decision score
- confidence
- summary
- evidence-based reasons
- alternatives where relevant
- structured metadata

`JsonlFantasyDecisionRepository` provides append-only decision history for later outcome tracking and calibration.

## Decision Boundaries

- Draft capital is not allowed to outweigh observed NFL evidence.
- Bye weeks affect lineup eligibility but do not degrade underlying player talent.
- Availability scales expected decision value.
- Matchup and trend context are modifiers, not sole decision drivers.
- Near-even trades return `HOLD` rather than forcing an artificial answer.
- FAAB bids are recommendations bounded by the league budget.

## Validation

Phase F introduces focused coverage for:

- decision scoring
- availability and bye behavior
- draft rankings
- start/sit selection
- waiver roster-need prioritization
- FAAB bounds
- trade acceptance/rejection/hold
- roster weakness analysis
- decision persistence and history

The full repository regression suite remains the phase-completion gate.
