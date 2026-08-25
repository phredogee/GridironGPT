# Architecture

## System Boundary

GridironGPT owns provider integration, ingestion scheduling, football-specific structured state, fantasy ranking/draft policy, application composition, and user-facing views. Gridiron Cortex owns intelligence processing, deduplication, scoring, recommendations, explanations, persistence, evidence trails, and replay.

Football-specific facts and draft policy remain outside the reusable Cortex core until application composition supplies them through explicit services.

## News Ingestion Pipeline

1. Scheduled runner invokes configured providers.
2. Provider adapters retrieve source records.
3. Player resolution maps article text to NFL entities.
4. Records are normalized into RawEvents.
5. Ingestion forwards each event to the configured Cortex processor.
6. Cortex fingerprints the event and rejects previously processed evidence.
7. New evidence moves through entity resolution, multi-signal classification, Signal construction, relationship propagation, scoring, recommendation, prediction, and explanation stages.
8. Cortex state and event-bus history are persisted for restart recovery and replay.
9. Ingestion-run diagnostics are persisted independently for operational observability.

### Multi-Signal Classification Boundary

`EventClassifier.classify(event)` preserves the legacy single-best classification contract while `classify_all(event)` returns all distinct structured developments detected in one RawEvent. SignalProcessor still creates exactly one Signal per RawEvent. Secondary classifications are evidence/context, not independent direct score contributions.

### Taxonomy Integrity Boundary

Event taxonomy rules are runtime dictionaries consumed by EventClassifier. Every rule must define `category`, `subtype`, `polarity`, `impact`, `confidence`, and `phrases`, and must contain at least one phrase. Regression tests enforce this schema after a live RotoWire event exposed a missing `impact` field in the `transaction.released` rule. This prevents malformed taxonomy entries from reaching production ingestion as runtime `KeyError` failures.

### Context-Aware Relationship Propagation

RelationshipContextPolicy derives relationship relevance from structured Signal classifications. RelationshipEngine applies that context before PropagationPlanner uses relationship strength, confidence, hop decay, and semantic multipliers. Classification count does not modify source impact magnitude.

```text
RawEvent
  -> classify_all()
  -> one Signal
       |- primary classification
       |- compound classification evidence
       v
RelationshipContextPolicy
  -> eligible graph paths
  -> existing propagation math
  -> one direct impact + contextual propagated impacts
```

## Daily Production Refresh

`scripts/run_daily_ingestion.py` is the scheduler-facing production entry point. A healthy run requires zero provider failures and zero Cortex processor failures; otherwise the command exits non-zero so schedulers can surface the failure.

The GitHub Actions workflow runs daily and supports manual dispatch. Production explicitly selects Supabase ingestion-run persistence and requires the configured Supabase credentials.

A post-hotfix manual production run on 2026-08-25 processed 41 records from ESPN NFL and RotoWire NFL, accepted 10 new Cortex events, ignored 31 duplicates, recorded zero processor failures, and finished healthy.

## Structured Football State

GridironGPT maintains factual player/roster and schedule/game state separately from scored Cortex news evidence. FootballContextService bridges this state into CortexEngine for explanation context without silently redefining Cortex scores.

## Fantasy Draft Decision Architecture

Draft decisions are composed outside Cortex scoring:

```text
Current undrafted candidate pool
          |
          v
Production ranking_score --------------------+
          |                                   |
          v                                   |
FantasyPositionScarcityService                |
  |- remaining same-position alternatives     |
  |- next-option ranking score                 |
  |- score drop                                |
  `- tier-cliff detection                      |
          |                                   |
          v                                   |
scarcity level: low / medium / high            |
          |                                   |
          v                                   |
FantasyBestFitService <------------------------+
  |- production score remains read-only
  |- roster/market decision inputs
  `- bounded scarcity bonus: 0 / 1 / 2
          |
          v
BestFitView
  |- deterministic reason
  |- scarcity level/bonus
  `- low-scarcity noise suppressed
          |
          v
Streamlit Draft Assistant
```

### Scarcity Contract

Position scarcity is an advisory opportunity-cost signal, not a replacement ranking model. `FantasyPositionScarcityService` evaluates a candidate against the current available pool and excludes the candidate by stable `player_id`, including reconstructed objects representing the same player.

Best Fit uses bounded scarcity bonuses: low `+0`, medium `+1`, high `+2`. This permits a scarce position to break a close ranking gap while preventing scarcity from overcoming a large production-value difference. The service never mutates `ranking_score`.

The view layer computes scarcity from the current undrafted pool on each recommendation build. Position runs therefore change scarcity automatically as the pool thins. Medium/high scarcity can appear in deterministic explanation text; low scarcity remains quiet.

## Failure Model

Provider failures are isolated so healthy providers can continue. Downstream processor failures are fail-open from the provider-ingestion perspective but are counted as processor failures. The production daily command converts either provider or processor failures into a non-zero exit status.

Football context and draft advisory context are optional enrichment. Missing optional context must not prevent the underlying evidence pipeline from operating.

## Deduplication Contract

Cortex remains the authority for whether normalized evidence is new. Ingestion reports accepted events separately from duplicates ignored. Multi-signal classification preserves one source RawEvent as one deduplicated event and one Signal.

## Ranking Boundary

Production fantasy ranking value and Cortex intelligence remain conceptually distinct. Draft advisory services may use ranking value as an input, but must not mutate it. New decision policies should be explicit, bounded, deterministic where practical, and covered by ordering/regression fixtures.

## Performance and Persistence

RSS retrieval uses explicit timeouts. Player alias resolution caches aliases and performs a cheap literal pre-check before regex boundary matching. Cortex data-directory persistence supports event history, score state, and replay. Operational ingestion history is persisted independently, and structured football state remains under `data/football_state/`.