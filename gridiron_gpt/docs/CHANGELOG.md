# Changelog

## 2026-08-17 — Projected Fantasy Points v1

### Added
- Historical-stat projection pipeline using regular-season NFL history only; preseason statistics are intentionally excluded.
- Recency-weighted per-game historical blending with available-season weight renormalization.
- Small-sample handling so limited appearances do not extrapolate directly to a full 17-game workload without adjustment.
- Fantasy scoring projections for PPR, half-PPR, and standard formats.
- Player-level projected season points and projected points per game.
- Cached projection views on the Streamlit Fantasy Rankings page.
- `Proj Pts` and `Proj PPG` visibility in expanded and collapsed ranking rows.
- Projection context in Draft Assistant Best Available and Best Value displays.
- Projected Points and Projected PPG support in Excel and PDF ranking exports, including the Draft Day preset.

### Projection Boundary

Projected production is currently informational only. It does not alter the production GridironGPT ranking score, Best Available ordering, or Best Value calculation.

```text
regular-season historical stats
→ per-game normalization
→ recency-weighted blending
→ small-sample adjustment
→ expected 17-game production
→ fantasy scoring
→ projected points / projected PPG
→ Rankings UI + Draft Assistant + Excel/PDF
```

This boundary intentionally provides a stable projection baseline before projected production receives any scoring weight. The next scoring experiment will compare 0%, 5%, and 10% projection influence without changing the live production formula.

### Validation

```text
834 passed
```

The UI and Draft Day Excel export were manually verified to expose the same projection values. This is the stable baseline for the projection-weight comparison experiment.

---

## 2026-08-14 — Integrated Fantasy Ranking Intelligence

### Added
- `FantasyRankingDataService` for loading real historical, market, role, and canonical football-state data into the ranking pipeline.
- Current-season ADP/market evidence with explicit season provenance and stale-market protection.
- Recent role/usage evidence normalized within fantasy position.
- Conservative cross-source player-name normalization for historical and ADP matching.
- Legacy Cortex scorecard fallback matching by normalized player name and team when canonical IDs differ.
- Anchor-evidence validation so availability/role/context alone cannot manufacture a fantasy ranking.
- `FantasyRankingExplanationService` for evidence-based ranking explanations.
- `explained_overall` population output with rank, score, strengths, concerns, provenance, and missing-evidence context.

### Ranking Model

The integrated ranking path now combines:

```text
historical production
+ current 2026 ADP / market
+ recent role / usage
+ Cortex intelligence
+ canonical availability
→ evidence sufficiency
→ weighted fantasy ranking
→ rank-aware explanation
```

Missing evidence is treated as unavailable evidence rather than negative evidence. Available weights are renormalized rather than silently assigning zeroes to missing sources.

### Explanation Semantics
- Availability remains evidence but is not described as an elite fantasy strength.
- Neutral Cortex intelligence is not presented as a negative factor.
- Missing evidence is called out explicitly without being converted into a concern.
- Explanation generation is downstream of scoring and does not alter ranking results.

### Validation

```text
780 passed
```

Real-data verification produced integrated Top-25 rankings using historical, 2026 market, role, Cortex, and availability evidence while preserving source-specific provenance.

---

## 2026-08-10 — v1.0 Cortex Runtime Integration & Stabilization

### Added
- Shared runtime ingestion composition through `build_runtime_ingestion_service(cortex)`.
- Automatic forwarding of normalized `RawEvent` objects into `CortexFacade.process_event()`.
- Optional downstream `event_processor` hook in `IngestionService`.
- Persisted ingestion-run repository support in runtime composition.
- End-to-end production-path coverage from provider record through Cortex persistence and Replay.
- Restart verification proving persisted Cortex decisions can be reconstructed without reprocessing the source article.

### Changed
- Provider adapters remain source/translation components and no longer need engine-specific processing responsibilities.
- Runtime ingestion now uses the same Cortex facade contract as the rest of the application.
- Streamlit runtime architecture documented around one shared session-state `CortexFacade`.
- Dashboard regression metadata updated from the stale 652 checkpoint to the verified 702 checkpoint.
- Project overview and architecture documentation rewritten around the implemented v1.0 boundaries.

### Reliability
- Downstream Cortex processor failures are fail-open at the ingestion boundary.
- Successful provider fetches are not retried because Cortex processing failed.
- Processor exception logging reads source provenance from the `RawEvent` evidence contract rather than nonexistent event attributes.
- Duplicate-event handling remains upstream of duplicate downstream decisions.

### Persistence & Replay
- Cortex event history persists through the event-bus repository.
- Player scorecards persist independently of Streamlit process lifetime.
- Correlation IDs connect normalized input events to downstream Cortex decision events.
- Replay reconstructs decisions from persisted event history after application restart.

### Validation

```text
702 passed
```

This checkpoint preceded the integrated fantasy-ranking work.

---

## 2026-08-03 — Live Platform & UI Modernization

### Added
- Supabase-backed live signal loading into the player scoring path.
- Duplicate-safe raw article persistence for unique `story_hash` collisions.
- Shared visualization models and Streamlit intelligence charts.
- Advisor 2.0 recommendation, confidence, signal-impact, Cortex-profile, timeline, and supporting-headline views.
- Dashboard 2.0 recommendation distribution, team momentum, position rankings, and live Cortex ranking views.
- Expanded Commissioner Suite with configurable league settings, schedule generation, schedule alternatives/analytics, rivalry constraints, configurable playoff duration, draft workflows, league history, and schedule exports/delivery support.

### Changed
- Dashboard and Advisor consume the scored-player map rather than relying only on static presentation data.
- UI chart calculations are separated from Streamlit rendering.
- Commissioner scheduling treats divisional home/away requirements as hard constraints where configuration permits and optimizes remaining assignments for balance.

### Fixed
- Duplicate RSS stories no longer terminate ingestion with a Supabase unique-key error.
- Advisor top-recommendation confidence path typo corrected.
- Small-league schedule generation no longer assumes every schedule can achieve an impossible home/away spread.
- Schedule analytics quality scoring handles balanced reference schedules correctly.
- CSV and iCalendar schedule exports validated against generated schedules.

### Validation

```text
619 passed
```

This checkpoint preceded the later Cortex runtime-integration work.

---

## Historical Milestones

Repository history preserves the detailed development sequence for Cortex foundation, persistent intelligence, semantic propagation, nflverse integration, evidence reasoning, multidimensional scoring, ingestion reliability, football context, Cortex Explorer, knowledge-graph work, event-bus observability, Replay, and intermediate regression checkpoints.
