# GridironGPT DFS — Capstone Project Overview

## Purpose

GridironGPT DFS is the Fall 2026 AI Capstone extension of the existing GridironGPT platform. The DFS subsystem adds machine-learning-based NFL player projection, DFS salary/value analysis, human-in-the-loop controls, and constrained lineup optimization for the common NFL contest structures on DraftKings and FanDuel.

The existing season-long GridironGPT product remains operational for draft support, waivers, weekly lineup decisions, roster management, and related fantasy workflows. DFS development is additive and must not disrupt those workflows.

## Capstone Boundary

### Existing GridironGPT foundation

- Existing GridironGPT application and UI
- Existing NFL data integrations and provider adapters
- Existing production rankings and projections
- Draft Assistant and live draft state
- Season-long waiver and weekly-lineup workflows
- Existing Cortex-backed reasoning and explanation infrastructure

### New DFS Capstone work

- DFS-specific data pipeline and normalization
- Historical player-week ML training dataset
- DFS feature engineering
- ML player-performance projection model(s)
- DraftKings and FanDuel salary/slate adapters
- Platform-specific scoring and roster-rule configuration
- DFS player value analysis
- Human review controls (lock, exclude, preference/strategy inputs)
- Constrained lineup optimizer
- Candidate lineup recommendation and human approval workflow
- Historical backtesting and live 2026 validation

## Primary Research Question

Can machine-learning models trained on historical NFL performance, usage, matchup, and contextual data improve player-level DFS projections and lineup selection compared with simple baseline methods?

## Primary Prediction Target

The primary ML target is actual fantasy-point production for a player in a given game/week. Training features must use only information that would have been available before kickoff for that observation.

## Human-in-the-Loop Principle

GridironGPT DFS is a decision-support system, not an autonomous contest-entry system.

The human remains in the loop at two points:

1. **Pre-optimization review** — review projections and uncertainty, lock or exclude players, account for late information, and choose preferences or strategy.
2. **Post-optimization decision** — accept, modify, or reject candidate lineups.

No automated contest entry is part of the Capstone scope.

## MVP

The minimum successful Capstone will:

1. Load a supported NFL DFS slate with real salaries.
2. Join slate players to GridironGPT/NFL data.
3. Generate player fantasy-point projections from an evaluated ML model.
4. Calculate player value relative to salary.
5. Accept human lock/exclude constraints.
6. Generate at least one legal optimized lineup under platform rules.
7. Present the lineup for human review rather than automatic submission.
8. Backtest the approach and report quantitative results.

## Stretch Goals

- Floor/ceiling or uncertainty estimates
- Multiple lineup generation
- Exposure constraints
- Tournament/cash strategy profiles
- Player/game correlation and stacking logic
- Ownership/leverage modeling
- Additional DFS contest formats
