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
| Best Fit Right Now | Operational |
| Positional Scarcity / Tier Drop | Operational |
| Pick Timing | Operational |
| Snake-Draft Turn Awareness | Operational |
| Market Availability / Wait Risk | Operational |
| Commissioner Suite | Operational |
| Production / Cloud | Future phase |

Current verified regression checkpoint: **990 passed**.

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
- [x] Add positional scarcity and tier-cliff awareness.
- [x] Add Pick Timing guidance while preserving the production score.
- [x] Validate production-shaped tier handoff for live Pick Timing.
- [x] Add validated league-size and draft-slot settings.
- [x] Add deterministic snake-draft turn calculation.
- [x] Add consensus-ADP-based next-pick availability / Wait Risk.
- [x] Distinguish pre-turn availability from on-the-clock Wait Risk in the UI.
- [x] Validate live snake progression and advisory independence in Streamlit.

## Next Milestone — Draft-Night Stabilization and Strategy Context

The core draft assistant now answers four separate questions:

1. Who is strongest on the authoritative board?
2. Who is the best market value?
3. Which player best fits the current roster and positional landscape?
4. Can the position wait, and is the specific player likely to survive to the next selection?

Near-term work should prioritize stability and explainability before adding more scoring complexity.

Planned steps:
- [ ] Run extended live-draft simulations across multiple draft slots.
- [ ] Verify turn transitions at snake boundaries and back-to-back picks.
- [ ] Improve zero-drop wording such as `0.0-point drop` for human readability.
- [ ] Add positional-run awareness without mutating the production board.
- [ ] Add configurable roster targets / league lineup requirements.
- [ ] Evaluate persistent draft-session storage.
- [ ] Add post-draft roster analysis.

## Draft Center Expansion

Later draft-center candidates:
- Reach/value indicators.
- Positional-run awareness.
- Draft-round strategy context.
- League-specific lineup requirements.
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
