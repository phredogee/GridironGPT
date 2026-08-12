# Changelog

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