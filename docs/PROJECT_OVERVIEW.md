# GridironGPT Project Overview

GridironGPT is a fantasy-football intelligence platform powered by the reusable Gridiron Cortex decision engine. The application ingests NFL news and structured football state, resolves players to stable identities, converts evidence into Cortex events, updates persistent score state, produces recommendations and explanations, and exposes operational/intelligence views through Streamlit.

## Current State

- Stable v1.0 runtime architecture is tagged and released.
- v1.1 development is focused on continuous ingestion, structured football context, observability, richer news interpretation, history accumulation, and the foundation for fantasy rankings.
- Automated news ingestion currently uses ESPN NFL and RotoWire NFL RSS providers.
- Daily production ingestion is scheduled through GitHub Actions and persists run history to Supabase.
- Structured football state persists 2026 roster/player state and schedule/game state independently from news evidence.
- Player availability is normalized into categories including available, reserve, exempt, retired, and released.
- Schedule context supports next-game lookup, opponent/location context, and bye-week detection.
- Stable GSIS player IDs are preserved through enrichment and Cortex entity resolution.
- FootballContextService is wired into the production CortexFacade and supplies factual roster/schedule context to explanations.
- Cortex can now detect multiple football developments inside one RawEvent while preserving a single Signal and a single direct scoring contribution.
- Compound classifications are stored as structured evidence and may influence relationship-path relevance without multiplying the source event's direct impact.
- Explanations surface compound football developments alongside normal evidence and propagation reasoning.
- Cortex persists event history, scorecards, recommendations, and replayable decision trails.
- Ingestion records provider health, normalized events, Cortex-accepted events, duplicate events, and processor failures.
- Current regression baseline: 909 passing tests as of 2026-08-22.

## Runtime Flow

News path:

NFL providers -> ingestion adapters -> player resolution -> normalized RawEvents -> multi-signal classification -> one Cortex Signal -> context-aware relationship propagation -> scoring/recommendation -> persistent history and scorecards.

Football-state path:

Structured NFL data -> canonical player/game state -> JSONL repositories -> ScheduleStateService + FootballContextService -> Cortex EngineContext -> factual explanation context.

## Multi-Signal Intelligence

A single report can contain several fantasy-relevant developments, such as a player returning to practice, receiving first-team reps, and drawing coach praise. EventClassifier preserves all detected classifications through `classify_all()` while the legacy `classify()` contract still returns the highest-ranked primary classification.

SignalProcessor stores the primary classification plus the full classification collection on one Signal. RelationshipContextPolicy can use those classifications to keep relevant graph paths eligible, especially opportunity and depth-chart relationships, without creating additional direct player impacts. Regression guards verify that one classification and three classifications produce the same direct source impact when the underlying Signal magnitude is unchanged.

## Ranking Status

RankingService can sort current Cortex scorecards overall or by position. These lists are infrastructure only and must not yet be treated as authoritative fantasy-football rankings. A dedicated Fantasy Ranking Score will combine baseline fantasy value with structured football state and Cortex intelligence rather than ranking raw Cortex overall scores alone.

## Operational Goal

Allow GridironGPT to continuously accumulate trustworthy historical evidence and structured NFL state without duplicate or multi-signal score inflation, while keeping provider failures observable and building toward explainable, context-aware fantasy rankings.