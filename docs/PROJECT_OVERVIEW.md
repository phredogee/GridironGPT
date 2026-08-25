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
- Fantasy draft Best Fit recommendations now include deterministic position-scarcity reasoning based on the current undrafted candidate pool.
- Position scarcity measures same-position depth, next-option ranking-score drop, and tier cliffs.
- Scarcity is advisory: bounded bonuses may resolve close Best Fit decisions but never mutate the production `ranking_score`.
- Draft Assistant explanations surface meaningful medium/high scarcity while suppressing low-scarcity noise.
- Cortex persists event history, scorecards, recommendations, and replayable decision trails.
- Ingestion records provider health, normalized events, Cortex-accepted events, duplicate events, and processor failures.
- A production taxonomy integrity guard now verifies every event rule contains the required classification fields after a live RotoWire event exposed a missing `impact` field.
- Current regression baseline: **939 passing tests as of 2026-08-25**.

## Runtime Flow

News path:

NFL providers -> ingestion adapters -> player resolution -> normalized RawEvents -> multi-signal classification -> one Cortex Signal -> context-aware relationship propagation -> scoring/recommendation -> persistent history and scorecards.

Football-state path:

Structured NFL data -> canonical player/game state -> JSONL repositories -> ScheduleStateService + FootballContextService -> Cortex EngineContext -> factual explanation context.

Draft decision path:

Available draft board -> production `ranking_score` -> PositionScarcityService -> bounded Best Fit adjustment -> deterministic Best Fit view -> Draft Assistant.

## Position Scarcity

Position scarcity answers a draft-specific opportunity-cost question: what is likely lost by waiting at this position? For each candidate, the service evaluates remaining same-position alternatives, the score of the next option, the score drop, and whether waiting crosses a tier boundary.

Scarcity levels are intentionally bounded in Best Fit: low adds 0, medium adds 1, and high adds 2. This allows scarcity to break close decisions without allowing positional urgency to overwhelm a materially better player. The underlying production `ranking_score` remains unchanged and authoritative.

Because scarcity is calculated from the current candidate pool, it reacts naturally to position runs as players are drafted. The Draft Assistant exposes useful high/medium urgency in deterministic explanation text and keeps low scarcity quiet.

## Multi-Signal Intelligence

A single report can contain several fantasy-relevant developments, such as a player returning to practice, receiving first-team reps, and drawing coach praise. EventClassifier preserves all detected classifications through `classify_all()` while the legacy `classify()` contract still returns the highest-ranked primary classification.

SignalProcessor stores the primary classification plus the full classification collection on one Signal. RelationshipContextPolicy can use those classifications to keep relevant graph paths eligible without creating additional direct player impacts.

## Ranking Status

Fantasy draft decisions now use a production ranking score plus explicit advisory layers such as roster need, market/draft value, and position scarcity. Cortex intelligence remains interpretable and separate from the ranking contract. Position scarcity does not rewrite player value; it only expresses the opportunity cost of waiting.

## Operational Goal

Allow GridironGPT to continuously accumulate trustworthy historical evidence and structured NFL state without duplicate or multi-signal score inflation, while turning that evidence into explainable, deterministic draft-night decisions with explicit safety boundaries.