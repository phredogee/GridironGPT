# Changelog

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

This is the current verified full regression checkpoint before the final v1.0 stabilization/smoke-test pass.

### Stabilization Remaining
- Refresh remaining contributor documentation.
- Review known issues and commands.
- Complete deployment-plan documentation.
- Run final full regression suite after documentation/stale-reference cleanup.
- Perform Streamlit smoke test.
- Reconcile branch/README history and prepare merge/release boundary.

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
