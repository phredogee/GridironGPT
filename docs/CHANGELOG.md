# Changelog

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
- 709 tests passing after v1.1 ingestion and observability work.
- Live run processed 30 normalized events: 3 accepted as new Cortex evidence, 27 rejected as duplicates, and 0 processor failures.

## v1.0.0 - 2026-08-10

- Stabilized GridironGPT / Gridiron Cortex runtime architecture.
- Verified 702 passing tests before release.
- Completed Streamlit smoke validation, branch reconciliation, documentation refresh, persistent Cortex state, and replay support.
- Release commit: de14fd460d42f4f2a2dc04097224501f84b82caf.