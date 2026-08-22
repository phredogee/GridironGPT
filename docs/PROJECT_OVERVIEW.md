# GridironGPT Project Overview

GridironGPT is a fantasy-football intelligence platform powered by the reusable Gridiron Cortex decision engine. The application ingests NFL news and structured football state, resolves players to stable identities, converts evidence into Cortex events, updates persistent score state, produces recommendations and explanations, and exposes operational/intelligence views through Streamlit.

## Current State

- Stable v1.0 runtime architecture is tagged and released.
- v1.1 development is focused on continuous ingestion, structured football context, observability, performance, history accumulation, and the foundation for fantasy rankings.
- Automated news ingestion currently uses ESPN NFL and RotoWire NFL RSS providers.
- Structured football state persists 2026 roster/player state and schedule/game state independently from news evidence.
- Player availability is normalized into categories including available, reserve, exempt, retired, and released.
- Schedule context supports next-game lookup, opponent/location context, and bye-week detection.
- Stable GSIS player IDs are preserved through enrichment and Cortex entity resolution.
- FootballContextService is wired into the production CortexFacade and supplies factual roster/schedule context to explanations.
- Cortex persists event history, scorecards, recommendations, and replayable decision trails.
- Ingestion records provider health, normalized events, Cortex-accepted events, duplicate events, and processor failures.
- Current regression baseline: 744 passing tests as of 2026-08-12.

## Runtime Flow

News path:

NFL providers -> ingestion adapters -> player resolution -> normalized RawEvents -> Gridiron Cortex -> deduplication -> signal/impact/scoring/recommendation -> persistent history and scorecards.

Football-state path:

Structured NFL data -> canonical player/game state -> JSONL repositories -> ScheduleStateService + FootballContextService -> Cortex EngineContext -> factual explanation context.

## Ranking Status

RankingService can sort current Cortex scorecards overall or by position. These lists are infrastructure only and must not yet be treated as authoritative fantasy-football rankings. A dedicated Fantasy Ranking Score will combine baseline fantasy value with structured football state and Cortex intelligence rather than ranking raw Cortex overall scores alone.

## Operational Goal

Allow GridironGPT to continuously accumulate trustworthy historical evidence and structured NFL state without duplicate inflation, while keeping provider failures observable and building toward explainable, context-aware fantasy rankings.