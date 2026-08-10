# GridironGPT Roadmap

## Vision

Build GridironGPT into a complete fantasy-football intelligence and commissioner platform powered by the reusable Gridiron Cortex engine.

## Current Status

| Area | Status |
|---|---|
| Cortex Foundation | Complete for v1.0 |
| Intelligence & Reasoning Pipeline | Complete for v1.0 |
| Multidimensional Scorecards | Complete for v1.0 |
| Event Bus / Decision History | Complete for v1.0 |
| Replay | Complete for v1.0 |
| Multi-source Ingestion | Operational |
| Automatic Ingestion → Cortex Runtime | Complete |
| Fail-open Downstream Processing | Complete |
| Persistence / Restart Verification | Complete |
| Football Context | Operational and expanding |
| Fantasy Decision Engine | Operational |
| Commissioner Suite | Operational |
| Advisor | Operational |
| Dashboard | Operational |
| Cortex Explorer | Operational |
| Knowledge Graph UI | Operational first pass |
| v1.0 Stabilization | In progress |
| Production / Cloud | Post-v1 |

Current verified regression checkpoint: **702 passed**.

## v1.0 — Current Phase

The core engine architecture is no longer in subsystem-expansion mode. The current goal is to produce a stable release candidate from the architecture already built.

### Remaining v1.0 work
- [x] Verify automatic provider ingestion reaches Cortex.
- [x] Verify downstream Cortex failures remain fail-open for ingestion.
- [x] Wire the real runtime composition to `cortex.process_event`.
- [x] Verify event history and scorecards persist.
- [x] Verify Replay reconstructs a decision after simulated restart.
- [x] Audit Streamlit for duplicate Cortex facade construction.
- [x] Audit the manual Inspector path and retain it as a diagnostic tool.
- [x] Update stale Dashboard regression metadata.
- [ ] Finish contributor-documentation refresh.
- [ ] Populate/refresh deployment documentation.
- [ ] Run final full regression suite.
- [ ] Perform Streamlit smoke test across primary pages.
- [ ] Reconcile `main` documentation-only divergence.
- [ ] Prepare merge/release/tag boundary.

## v1.0 Release Criteria

A v1.0 release candidate should satisfy all of the following:

1. All normalized runtime events enter Cortex through the shared ingestion boundary.
2. Provider health is isolated from downstream intelligence failures.
3. Duplicate evidence does not produce duplicate decisions.
4. Scorecards and event history survive restart.
5. Replay reconstructs prior decisions from persisted history.
6. Streamlit uses a shared Cortex facade rather than independent page engines.
7. Primary product pages load without runtime errors.
8. Contributor documentation matches implemented architecture.
9. Full regression suite passes at or above the current 702-test boundary.

## Post-v1 — Intelligence Improvements

Once v1.0 is stable, improve quality rather than adding unbounded architecture:
- Expand player alias and identity coverage.
- Improve unknown/ambiguous impact classification.
- Deepen injury and availability interpretation.
- Reconcile usage/opportunity signals across providers.
- Calibrate confidence against historical outcomes.
- Measure relationship-propagation effectiveness.
- Add decision outcome tracking and recommendation calibration.

## Post-v1 — Data and Operations

- Scheduled/background ingestion.
- Provider freshness and latency monitoring.
- Durable database-first repositories where scale requires them.
- Queue/worker execution for expensive processing.
- Better ingestion dashboards and alerting.
- Backup/restore procedures.
- Data-retention policies.

## Post-v1 — Product Expansion

### Cortex Explorer / Knowledge Graph
- Richer graph filtering and navigation.
- Evidence-path inspection.
- Historical relationship changes.
- Player/team dossier improvements.

### Draft Center
- Live draft state.
- Remaining player tiers.
- Cortex draft value.
- Position scarcity.
- Reach/value indicators.
- Roster construction recommendations.

### Commissioner Analytics
- Schedule fairness visualizations.
- Strength of schedule.
- Luck Index.
- Standings and team-performance history.
- Rivalry/divisional analysis.

## Production / Cloud

Productionization follows the stable local/runtime architecture rather than preceding it:
- Deployment packaging and environment configuration.
- Scheduled ingestion/background services.
- Authentication.
- Multi-user and multi-league support.
- Monitoring and alerting.
- Backups and recovery.
- Deployment automation.
- Cost controls.
- Secrets management.

## Guiding Principles

1. Cortex owns intelligence.
2. GridironGPT owns football-domain product behavior.
3. Providers retrieve data; shared ingestion owns normalization and runtime handoff.
4. Evidence comes before conclusions.
5. Preserve provenance, history, and correlation.
6. Prefer football semantics over generic math.
7. Keep infrastructure replaceable behind contracts.
8. Keep presentation separate from scoring/reasoning.
9. Make important decisions replayable and explainable.
10. Preserve a passing regression suite after every significant implementation batch.
