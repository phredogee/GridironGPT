# Phase D — Football Knowledge & Context

## Purpose

Phase D teaches Gridiron Cortex the durable football state surrounding incoming evidence. The goal is to reason about changes in football reality, not only isolated articles or box scores.

The architecture keeps football-domain integration in GridironGPT while Cortex continues to own generic intelligence processing.

```text
NFL data / reports
    ↓
GridironGPT football-state services
    ↓
Canonical football state
    ↓
State changes / derived consequences
    ↓
RawEvent evidence
    ↓
Gridiron Cortex
```

## D1 — Canonical NFL State ✅

Components include `CanonicalPlayerState`, player-state repositories/services, change detection, and `PlayerStateEventFactory`. The existing nflverse player catalog is promoted into queryable canonical state. Meaningful team, position, roster-status, and depth-chart changes become structured Cortex evidence while identical refreshes are suppressed.

## D2 — Injury & Availability State ✅

Components include canonical availability state/report models, `AvailabilityReconciler`, `AvailabilityTrajectoryService`, and `AvailabilityEventFactory`.

Official evidence takes precedence over unofficial evidence for the same field, while newer official evidence supersedes older official evidence. Designation and practice participation reconcile independently.

Supported trajectories are improving, stable, worsening, recovered, unavailable, and unknown. Current risk and direction remain separate evidence dimensions, so Cortex does not mistake an improving injured player for a healthy player.

## D3 — Transactions & Roster Movement ✅

Components include `OpportunityChange`, `RosterOpportunityService`, `OpportunityEventFactory`, and `RosterConsequenceOrchestrator`.

D3 reuses the Phase B relationship graph and propagation semantics. Opportunity relationships include `backs_up`, `competes_with`, `target_competitor`, and `depth_chart_competitor`.

```text
Source player event
    ↓
Source impact
    ↓
PropagationPlanner (one hop)
    ↓
OpportunityChange
    ↓
Affected-player RawEvent
    ↓
SignalProcessor
```

Safety guards prevent zero-impact/unresolved propagation, self-consequences, recursive opportunity propagation, and duplicate consequences. Derived events preserve causal metadata pointing to the originating event fingerprint.

## D4 — Snap / Route / Opportunity Context ✅

### Canonical Usage State

`CanonicalUsageState` represents observed participation and opportunity:

- snaps / snap share
- routes / route participation
- carries / carry share
- targets / target share
- red-zone carries and targets
- red-zone opportunities
- derived touches
- derived opportunity concentration

Partial provider coverage is explicitly valid. A source can contribute useful carry/target information even when snap or route data is unavailable.

### Usage Baseline & Trend

`UsageTrendService` compares the current game with a configurable recent-game baseline (three prior games by default).

Trend vocabulary:

- rising
- stable
- falling
- mixed
- unknown

Small changes below meaningful thresholds are treated as stable rather than noise.

### Opportunity Reconciliation

`OpportunityReconciliationService` compares D3's predicted opportunity with D4's observed usage.

```text
Predicted opportunity ↑ + observed usage RISING  → CONFIRMED
Predicted opportunity ↑ + observed usage FALLING → CONTRADICTED
Predicted opportunity ↓ + observed usage FALLING → CONFIRMED
Stable / mixed / unknown usage                    → INCONCLUSIVE
```

Confidence accounts for available baseline history and predicted opportunity magnitude.

### Cortex Integration

`UsageEventFactory` converts both usage trends and opportunity reconciliation into normal `RawEvent` evidence.

Rising usage is positive evidence, falling usage is negative evidence, and non-directional usage remains neutral. Confirmation is interpreted relative to the original prediction: confirming a predicted decrease is negative, while confirming a predicted increase is positive.

This creates the end-to-end chain:

```text
Roster change
    ↓
Opportunity predicted
    ↓
Usage observed
    ↓
Baseline/trend comparison
    ↓
Prediction confirmed / contradicted
    ↓
Cortex evidence
    ↓
Scoring / recommendation
```

D4 therefore distinguishes **narrative opportunity** from **confirmed opportunity**.

## D5 — Schedule & Opponent Context ▶ Next

Planned sequence:

1. Canonical game context
2. Upcoming schedule / bye / rest context
3. Evidence-based opponent and matchup context
4. Cortex integration

Schedule facts should remain separate from fantasy interpretation so matchup heuristics can later be calibrated independently.

## Validation

Focused checkpoints completed during Phase D development:

- D1 gate: 15 passing tests
- D2.1–D2.2 gate: 26 passing tests
- D2.3 gate: 35 passing tests
- D2 complete gate: 40 passing tests
- D3.1 import/integration gate: 29 passing tests
- D3.2 gate: 34 passing tests
- D3 complete focused gate: 42 passing tests
- D4.1 gate: 8 passing tests
- D4.2 gate: 17 passing tests
- D4.3 gate: 26 passing tests
- D4 complete focused gate: 35 passing tests

The full repository suite should be run at the Phase D boundary.
