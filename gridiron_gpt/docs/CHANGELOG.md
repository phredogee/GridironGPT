# Changelog

## 2026-08-31 — Decision Center Canonical Player Pool

### Fixed
- Decision Center now builds its selectable player universe from the canonical NFL roster catalog instead of only from players that currently have Cortex score data.
- Start / Sit, Waivers, Trade, Roster, and Commissioner Hub can retain fantasy-relevant catalog players even when those players have no recent signals.
- Stable GSIS IDs are used when available, with existing fallback IDs retained for compatibility.
- Catalog players are enriched with Cortex score/confidence data when present; unscored players remain selectable with neutral score/confidence defaults.
- Added focused regression tests for unscored-player retention, fantasy-position filtering, stable IDs, and team-code fallback behavior.

### Architectural Boundary

The canonical player catalog is now authoritative for Decision Center player identity and population. Cortex score data is enrichment, not an inclusion gate. This keeps roster construction independent from whether a player happened to produce a recent intelligence signal.

---

## 2026-08-27 — Scarcity, Pick Timing, and Wait Risk

### Added
- `FantasyPositionScarcityService` for same-position depth, score-drop, and tier-cliff awareness.
- Scarcity integration into Best Fit using bounded advisory adjustments without mutating production rankings.
- `FantasyPickTimingService` with `TAKE NOW`, `CAN WAIT`, and `NEUTRAL` guidance.
- Production-shaped tier handoff from existing market views into scarcity/pick-timing evaluation.
- `FantasyDraftSettings` for validated league size and draft slot.
- `FantasyDraftTurnService` for deterministic snake-draft turn calculation.
- `FantasyWaitRiskService` and `FantasyWaitRiskViewService` for ADP-based next-pick availability.
- `fantasy_wait_risk_ui` presentation adapter so Streamlit renders domain output rather than owning business logic.
- Draft Assistant controls for league size and draft slot.
- State-aware market guidance: upcoming-pick availability before the user's turn and Wait Risk while on the clock.
- Focused service, scenario, integration, UI-contract, and production-shape regression tests.

### Architectural Boundary

Scarcity, Pick Timing, and Wait Risk remain advisory layers downstream of the authoritative production board. Pick Timing answers whether the same-position pool can tolerate waiting; Wait Risk answers whether the specific player is likely to survive to the user's next selection. Neither mutates `ranking_score`.

### Validation

```text
990 passed
```

Interactive Streamlit validation confirmed:
- live market tiers reach Pick Timing,
- snake turns advance correctly from slot-based settings,
- pre-turn guidance targets the user's upcoming pick,
- on-the-clock guidance targets the following user selection,
- positional timing and market availability remain independently explainable.

---

## 2026-08-22 — Best Fit Right Now

### Added
- `FantasyBestFitService` as a separate contextual draft recommendation layer.
- `BestFitRecommendation` output with advisory fit score, roster-need state, and Draft Value context.
- `FantasyBestFitView` / `build_best_fit_views()` for UI-ready explanations.
- **Best Fit Right Now** as a third Draft Assistant recommendation surface alongside Best Available and Best Value.
- Focused regression tests for close-vs-large ranking gaps, roster-need influence, Draft Value influence, limits, missing market context, score immutability, and explanation output.

### Architectural Boundary

Best Fit is advisory. Its initial conservative heuristic reads production ranking quality and adds bounded contextual signals for active roster need and Draft Value. It may reorder the Best Fit advisory list, but it does **not** mutate production `ranking_score`, Best Available, or Best Value.

### Validation

```text
878 passed
```

Interactive Streamlit validation confirmed Best Fit responds as My Team changes while the underlying production board remains stable.

---

## 2026-08-21 — Roster-Aware Draft Assistant

### Added
- `DraftBoardState` with ordered pick history and explicit `MY_TEAM` / `OTHER_TEAM` ownership.
- Live Draft Mode controls for drafted players, My Team assignments, restore, undo, and reset.
- `FantasyDraftPoolService` for tested remaining-population, Best Available, and Best Value filtering.
- `FantasyRosterNeedsService` for starter-oriented QB/RB/WR/TE roster deficits.
- `FantasyRosterAdviceService` for advisory roster summaries and per-player need badges.
- Draft Assistant UI roster context and regression coverage.

### Validation

```text
869 passed
```

---

## 2026-08-17 — Projected Fantasy Points v1

Historical-stat projections, projected points/PPG, Streamlit/export presentation, and the projection pipeline were introduced. Projection influence was later activated in the production ranking model at its configured weight.

### Validation

```text
834 passed
```

---

## 2026-08-14 — Integrated Fantasy Ranking Intelligence

Integrated historical production, market/ADP, recent role, Cortex intelligence, canonical availability, anchor-evidence validation, and evidence-based ranking explanations.

### Validation

```text
780 passed
```

---

## 2026-08-10 — v1.0 Cortex Runtime Integration & Stabilization

Added shared runtime ingestion composition, automatic RawEvent forwarding into Cortex, persistence/restart verification, Replay, and downstream fail-open behavior.

### Validation

```text
702 passed
```

---

## 2026-08-03 — Live Platform & UI Modernization

Added Supabase-backed live signal loading, duplicate-safe article persistence, shared visualization models, Advisor/Dashboard modernization, and expanded Commissioner Suite capabilities.

### Validation

```text
619 passed
```

---

## Historical Milestones

Repository history preserves the detailed development sequence for Cortex foundation, persistent intelligence, semantic propagation, nflverse integration, evidence reasoning, multidimensional scoring, ingestion reliability, football context, Cortex Explorer, knowledge-graph work, event-bus observability, Replay, ranking integration, projection experiments, and intermediate regression checkpoints.
