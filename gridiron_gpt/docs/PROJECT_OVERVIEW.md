# GridironGPT Project Overview

## Vision

GridironGPT is a fantasy-football intelligence platform powered by **Gridiron Cortex**. It converts NFL news and structured football evidence into persistent, explainable player intelligence, recommendations, trends, and decision history.

GridironGPT is the flagship football application built on Cortex. Cortex owns reusable intelligence and reasoning; GridironGPT owns football-specific ingestion, workflows, presentation, and league-management features.

## v1.0 System

```text
ESPN / NBC Sports / ProFootballTalk / RotoWire / nflverse
                         ↓
                  Provider Adapters
                         ↓
                  IngestionService
                         ↓
             Normalize + Deduplicate
                         ↓
                     RawEvent
                         ↓
                  Gridiron Cortex
                         ↓
       Resolve → Classify → Propagate → Score
                         ↓
             Recommend → Explain
                         ↓
       Event Bus + Scorecard Persistence
                         ↓
 Dashboard / Advisor / Players / Explorer / Replay / Mission Control
```

The production ingestion boundary automatically forwards normalized `RawEvent` objects into Cortex. Individual providers remain responsible only for retrieving and translating source data. Downstream Cortex failures are fail-open so provider ingestion remains successful and is not retried simply because the intelligence processor is unavailable.

## Major Capabilities

### Live Football Intelligence
- Multi-source provider ingestion
- Structured nflverse statistical context
- Normalized `RawEvent` contract
- Duplicate-safe event processing
- Player/entity resolution
- Signal classification and impact scoring
- Relationship-aware propagation
- Confidence and recommendation generation
- Persistent player scorecards
- Momentum and trend history
- Evidence chains and explanations

### Persistent Decision Trail
- Cortex event bus records processing stages
- Correlation IDs connect a source event to its downstream decision trail
- Event history persists to JSONL
- Player scorecards persist independently of the UI
- Replay reconstructs prior Cortex decisions after an application restart
- Mission-control/activity surfaces consume the same event history

### Advisor
- Natural-language football questions
- Recommendation, score, and confidence cards
- Supporting evidence and headlines
- Signal-impact visualization
- Cortex timeline
- Health, opportunity, momentum, risk, and upside profile

### Dashboard and Player Intelligence
- Player and recommendation metrics
- BUY/WATCH/risk candidates
- Recommendation distribution
- Team momentum
- Position rankings
- Cortex-ranked player table
- Player trend and trajectory views

### Cortex Explorer and Inspector
- Player/entity exploration
- Knowledge-graph visualization
- Decision/event inspection
- Manual diagnostic event processing through the same Cortex facade used by runtime intelligence

### Commissioner Suite
- Configurable league settings
- Team/division management
- Schedule generation and quality analytics
- Rivalry and home/away constraints
- CSV/iCalendar exports
- Playoff and draft-room workflows
- League history and commissioner insights

## Runtime Composition

The Streamlit application keeps one `CortexFacade` in session state and shares it across Cortex-facing pages. Runtime ingestion can receive that same facade, ensuring ingestion, activity views, scorecards, and Replay operate against the same engine boundary and persistence model.

## Persistence

Cortex persistence is repository-oriented and currently uses local JSON/JSONL state for core engine artifacts, including event history and player scorecards. Ingestion-run observability is persisted separately. Provider/data infrastructure remains replaceable behind contracts so storage can evolve without coupling the reasoning pipeline to one backend.

## Quality Baseline

Current verified full-suite checkpoint:

```text
702 passed
```

This checkpoint includes automatic runtime ingestion into Cortex and an end-to-end persistence test that verifies a decision can be reconstructed by Replay after a simulated application restart.

## Design Principles

1. Cortex owns intelligence; GridironGPT owns football product behavior.
2. Providers retrieve data; the shared ingestion layer normalizes it.
3. Normalized events cross one explicit boundary into Cortex.
4. Evidence and provenance come before conclusions.
5. Duplicate events must not produce duplicate decisions.
6. Provider ingestion must remain resilient when downstream intelligence processing fails.
7. User-facing recommendations should explain why.
8. Decision history should survive process restarts and remain replayable.
9. Infrastructure remains replaceable behind contracts.
10. Tests define the regression boundary for every major development batch.

## v1.0 Status

The core intelligence architecture is feature-complete for the v1.0 stabilization phase. Current work is focused on documentation, stale-path cleanup, regression verification, Streamlit smoke testing, and merge/release preparation rather than adding another major engine subsystem.

The system is designed to answer:

> What happened, why does it matter, who else is affected, how confident is Cortex, what should a fantasy manager do next, and can Cortex show how it reached that decision?
