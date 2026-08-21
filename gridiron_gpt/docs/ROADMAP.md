# GridironGPT Roadmap

## Vision

Build GridironGPT into a complete fantasy-football intelligence, live draft, and commissioner platform powered by the reusable Gridiron Cortex engine.

## Current Status

| Area | Status |
|---|---|
| Cortex Foundation | Complete for current architecture |
| Intelligence & Reasoning Pipeline | Operational |
| Multidimensional Scorecards | Operational |
| Event Bus / Decision History | Operational |
| Replay | Operational |
| Multi-source Ingestion | Operational |
| Automatic Ingestion → Cortex Runtime | Complete |
| Persistence / Restart Verification | Complete |
| Integrated Fantasy Rankings | Operational |
| Projection-Aware Production Ranking | Operational |
| Ranking Explanations | Operational first pass |
| Position Tiers / Draft Value | Operational |
| Live Draft State | Operational |
| My Team Ownership | Operational |
| Best Available / Best Value Filtering | Operational |
| Roster Needs | Operational |
| Roster Advice | Operational first pass |
| Best Fit Right Now | Next milestone |
| Commissioner Suite | Operational |
| Production / Cloud | Future phase |

Current verified regression checkpoint: **869 passed**.

## Completed Fantasy Ranking and Draft Milestones

- [x] Integrate historical production, market/ADP, recent role, Cortex, and canonical availability.
- [x] Preserve missing evidence as missing rather than negative.
- [x] Enforce anchor-evidence sufficiency.
- [x] Add rank-aware evidence explanations.
- [x] Add projected points and projected PPG.
- [x] Validate projection-weight experiments.
- [x] Activate projection influence in the production ranking model at its configured weight.
- [x] Unify CLI and current UI around the production ranking source.
- [x] Add position tiers and Draft Value derived from production rank.
- [x] Add live drafted-player filtering.
- [x] Add `DraftBoardState` with My Team vs. Other Team ownership.
- [x] Add tested Best Available and Best Value draft-pool services.
- [x] Add starter-oriented roster-needs evaluation.
- [x] Add advisory roster summaries and per-player need badges.
- [x] Validate roster-aware behavior interactively in Streamlit.

## Next Milestone — Best Fit Right Now

Create a separate draft recommendation service that answers a more contextual question than raw ranking:

> Given the production board, what is the best fit for my roster right now?

Candidate inputs:
- Production ranking score/rank.
- Current roster needs.
- Position tier.
- Draft Value / market opportunity.
- Position scarcity.
- Current draft stage / pick context where available.

Design requirement:

**Best Fit Right Now must remain downstream of the production ranking model.** It may produce a separate advisory score or explanation, but it must not silently rewrite `ranking_score`.

Planned steps:
- [ ] Define Best Fit advisory contract and explanation output.
- [ ] Add focused tests before UI integration.
- [ ] Add position-scarcity context.
- [ ] Add draft-stage awareness if the recommendation quality benefits from it.
- [ ] Expose Best Fit Right Now in Draft Assistant.
- [ ] Simulate multiple roster-construction paths.
- [ ] Verify production board order remains unchanged.

## Near-Term Stabilization

- [ ] Keep project documentation synchronized with implemented architecture.
- [ ] Run full regression suite after every significant batch.
- [ ] Continue Streamlit smoke tests after Draft Assistant changes.
- [ ] Review stale branches/documentation before release preparation.
- [ ] Improve deployment documentation.

## Intelligence Quality Improvements

- Measure ranking quality against season outcomes before making large weight changes.
- Calibrate ranking weights only with sufficient evidence.
- Expand player alias and identity coverage.
- Improve injury and availability interpretation.
- Reconcile usage/opportunity evidence across providers.
- Calibrate confidence against historical outcomes.
- Measure relationship-propagation effectiveness.
- Add recommendation outcome tracking.

## Draft Center Expansion

After Best Fit Right Now:
- Position scarcity and drop-off warnings.
- Reach/value indicators.
- Expected availability at future picks where modeling is defensible.
- Draft-round strategy and positional run awareness.
- Configurable roster targets and league-specific lineup requirements.
- Persistent draft sessions.
- Post-draft roster analysis.

## Regular-Season Expansion

The same player-evaluation foundation can later support:
- Best Available waiver/free-agent board.
- Add/drop recommendations.
- Best available over the next X weeks.
- Schedule-aware streaming advice.
- Start/sit and roster optimization.

These should reuse production player intelligence while introducing schedule and roster context as separate decision layers.

## Data and Operations

- Scheduled/background ingestion.
- Provider freshness and latency monitoring.
- Durable database-first repositories where scale requires them.
- Queue/worker execution for expensive processing.
- Backup/restore procedures.
- Data-retention policies.

## Production / Cloud

- Deployment packaging and environment configuration.
- Authentication.
- Multi-user and multi-league support.
- Background services.
- Monitoring and alerting.
- Backups and recovery.
- Deployment automation.
- Secrets and cost management.

## Guiding Principles

1. Cortex owns reusable intelligence.
2. GridironGPT owns football-domain product behavior.
3. Evidence and provenance precede conclusions.
4. Keep presentation and contextual advice separate from production scoring.
5. Do not create a second hidden ranking engine.
6. Preserve a stable authoritative production board.
7. Make contextual recommendations explainable.
8. Keep infrastructure replaceable behind contracts.
9. Preserve decision history where persistence is required.
10. Maintain a passing regression suite after every significant implementation batch.
