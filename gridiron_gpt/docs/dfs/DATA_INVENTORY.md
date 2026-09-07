# GridironGPT DFS Data Inventory

## Purpose

This document records which data required by the DFS Capstone already exists in GridironGPT, which data can be derived from existing sources, and which data requires new DFS-specific integration.

The goal is to validate project feasibility before model development begins.

## Existing GridironGPT Data Foundation

GridironGPT already has an active structured-data pipeline using `nflreadpy` / nflverse. Current documented datasets include:

- player identities;
- seasonal rosters;
- weekly player statistics.

The current weekly-stat pipeline includes opportunity and production metrics such as:

- targets;
- carries;
- receptions;
- passing yards;
- rushing yards;
- receiving yards;
- passing touchdowns;
- rushing touchdowns;
- receiving touchdowns.

GridironGPT also has active NFL/fantasy news sources and an existing projection layer. These are useful supporting inputs, but the DFS Capstone will not assume that existing season-long projections are the final DFS prediction model.

## DFS Data Inventory

| Data Requirement | Current Status | Existing Source / Capability | DFS Action |
| --- | --- | --- | --- |
| Player identity | Available | nflverse / internal player catalog | Reuse |
| Team | Available | nflverse rosters / weekly stats | Reuse |
| Position | Available | nflverse rosters / weekly stats | Reuse |
| Season and week | Available | nflverse weekly stats | Reuse |
| Passing production | Available | nflverse weekly stats | Reuse |
| Rushing production | Available | nflverse weekly stats | Reuse |
| Receiving production | Available | nflverse weekly stats | Reuse |
| Targets | Available | nflverse weekly stats | Reuse |
| Carries | Available | nflverse weekly stats | Reuse |
| Historical fantasy-point target | Derivable | existing weekly statistics | Calculate using platform scoring rules |
| Rolling recent performance | Derivable | historical weekly statistics | Build DFS feature pipeline |
| Rolling targets / carries | Derivable | historical weekly statistics | Build DFS feature pipeline |
| Recent scoring trend | Derivable | historical weekly statistics | Build DFS feature pipeline |
| Opponent / matchup context | Partial / to validate | current matchup-related infrastructure exists, but documented nflverse pipeline does not yet include opponent quality in its signals | Validate and extend |
| Injury status | Gap | current legacy injury pipeline is a placeholder; formal injury/participation pipeline is documented as planned | Add reliable source before using as model feature |
| Practice participation | Gap | planned | Stretch / later feature |
| Depth chart / starter status | Gap | documented as planned | Add if reliable source is available |
| Snap share / route participation | Not confirmed | not confirmed by current documented active pipeline | Research source; do not promise for MVP |
| Weather | Not confirmed | no confirmed active DFS-ready source | Optional later feature |
| Game total / betting environment | Not confirmed | no confirmed active source | Optional later feature |
| DraftKings weekly salary | New DFS requirement | none found in existing repo | Add DFS salary provider/import |
| FanDuel weekly salary | New DFS requirement | none found in existing repo | Add DFS salary provider/import |
| DraftKings slate eligibility | New DFS requirement | none found in existing repo | Add with salary/slate import |
| FanDuel slate eligibility | New DFS requirement | none found in existing repo | Add with salary/slate import |
| DraftKings scoring rules | New DFS requirement | none found in existing repo | Implement platform configuration |
| FanDuel scoring rules | New DFS requirement | none found in existing repo | Implement platform configuration |
| Salary cap / roster constraints | New DFS requirement | none found in existing repo | Implement optimizer constraints |
| Human lock / exclude preferences | New DFS requirement | none | Implement HITL controls |

## Initial MVP Feature Set

The first model should use features that are already available or safely derivable from existing historical structured data.

Proposed MVP feature groups:

1. **Player identity context**
   - position;
   - team;
   - opponent when validated.

2. **Recent production**
   - rolling fantasy-point average;
   - rolling passing yards;
   - rolling rushing yards;
   - rolling receiving yards;
   - rolling touchdown production.

3. **Recent opportunity**
   - rolling targets;
   - rolling carries;
   - receptions.

4. **Trend features**
   - most recent game compared with three-game average;
   - three-game average compared with season average;
   - recent opportunity change.

Only information available before kickoff may be used as a model input.

## Primary Prediction Target

One training observation represents one player in one NFL game/week.

The primary target is:

> Actual fantasy-point production for that player-game/week.

Historical fantasy points can be calculated from the underlying weekly statistical record using a platform-specific scoring adapter.

For the first experiment, the project may either:

- train against one clearly defined scoring target and later add a second platform; or
- create separate DraftKings and FanDuel target columns from the same underlying football statistics.

The underlying football data remains shared.

## Initial Model Experiment

### Baseline

A simple pre-game projection such as a rolling recent fantasy-point average.

### Candidate Models

Initial candidates may include:

- linear regression;
- random forest regression;
- gradient-boosted tree regression.

The final model is selected through evaluation rather than predetermined during Phase 1.

### Evaluation

Primary metrics:

- MAE;
- RMSE;
- predicted-vs-actual correlation;
- improvement over the simple baseline.

The train/validation/test process must be chronological to reduce data leakage.

## DFS-Specific New Data Work

The main data additions required for the Capstone are not general NFL statistics. They are the platform-specific weekly DFS inputs:

```text
DraftKings / FanDuel Slate
        ↓
Player + Platform ID
Position / Eligibility
Team / Game
Actual Weekly Salary
Platform
Slate
        ↓
Canonical DFS Slate Record
```

The DFS subsystem should use a provider abstraction so the rest of GridironGPT does not depend on one acquisition method.

Proposed contract:

```text
DFSDataProvider
    ├── DraftKingsSalaryProvider
    ├── FanDuelSalaryProvider
    └── CsvSalaryProvider / fallback
            ↓
       DFS Slate Records
```

## Human-in-the-Loop Data

Human input becomes an explicit optimizer input rather than an informal post-processing step.

Examples:

- locked player IDs;
- excluded player IDs;
- injury/status overrides;
- strategy selection;
- optional risk preferences.

The optimizer must treat these as constraints without modifying the underlying ML projection.

## Current Feasibility Assessment

### Strongly Supported

- historical player-week records;
- player identity/team/position;
- core passing/rushing/receiving production;
- targets and carries;
- rolling historical features;
- fantasy-point target construction;
- baseline and classical ML regression experiments.

### Requires New DFS Integration

- real weekly DraftKings salaries/slates;
- real weekly FanDuel salaries/slates;
- platform scoring configuration;
- roster/salary constraints;
- lineup optimization;
- human lock/exclude controls.

### Optional or Requires Further Validation

- official injury and participation data;
- depth charts;
- snap share / route participation;
- weather;
- betting/game-environment features.

These optional inputs are not required for the MVP and should not block the Capstone if they prove unreliable.

## Architecture Constraint

This DFS data work is additive.

It must not change the authoritative season-long ranking order, draft state, waiver workflows, or weekly lineup behavior in GridironGPT Core unless a separate tested change is intentionally approved.
