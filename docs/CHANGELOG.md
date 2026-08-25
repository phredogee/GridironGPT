# Changelog

## v1.1 Development - 2026-08-25 - Position Scarcity and Ingestion Hardening

### Added
- `FantasyPositionScarcityService` for draft-time same-position depth and opportunity-cost analysis.
- Tier-cliff detection and next-option ranking-score drop measurement.
- Low/medium/high scarcity classification.
- Bounded scarcity integration into `FantasyBestFitService`: low `+0`, medium `+1`, high `+2`.
- Best Fit view support for scarcity level/bonus and deterministic scarcity explanations.
- Realistic draft scenario coverage for RB cliffs, TE scarcity, deep same-tier pools, position runs, and the cost of waiting.
- Event-taxonomy integrity regression tests requiring every rule to define `category`, `subtype`, `polarity`, `impact`, `confidence`, and `phrases`.

### Fixed
- Added the missing `impact` value to `transaction.released` after a live RotoWire ingestion event caused `KeyError: 'impact'` in EventClassifier.
- Daily ingestion now completes normally for that production path; a verified post-fix run processed 41 records with zero processor failures.

### Decision Safety
- Position scarcity is advisory and never mutates production `ranking_score`.
- Scarcity can break close Best Fit gaps but cannot overcome large production-ranking gaps.
- Low scarcity is intentionally suppressed from Draft Assistant explanation text to reduce draft-night noise.
- Scarcity is recomputed from the current undrafted pool, so position runs update urgency naturally.

### Validated
- 25 focused scarcity/Best Fit tests passed before view integration.
- 6 Best Fit view-boundary tests passed after integration.
- Full regression suite: **939 passing tests** on `main`.
- Position scarcity merged through PR #10.

## v1.1 Development - 2026-08-23 - Camp Signal Quality

### Added
- Production-derived regression fixtures from live ESPN NFL and RotoWire NFL ingestion.
- `injury.season_ending` coverage for season-ending IR and out-for-year language.
- `injury.returned_to_team_drills` coverage for players cleared to resume team or 11-on-11 work.
- `participation.walkthrough` coverage for low-strength walkthrough participation.
- `depth_chart.qb_competition` coverage for explicit quarterback competition language.
- Generic absence disambiguation so `won't play` does not automatically imply injury without injury context.

### Validated
- 20 focused EventClassifier tests passing.
- Full regression suite: 915 passing tests.

## v1.1 Development - 2026-08-22 - Multi-Signal Intelligence

### Added
- `EventClassifier.classify_all()` for extracting multiple structured football developments from one RawEvent while preserving legacy `classify()` behavior.
- Complete classification collections on one Signal.
- `RelationshipContextPolicy` for classification-guided relationship relevance.
- Regression guards preventing secondary classifications from multiplying direct score contribution.

### Validated
- One RawEvent still produces one Cortex Signal and one direct source impact.
- Full regression suite: 909 passing tests.
- Feature merged through PR #6.

## v1.1 Development - 2026-08-22 - Production Daily Ingestion

### Added
- `scripts/run_daily_ingestion.py` production command.
- Ingestion freshness evaluation and Streamlit operational status.
- Supabase-backed `cortex_ingestion_runs` persistence.
- GitHub Actions daily ingestion workflow.

### Validated
- Supabase-backed production ingestion successfully processed ESPN/RotoWire data with Cortex duplicate accounting.
- 894 tests passing.

## v1.1 Development - 2026-08-12 - Structured Football Context

### Added
- Persistent 2026 player/roster and schedule/game state.
- Availability classification, ScheduleStateService, and FootballContextService.
- Stable GSIS identity propagation into Cortex.

### Validated
- Production-path football context smoke test completed successfully.
- 744 tests passing.

## v1.1 Development - 2026-08-10 - Continuous Ingestion

### Added
- Scheduled ingestion runner, ESPN/RotoWire composition, persistent diagnostics, and Streamlit ingestion status.

### Improved
- Player-resolution benchmark improved from approximately 20.559 seconds to 0.221 seconds.

### Validated
- 709 tests passing.

## v1.0.0 - 2026-08-10

- Stabilized GridironGPT / Gridiron Cortex runtime architecture.
- Verified 702 passing tests before release.
- Completed Streamlit smoke validation, branch reconciliation, documentation refresh, persistent Cortex state, and replay support.