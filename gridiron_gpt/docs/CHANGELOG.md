# Changelog

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

### Next

Add positional scarcity / tier-drop awareness as an independently tested advisory signal before considering it as an input to Best Fit.

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
