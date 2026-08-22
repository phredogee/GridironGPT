# Architecture

## System Boundary

GridironGPT owns provider integration, ingestion scheduling, football-specific structured state, application composition, and user-facing views. Gridiron Cortex owns intelligence processing, deduplication, scoring, recommendations, explanations, persistence, evidence trails, and replay.

Football-specific facts remain outside the reusable Cortex core until application composition supplies them through explicit context services.

## News Ingestion Pipeline

1. Scheduled runner invokes configured providers.
2. Provider adapters retrieve source records.
3. Player resolution maps article text to NFL entities.
4. Records are normalized into RawEvents.
5. Ingestion forwards each event to the configured Cortex processor.
6. Cortex fingerprints the event and rejects previously processed evidence.
7. New evidence moves through entity resolution, signal processing, relationship propagation, scoring, recommendation, prediction, and explanation stages.
8. Cortex state and event-bus history are persisted for restart recovery and replay.
9. Ingestion-run diagnostics are persisted independently for operational observability.

### Daily Production Refresh

`scripts/run_daily_ingestion.py` is the scheduler-facing production entry point. It composes the existing unified ingestion path rather than introducing a parallel pipeline. A healthy run requires zero provider failures and zero Cortex processor failures; otherwise the command exits non-zero so schedulers can surface the failure.

The prepared GitHub Actions workflow runs the command daily and also supports manual dispatch. Production execution explicitly sets `GRIDIRON_INGESTION_RUN_PERSISTENCE=supabase` and requires `SUPABASE_URL` plus `SUPABASE_SERVICE_ROLE_KEY`.

## Ingestion Freshness and Operational Persistence

Ingestion-run persistence is selected at the application-composition boundary:

```text
Local development
  ingestion -> JsonlIngestionRunRepository <- Streamlit

Production / scheduled execution
  ingestion -> SupabaseIngestionRunRepository <- Streamlit
                         |
                         v
                cortex_ingestion_runs
```

JSONL remains the default for local development. Supabase must be explicitly selected with `GRIDIRON_INGESTION_RUN_PERSISTENCE=supabase`; unknown persistence modes fail rather than silently falling back to local storage.

The dedicated `cortex_ingestion_runs` table stores operational run summaries separately from the legacy article-ingestion contract. It includes run timestamps, provider totals, records received, normalized events, Cortex accepts, duplicates, processor failures, diagnostics, and overall success.

The freshness evaluator derives presentation-safe state from the latest persisted run. A successful run is considered fresh for 26 hours, allowing modest scheduling/runtime drift around a daily cadence. A recent failed run is still reported as failed rather than fresh. Streamlit uses the same configured repository and surfaces freshness, last-updated time, update age, provider diagnostics, Cortex outcomes, and recent history.

## Structured Football State

GridironGPT maintains a factual football-state layer separate from Cortex news scoring.

### Player State

CanonicalPlayerState records stable player identity, team, position, raw roster status, status detail, roster week, and game type. JsonlPlayerStateRepository persists latest player state and history. Availability classification converts source-specific roster codes into application-level states such as available, reserve, exempt, retired, and released.

### Game State

CanonicalGameState records season, week, season type, home/away teams, kickoff time, and game status. JsonlGameStateRepository persists schedule state. ScheduleStateService provides team schedules, next-game lookup, opponent/location context, and bye-week detection for a selected season.

### Football Context Bridge

CortexFacade composes the football-specific services and injects FootballContextService into CortexEngine:

```text
JsonlPlayerStateRepository ----\
                                -> FootballContextService -> CortexEngine
JsonlGameStateRepository -> ScheduleStateService --------/
```

Player enrichment and EntityResolver preserve the stable GSIS `player_id`. During event processing, CortexEngine uses that identity to request factual football context and stores it on EngineContext. ExplanationEngine may render this context, but the current v1.1 implementation does not alter Cortex scores based on schedule or availability.

Example factual context:

```text
Football context: C.J. Stroud is available.
Next game: Week 1 vs BUF home.
Bye week: 8.
```

## Failure Model

Provider retrieval uses bounded attempts and timeout handling. Provider failures are isolated so healthy providers can continue. Downstream processor failures are fail-open from the ingestion perspective and are recorded as processor failures rather than causing provider refetches.

The daily production command converts provider or processor failures into a non-zero process exit so external schedulers can detect an unhealthy refresh. Durable operational persistence prevents scheduler-local state from disappearing when an ephemeral runner exits.

Football context is optional enrichment. Missing player state, schedule state, or stable identity must not prevent Cortex from processing the underlying news event.

## Deduplication Contract

Ingestion may normalize the same source evidence on successive scheduled runs. Cortex remains the authority for determining whether evidence is new. Ingestion captures the Cortex result and reports accepted events separately from duplicates ignored.

A verified Supabase-backed production run on 2026-08-22 processed 28 normalized records: 1 was accepted as new Cortex evidence, 27 were correctly ignored as duplicates, and no provider or processor failures occurred.

## Ranking Boundary

The existing RankingService sorts latest player scorecards by Cortex `overall_score`, globally or by position. This validates ranking infrastructure but does not constitute a complete fantasy ranking model.

The planned Fantasy Ranking Score will be a separate aggregation layer combining baseline fantasy value with role, availability, Cortex momentum/evidence, and later schedule/matchup context. Cortex intelligence scores should remain interpretable rather than being redefined as draft rankings.

## Performance

RSS retrieval uses an explicit HTTP timeout before feed parsing. Player alias resolution caches the ordered alias catalog and performs a cheap literal pre-check before regex boundary matching. On the 2026-08-10 ESPN feed, player-resolution time improved from approximately 20.6 seconds to 0.22 seconds while preserving the test baseline.

## Persistence

Cortex data-directory persistence supports event history, score state, and replay across application restarts. Ingestion operational history is persisted independently: JSONL for local development and the dedicated Supabase `cortex_ingestion_runs` table for production/scheduled execution. Both the ingestion runtime and Streamlit status view use the same repository-selection boundary.

Structured football state is persisted separately under `data/football_state/`, currently using `player_states.jsonl` and `game_states.jsonl`. This separation prevents factual roster/schedule state from becoming indistinguishable from scored news evidence.