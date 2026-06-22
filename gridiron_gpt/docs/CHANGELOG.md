# Changelog

## 2026-06-22

### Added
- Added Momentum Engine for player trend acceleration analysis.
- Added momentum rankings for Top Risers and Top Fallers.
- Added first-snapshot tracking for players with limited historical data.
- Added momentum reporting to the daily pipeline.
- Added Momentum tab to the Streamlit dashboard.

### Changed
- Daily pipeline now generates:
  - RSS ingestion summary
  - Trend report
  - Momentum report
- Dashboard now exposes momentum analytics alongside existing trend analysis.

### Improved
- Expanded player intelligence layer beyond static recommendations.
- Created foundation for future momentum-based rankings and alerts.
- Improved visibility of player movement using historical score snapshots.

---

## 2026-06-21

### Added
- Added `story_dedup.py` for duplicate story detection.
- Added headline normalization for comparing similar news stories.
- Added stable `story_hash` generation for RSS article records.
- Added `story_hash` persistence to `raw_articles`.
- Added `signal_event_hash.py` for signal-level event identity.
- Added `signal_event_hash` wiring through the signal persistence flow.
- Added signal-level deduplication using the existing `unique_signal_event_hash` index.

### Changed
- RSS article records now include `story_hash`.
- Raw articles continue to upsert by `content_hash`, while also storing `story_hash` for future event-level analysis.
- Signals now upsert by `signal_event_hash` to prevent duplicate player-impact events from inflating scores.

### Fixed / Improved
- Prevented repeated ingestion runs from creating duplicate fantasy signals for the same story, player, impact, and date.
- Improved data-quality foundation for future multi-source ingestion.

---

## 2026-06-12

### Added

Article relevance classification
Player score snapshots
Snapshot service
Daily snapshot deduplication

---

## 2026-06-11

### Added

Supabase integration
raw_articles repository
signals repository
propagated_signals repository
ingestion_runs repository
signal persistence service
news persistence service
ingestion tracking

Improved:

Player matcher accuracy
Alias handling
Catalog caching
RSS ingestion pipeline

RSS Improvements:

Multi-player matching
Summary-aware extraction
Confidence tracking
Expanded signal generation

Infrastructure:

Cloud-backed persistence
Event-driven architecture
Historical audit capability

Current Pipeline:

RSS Feed
 ↓
raw_articles
 ↓
signals
 ↓
propagated_signals
 ↓
recommendations

Status:
V4 Foundation Complete

---

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

### V4 Foundation Milestone Reached

- Supabase migration started
- Event persistence implemented
- Historical score tracking implemented
- RSS ingestion operational
- Article classification operational
