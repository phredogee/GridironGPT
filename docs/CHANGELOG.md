# Changelog

## v1.1 Development - 2026-08-22

### Added
- Production `scripts/run_daily_ingestion.py` command for scheduler-friendly NFL news ingestion through the existing Cortex runtime path.
- Ingestion freshness evaluator with fresh, stale, failed, and missing states and a 26-hour daily freshness window.
- Streamlit ingestion freshness metrics for last update time, update age, and stale/failed operational warnings.
- Dedicated `cortex_ingestion_runs` Supabase persistence contract for durable operational history without changing the legacy article-ingestion table.
- `SupabaseIngestionRunRepository` and explicit ingestion-run repository factory.
- Environment-controlled persistence via `GRIDIRON_INGESTION_RUN_PERSISTENCE=jsonl|supabase`; local development defaults to JSONL while production must explicitly select Supabase.
- GitHub Actions `Daily NFL Ingestion` workflow prepared for daily and manual execution with Supabase-backed persistence.

### Improved
- Streamlit Ingestion Operations now reads from the same configured ingestion-run repository as the production ingestion runtime.
- Production persistence configuration fails on unsupported modes rather than silently falling back to ephemeral local storage.
- Daily workflow validates required Supabase secrets before attempting ingestion and protects against overlapping scheduled runs.

### Validated
- Manual production ingestion successfully retrieved 28 records from ESPN NFL and RotoWire NFL, normalized all 28, and completed with zero provider or processor failures.
- Supabase-backed end-to-end run `bae87553-00f7-4a21-998d-02474f33fd91` persisted 28 normalized events, including 1 newly accepted Cortex event and 27 correctly ignored duplicates.
- Streamlit freshness/status UI was manually smoke-tested against the production ingestion flow.
- 894 tests passing after durable persistence, runtime repository selection, Streamlit reader wiring, and scheduler preparation.

## v1.1 Development - 2026-08-12

### Added
- Structured 2026 NFL game/schedule state with persistent JSONL storage.
- Structured 2026 player/roster state with stable GSIS identities.
- Player availability classification for available, reserve, exempt, retired, and released states.
- ScheduleStateService for team schedules, next-game context, opponent/location lookup, and bye-week detection.
- FootballContextService combining canonical player state and schedule state.
- Production CortexFacade wiring for football context.
- Factual football context in Cortex explanations without changing Cortex scoring behavior.
- Facade-level integration coverage proving player identity -> football state -> schedule state -> Cortex explanation.

### Fixed
- EntityResolver now preserves player GSIS ID and position instead of dropping identity metadata during canonical entity construction.
- JsonPlayerScorecardRepository `get_all_latest()` now uses the repository's correct file-path attribute, restoring RankingService reads.
- Live alias/suffix tests were hardened against upstream roster display-name changes.
- Facade football-context fixture now uses chronological synthetic kickoff dates.

### Validated
- Real production-path smoke test resolved C.J. Stroud to GSIS `00-0039163` and produced available status, Week 1 home game vs BUF, and Week 8 bye context.
- RankingService infrastructure can read latest scorecards and produce overall/position-sorted lists; these are not yet authoritative fantasy rankings.
- 744 tests passing after football-state/context integration and facade-level regression coverage.

## v1.1 Development - 2026-08-10

### Added
- Scheduled ingestion runner for recurring NFL data collection.
- ESPN NFL and RotoWire NFL runtime provider composition.
- Persisted ingestion-run diagnostics and provider health.
- Streamlit Ingestion Status observability.
- Cortex acceptance, duplicate, and processor-failure counters at run and provider level.
- Hourly WSL cron deployment for local continuous ingestion.

### Improved
- Added explicit HTTP timeout handling to RSS retrieval.
- Optimized player alias matching by caching ordered aliases and avoiding unnecessary regex evaluation.
- ESPN player resolution benchmark improved from approximately 20.559 seconds to 0.221 seconds, with total diagnostic processing reduced from approximately 20.777 seconds to 0.480 seconds.
- End-to-end scheduled ingestion subsequently completed in under one second with both providers healthy.

### Validated
- 709 tests passing after initial v1.1 ingestion and observability work.
- Live run processed 30 normalized events: 3 accepted as new Cortex evidence, 27 rejected as duplicates, and 0 processor failures.

## v1.0.0 - 2026-08-10

- Stabilized GridironGPT / Gridiron Cortex runtime architecture.
- Verified 702 passing tests before release.
- Completed Streamlit smoke validation, branch reconciliation, documentation refresh, persistent Cortex state, and replay support.
- Release commit: de14fd460d42f4f2a2dc04097224501f84b82caf.