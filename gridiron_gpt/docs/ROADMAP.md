# GridironGPT Roadmap

## Vision

Build GridironGPT into a complete fantasy-football intelligence, live draft, and commissioner platform powered by the reusable Gridiron Cortex engine.

## Current Status

| Area | Status |
|---|---|
| Cortex Foundation | Complete for current architecture |
| Intelligence & Reasoning Pipeline | Operational |
| Persistence / Replay | Operational |
| Integrated Fantasy Rankings | Operational |
| Projection-Aware Production Ranking | Operational |
| Ranking Explanations | Operational first pass |
| Position Tiers / Draft Value | Operational |
| Live Draft State / My Team | Operational |
| Best Available / Best Value | Operational |
| Roster Needs / Roster Advice | Operational first pass |
| Best Fit Right Now | Operational first pass |
| Positional Scarcity / Tier Drop | Next milestone |
| Commissioner Suite | Operational |
| Production / Cloud | Future phase |

Current verified regression checkpoint: **878 passed**.

## Completed Draft Milestones

- [x] Establish one authoritative production ranking population.
- [x] Add projected production to the configured production ranking model.
- [x] Add position tiers and Draft Value.
- [x] Add live drafted-player filtering.
- [x] Add `DraftBoardState` with My Team vs. Other Team ownership.
- [x] Add tested Best Available and Best Value draft-pool services.
- [x] Add starter-oriented roster-needs evaluation and advice.
- [x] Define and test the Best Fit advisory contract.
- [x] Add a Best Fit presentation/view layer with concise reasons.
- [x] Expose Best Fit Right Now in the Draft Assistant.
- [x] Verify Best Fit responds to roster context without changing production ranking order.

## Next Milestone — Positional Scarcity / Tier-Drop Awareness

Answer the draft question:

> If I pass on this position now, how much worse does the next realistic option become?

Planned inputs:
- Current player's production ranking score.
- Next available players at the same position.
- Position tier boundaries.
- Score drop to the next realistic option.
- Remaining depth at the position.
- Market/ADP context where useful and defensible.

Planned steps:
- [ ] Define a `FantasyPositionScarcityService` contract.
- [ ] Add focused tests for meaningful score drop-offs and tier cliffs.
- [ ] Keep scarcity independent from production `ranking_score`.
- [ ] Produce explainable scarcity labels/reasons.
- [ ] Feed scarcity into Best Fit as a bounded advisory signal only after focused validation.
- [ ] Simulate multiple roster-construction paths.
- [ ] Run full regression and Streamlit smoke tests.

## Draft Center Expansion

After scarcity:
- Reach/value indicators.
- Expected availability at future picks where modeling is defensible.
- Draft-round strategy and positional-run awareness.
- Configurable roster targets and league-specific lineup requirements.
- Persistent draft sessions.
- Post-draft roster analysis.

## Regular-Season Expansion

Later reuse the player-evaluation foundation for:
- Best Available waiver/free-agent board.
- Add/drop recommendations.
- Best available over the next X weeks.
- Schedule-aware streaming advice.
- Start/sit and roster optimization.

These should reuse production player intelligence while introducing schedule and roster context as separate decision layers.

## Intelligence Quality Improvements

- Measure ranking quality against season outcomes before large weight changes.
- Calibrate ranking weights only with sufficient evidence.
- Expand player alias/identity coverage.
- Improve injury and availability interpretation.
- Reconcile usage/opportunity evidence across providers.
- Calibrate confidence against historical outcomes.
- Add recommendation outcome tracking.

## Data, Operations, and Production

- Scheduled/background ingestion.
- Provider freshness and latency monitoring.
- Durable database-first repositories where scale requires them.
- Queue/worker execution for expensive processing.
- Backup/restore and data-retention procedures.
- Deployment packaging, authentication, multi-user/multi-league support, monitoring, secrets, cost management, and automation.

## Guiding Principles

1. Cortex owns reusable intelligence.
2. GridironGPT owns football-domain product behavior.
3. Evidence and provenance precede conclusions.
4. Keep contextual advice separate from production scoring.
5. Do not create a second hidden production ranking engine.
6. Preserve a stable authoritative production board.
7. Make contextual recommendations explainable.
8. Maintain a passing regression suite after every significant implementation batch.
