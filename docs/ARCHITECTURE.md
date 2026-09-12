# Architecture

## System Boundary

GridironGPT owns provider integration, ingestion scheduling, football-specific structured state, fantasy ranking/draft policy, application composition, and user-facing views. Gridiron Cortex owns intelligence processing, deduplication, scoring, recommendations, explanations, persistence, evidence trails, and replay.

Football-specific facts and draft policy remain outside the reusable Cortex core until application composition supplies them through explicit services.

## Existing Season-Long Architecture

The existing system maintains separate news-ingestion, structured football-state, ranking, and draft-decision paths. Production ranking value remains authoritative; advisory layers such as roster need and position scarcity must not silently mutate that value.

## Capstone DFS Architecture

The DFS Capstone is an isolated extension of GridironGPT. It reuses appropriate existing NFL identity and football-data foundations while introducing a new player-week ML pipeline, DFS platform adapters, value analysis, human review, and constrained optimization.

```text
Historical + Current NFL Data
          |
          v
Player-Week Dataset
          |
          v
Data Preparation / Feature Engineering
          |
          v
Baseline + ML Projection Models
          |
          v
Predicted Fantasy Points
          |
          v
DFS Value Layer
  |- projection
  |- salary
  |- platform scoring
  `- slate context
          |
          v
+---------------------------+
|       HUMAN REVIEW        |
| review projection/context |
| lock players              |
| exclude players           |
| consider late information |
| set strategy/preferences  |
+-------------+-------------+
              |
              v
Constrained Lineup Optimizer
  |- salary cap
  |- roster requirements
  |- position eligibility
  |- FLEX rules
  |- platform rules
  `- human constraints
              |
              v
Candidate Optimized Lineup(s)
              |
              v
+---------------------------+
|      HUMAN DECISION       |
| accept / modify / reject  |
+---------------------------+
```

### ML Boundary

One training observation represents one NFL player in one game/week. The primary target is actual fantasy-point production. Inputs may include historical performance, rolling form, usage, team context, matchup, game context, injury/status information when reliably available, and position. Only information available before kickoff may be used as a feature.

The initial baseline is recent rolling fantasy-point performance. Candidate models are linear regression, random forest regression, and gradient-boosted regression. Train, validation, and test partitions are chronological to reduce leakage and better represent real forecasting conditions.

### DFS Platform Boundary

Football-performance prediction and DFS platform rules are separate concerns. DraftKings and FanDuel adapters will supply salary, slate, scoring, roster, and eligibility constraints. This separation allows the football projection layer to remain reusable while platform-specific scoring and optimization rules vary independently.

### Human-in-the-Loop Boundary

Human control exists at two explicit gates. Before optimization, the user reviews projections and current information and may lock or exclude players or establish strategy constraints. After optimization, the system presents candidate lineups for human acceptance, modification, or rejection. No contest entry is automated.

### Optimization Objective

For an eligible player set, the optimizer seeks a legal lineup that maximizes projected fantasy production subject to platform and human constraints. Conceptually:

```text
maximize sum(P_i * x_i)
```

where `P_i` is the projected fantasy-point value for player `i` and `x_i` is 1 when the player is selected and 0 otherwise. Salary caps, roster composition, position/FLEX eligibility, platform rules, and user locks/exclusions constrain the solution.

## Failure and Safety Model

DFS data providers and salary imports must be replaceable through explicit adapters. Missing optional injury or contextual data should degrade gracefully rather than invalidate the full pipeline. Player identity mapping must use canonical IDs where possible. Feature construction must preserve chronological integrity.

DFS work must not modify authoritative season-long rankings, draft state, waiver logic, or weekly lineup behavior. Integration will be regression-tested so the Capstone module remains additive.

## Performance and Persistence

Historical player-week datasets and derived features should be reproducible from documented inputs. Classical ML models are the initial implementation target to keep compute requirements practical and experiments interpretable. More complex approaches are stretch work only after the baseline, evaluation, optimizer, HITL controls, and platform integration are working.