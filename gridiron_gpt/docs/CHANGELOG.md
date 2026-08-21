# Changelog

## 2026-08-21 — Roster-Aware Draft Assistant

### Added
- `DraftBoardState` with ordered pick history and explicit `MY_TEAM` / `OTHER_TEAM` ownership.
- Live Draft Mode controls for drafted players, My Team assignments, restore, undo, and reset.
- `FantasyDraftPoolService` for tested remaining-population, Best Available, and Best Value filtering.
- `FantasyRosterNeedsService` for starter-oriented QB/RB/WR/TE roster deficits.
- `FantasyRosterAdviceService` for advisory roster summaries and per-player need badges.
- Draft Assistant UI context such as `Roster Needs: ...` and `Fills TE need`.
- Regression coverage for draft-pool filtering, roster needs, and advisory behavior.

### Changed
- The Streamlit Fantasy Rankings page now consumes the tested draft-pool service instead of duplicating filtering logic.
- The CLI ranking path was migrated to the same production ranking source used by the current fantasy board.
- Projected production is active in the production ranking model at its configured production weight.
- Best Available and Best Value continue to consume the authoritative production population rather than recomputing an alternate score.

### Architectural Boundary

Roster context is downstream advice, not production scoring.

```text
Production Rankings
        ↓
Draft Pool
  ├─ Best Available
  └─ Best Value
        ↓
DraftBoardState + My Team
        ↓
Roster Needs
        ↓
Roster Advice
        ↓
Draft Assistant presentation
```

A player's `ranking_score` does not change because a user's roster already filled that position. Current roster advice annotates decisions without reordering Best Available or Best Value.

### Validation

```text
869 passed
```

Interactive Streamlit validation confirmed that My Team assignments update roster-needs counts while drafted players leave the available pool and the underlying ranking order remains stable.

---

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

### Historical Note

This milestone originally introduced projections as informational-only output. That boundary was later superseded: projected production is now included in the production ranking model at its configured weight while the direct Proj Pts / Proj PPG values remain visible for interpretation.

### Validation

```text
834 passed
```

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

```text
historical production
+ current ADP / market
+ recent role / usage
+ Cortex intelligence
+ canonical availability
→ evidence sufficiency
→ weighted fantasy ranking
→ rank-aware explanation
```

Missing evidence is treated as unavailable evidence rather than negative evidence. Available weights are renormalized rather than silently assigning zeroes to missing sources.

### Validation

```text
780 passed
```

---

## 2026-08-10 — v1.0 Cortex Runtime Integration & Stabilization

### Added
- Shared runtime ingestion composition through `build_runtime_ingestion_service(cortex)`.
- Automatic forwarding of normalized `RawEvent` objects into `CortexFacade.process_event()`.
- Optional downstream `event_processor` hook in `IngestionService`.
- Persisted ingestion-run repository support in runtime composition.
- End-to-end production-path coverage from provider record through Cortex persistence and Replay.
- Restart verification proving persisted Cortex decisions can be reconstructed without reprocessing the source article.

### Reliability
- Downstream Cortex processor failures are fail-open at the ingestion boundary.
- Successful provider fetches are not retried because Cortex processing failed.
- Duplicate-event handling remains upstream of duplicate downstream decisions.

### Validation

```text
702 passed
```

---

## 2026-08-03 — Live Platform & UI Modernization

### Added
- Supabase-backed live signal loading into the player scoring path.
- Duplicate-safe raw article persistence for unique `story_hash` collisions.
- Shared visualization models and Streamlit intelligence charts.
- Advisor 2.0 recommendation, confidence, signal-impact, Cortex-profile, timeline, and supporting-headline views.
- Dashboard 2.0 recommendation distribution, team momentum, position rankings, and live Cortex ranking views.
- Expanded Commissioner Suite with configurable league settings, schedule generation, schedule alternatives/analytics, rivalry constraints, configurable playoff duration, draft workflows, league history, and schedule exports/delivery support.

### Validation

```text
619 passed
```

---

## Historical Milestones

Repository history preserves the detailed development sequence for Cortex foundation, persistent intelligence, semantic propagation, nflverse integration, evidence reasoning, multidimensional scoring, ingestion reliability, football context, Cortex Explorer, knowledge-graph work, event-bus observability, Replay, ranking integration, projection experiments, and intermediate regression checkpoints.
