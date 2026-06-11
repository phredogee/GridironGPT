# Changelog

## 2026-06-09

### Added

#### Entity Relationship Engine

* Added JSON-driven relationship framework.
* Added support for propagating impacts between related entities.
* Added relationship validation and loading system.
* Added configurable relationship definitions via `data/relationships.json`.

#### Signal Impact API

* Added `generate_signal_impacts()`.
* Added `format_signal_impact_report()`.
* Added support for calculating system-wide impacts from a single signal.

#### Recommendation Integration

* Added propagated impact scoring to recommendation engine.
* Recommendations now support adjusted scores derived from relationship propagation.
* Recommendation rankings can incorporate downstream effects from related entities.

### Refactored

* Moved intelligence components into:

  * `gridiron_gpt/intelligence/`
* Removed duplicate intelligence module locations.
* Standardized import paths throughout intelligence engine.

### Infrastructure

* Cleaned project dependencies.
* Split runtime and development dependencies.
* Added testing support for relationship engine and signal impact API.

### Status

Phase 1 of the Impact Propagation Engine completed.

---

## 2026-06-11

### Added
- Added Supabase cloud storage foundation.
- Added `ingestion_runs` table for tracking ingestion job status.
- Added `raw_articles` table for storing ingested articles.
- Added `signals` table for direct fantasy-relevant player signals.
- Added `propagated_signals` table for relationship-generated downstream impacts.
- Added Supabase storage client.
- Added article repository with `content_hash` deduplication.
- Added signal repository.
- Added propagated signal repository.
- Added signal persistence service that saves direct and propagated signals together.

### Changed
- Began moving GridironGPT from JSON-only storage toward Supabase/Postgres-backed persistence.
- V4 architecture now treats signals as persistent, auditable data instead of temporary in-memory calculations.

### Status
- V4A Signal Persistence Layer completed.
