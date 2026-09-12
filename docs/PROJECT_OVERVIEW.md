# GridironGPT Project Overview

GridironGPT is a fantasy-football intelligence platform powered by the reusable Gridiron Cortex decision engine. The application ingests NFL news and structured football state, resolves players to stable identities, converts evidence into Cortex events, updates persistent score state, produces fantasy rankings and draft recommendations, and exposes operational/intelligence views through Streamlit.

## Current State

- Stable v1.0 runtime architecture is tagged and released.
- v1.1 development includes continuous ingestion, structured football context, observability, richer news interpretation, fantasy ranking infrastructure, and draft decision support.
- Automated news ingestion uses ESPN NFL and RotoWire NFL RSS providers.
- Daily production ingestion runs through GitHub Actions and persists run history to Supabase.
- Structured football state persists 2026 roster/player state and schedule/game state independently from news evidence.
- Stable GSIS player IDs are preserved through enrichment and Cortex entity resolution.
- FootballContextService supplies factual roster/schedule context to Cortex explanations.
- Cortex supports compound football developments on one Signal without multiplying direct source impact.
- Context-aware relationship propagation uses structured classifications to select relevant graph paths.
- Fantasy draft Best Fit recommendations include deterministic position-scarcity reasoning based on the current undrafted candidate pool.
- Position scarcity is advisory and never mutates the production ranking score.
- Cortex persists event history, scorecards, recommendations, and replayable decision trails.

## Runtime Flow

News path:

NFL providers -> ingestion adapters -> player resolution -> normalized RawEvents -> multi-signal classification -> one Cortex Signal -> context-aware relationship propagation -> scoring/recommendation -> persistent history and scorecards.

Football-state path:

Structured NFL data -> canonical player/game state -> JSONL repositories -> ScheduleStateService + FootballContextService -> Cortex EngineContext -> factual explanation context.

Draft decision path:

Available draft board -> production ranking_score -> PositionScarcityService -> bounded Best Fit adjustment -> deterministic Best Fit view -> Draft Assistant.

## Capstone Project: GridironGPT DFS Intelligence

The Fall 2026 Capstone extends the existing GridironGPT platform with a new, isolated Daily Fantasy Sports decision-support module for DraftKings and FanDuel. Existing GridironGPT infrastructure is prior work and remains the season-long fantasy foundation. Capstone credit applies to the new DFS-specific pipeline, machine-learning projection system, platform integration, value analysis, optimization, human-in-the-loop controls, backtesting, live evaluation, and integration work.

### Capstone Scope

The new DFS work will include:

- Historical NFL player-week training data.
- Pregame feature engineering using only information available before kickoff.
- A baseline projection method and multiple regression models.
- Prediction of player fantasy-point production.
- DraftKings and FanDuel salary/slate ingestion through permitted sources or import workflows.
- Platform-specific scoring and roster-rule adapters.
- DFS player-value analysis combining projections with salary and platform context.
- Human review controls for locking, excluding, and overriding players before optimization.
- A constrained lineup optimizer.
- Human acceptance, modification, or rejection of candidate lineups.
- Historical backtesting and live 2026 weekly evaluation.
- Integration that does not disrupt existing season-long GridironGPT functionality.

### Prediction Target

The primary machine-learning target is actual fantasy-point production for an NFL player in a given player-week/game. Each training row represents one player appearance. Features must be derived only from information available before that game's kickoff to prevent data leakage.

The initial baseline will use recent rolling fantasy-point performance. Candidate models will include linear regression, random forest regression, and gradient-boosted regression. Model selection will use chronological validation rather than random future-to-past mixing.

### Success Criteria

Prediction quality will be evaluated with MAE, RMSE, predicted-versus-actual correlation, positional error analysis, and comparison with the rolling-performance baseline. Success requires the selected ML approach to demonstrate measurable improvement over the baseline on unseen chronological test data.

Optimizer success requires 100% compliance with implemented salary-cap, roster, position, FLEX, platform, and human lock/exclude constraints. Human-in-the-loop success requires the user to be able to review projections, constrain optimization, and accept, modify, or reject candidate lineups. DFS integration must not break existing season-long GridironGPT behavior.

### Human-in-the-Loop Principle

GridironGPT DFS Intelligence is a decision-support system, not an autonomous wagering system. Human review occurs before optimization and human authority is retained after candidate lineups are generated. The system will not automatically enter contests or present predictions as guaranteed outcomes.

## Operational Goal

Allow GridironGPT to continuously accumulate trustworthy historical evidence and structured NFL state while turning that information into explainable fantasy-football decisions. The DFS Capstone adds a measurable ML-and-optimization workflow while preserving clear boundaries between prediction, optimization, and human judgment.