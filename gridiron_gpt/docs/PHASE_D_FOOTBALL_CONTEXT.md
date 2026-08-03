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

### Components

- `CanonicalPlayerState`
- `PlayerStateRepository`
- `JsonlPlayerStateRepository`
- `PlayerStateService`
- `PlayerStateChange`
- `PlayerStateEventFactory`

### Behavior

The existing nflverse player catalog is promoted into a queryable canonical state rather than duplicated by another roster loader.

Meaningful changes include:

- team
- position
- roster status
- depth-chart position

Identical refreshes do not create duplicate snapshots. Meaningful transitions are converted into structured `RawEvent` evidence for Cortex.

## D2 — Injury & Availability State ✅

### Components

- `CanonicalAvailabilityState`
- `AvailabilityDesignation`
- `PracticeParticipation`
- `AvailabilityReport`
- `AvailabilityReconciler`
- `AvailabilityTrajectoryService`
- `AvailabilityEventFactory`

### Reconciliation

Multiple observations can describe different dimensions of the same player state. Official evidence takes precedence over unofficial evidence for the same field, while newer official evidence supersedes older official evidence.

Designation and practice participation reconcile independently.

### Trajectory

Supported trajectory classifications:

- improving
- stable
- worsening
- recovered
- unavailable
- unknown

Current state and direction remain separate evidence dimensions.

Example:

```text
QUESTIONABLE + DNP
        ↓
QUESTIONABLE + LIMITED
        ↓
Current risk: negative
Trajectory: improving
```

Cortex therefore does not mistake an improving injured player for a healthy player.

## D3 — Transactions & Roster Movement ✅

### Components

- `OpportunityChange`
- `RosterOpportunityService`
- `OpportunityEventFactory`
- `RosterConsequenceOrchestrator`

### Relationship Reuse

D3 reuses the existing Phase B relationship graph and propagation semantics rather than creating a separate roster-consequence graph.

Opportunity relationships include:

- `backs_up`
- `competes_with`
- `target_competitor`
- `depth_chart_competitor`

### Causal Chain

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
    ↓
Score / recommendation
```

Derived opportunity events preserve causal metadata pointing to the originating event fingerprint.

### Safety Guards

- no zero-impact propagation
- no unresolved-player propagation
- no self-consequence back onto the source player
- no opportunity-event recursive propagation
- duplicate consequences collapsed within an orchestration pass

## D4 — Snap / Route / Opportunity Context ▶ Next

D4 will add observed usage state and compare it against the opportunity Cortex inferred from roster movement.

Planned sequence:

1. Canonical usage-state model
2. Usage baseline and trend
3. Derived-vs-observed opportunity reconciliation
4. Cortex evidence integration

Target reasoning example:

```text
Starter unavailable
    ↓
Backup opportunity predicted
    ↓
Next game: snap share 28% → 67%
           touches 7 → 18
    ↓
Opportunity confirmed by observed usage
```

This distinction between **narrative opportunity** and **confirmed opportunity** is a core Phase D objective.

## Validation

Focused checkpoints completed during Phase D development:

- D1 gate: 15 passing tests
- D2.1–D2.2 gate: 26 passing tests
- D2.3 gate: 35 passing tests
- D2 complete gate: 40 passing tests
- D3.1 import/integration gate: 29 passing tests
- D3.2 gate: 34 passing tests
- D3 complete focused gate: 42 passing tests

The full repository suite should be run at the Phase D boundary.
