# GridironGPT DFS Architecture

## Design Goals

- Keep DFS development isolated from season-long GridironGPT behavior.
- Reuse existing provider/data infrastructure where appropriate.
- Keep model prediction, DFS value analysis, optimization, and presentation as separate responsibilities.
- Keep the human in the loop before and after optimization.
- Support DraftKings and FanDuel through platform adapters/configuration rather than hard-coding one provider into the ML layer.
- Prevent temporal data leakage: historical training rows may use only information available before kickoff.

## Technical Framework

```text
Existing GridironGPT Sources      Historical NFL Data      Current DFS Slate
          │                              │                 DK / FD salary
          └──────────────┬───────────────┘                 + eligibility
                         │                                      │
                         ▼                                      │
                DFS Data Preparation  ◄─────────────────────────┘
                         │
                         ▼
                 Feature Engineering
                         │
                         ▼
              ML Player Projection Layer
              baseline → candidate models
                         │
                         ▼
               Predicted Fantasy Points
                         │
                         ▼
                 DFS Value Analysis
            projection + salary + scoring
                         │
                         ▼
                HUMAN REVIEW GATE
           ┌─────────────────────────────┐
           │ review projection/confidence│
           │ lock / exclude players      │
           │ review injuries/late news   │
           │ choose preferences/strategy │
           └──────────────┬──────────────┘
                          ▼
                 Lineup Optimization
           maximize modeled lineup value
                    subject to:
           - salary cap
           - roster positions
           - FLEX eligibility
           - slate eligibility
           - platform rules
           - human constraints
                          │
                          ▼
               Candidate Lineup(s)
                          │
                          ▼
                HUMAN DECISION GATE
                accept / modify / reject
                          │
                          ▼
                    Final Recommendation
```

## Layer 1 — DFS Data

The DFS subsystem may reuse existing GridironGPT provider adapters and normalized football-domain data. New DFS-specific inputs include weekly platform salary/slate data and platform rules.

The DFS layer should normalize platform inputs into a common internal representation rather than leaking DraftKings/FanDuel-specific schemas through the system.

Proposed normalized concepts:

- `DFSPlatform`
- `DFSSlate`
- `DFSPlayerEntry`
- `DFSSalary`
- `DFSScoringRules`
- `DFSRosterRules`

## Layer 2 — Player-Week Training Dataset

The fundamental supervised-learning observation is one player in one historical game/week.

Candidate feature families include:

- Historical fantasy production
- Rolling recent performance
- Usage: targets, carries, snaps, routes when available
- Team offensive context
- Opponent/matchup context
- Home/away and game context
- Injury/status information available before kickoff
- Position and role

The initial target is actual fantasy-point production. Phase 2 exploratory analysis will determine the final feature set.

## Layer 3 — ML Projection

Model development will begin with a transparent baseline and compare candidate regression approaches.

Initial experimental sequence:

```text
recent-performance baseline
        ↓
linear regression / regularized linear model
        ↓
tree-based candidate model(s)
        ↓
model comparison + error analysis
        ↓
selected production candidate
```

Model choice is based on measured validation/test performance rather than model complexity.

Primary evaluation metrics:

- MAE
- RMSE
- Predicted/actual correlation
- Baseline improvement
- Position/context-specific error analysis

## Layer 4 — Platform Scoring and Value

The prediction layer should remain as platform-independent as practical. Platform adapters/configuration apply DraftKings/FanDuel scoring and salary/roster information to derive DFS-specific projections and value.

A simple derived value metric may be reported as projected points per $1,000 of salary, but the optimizer should operate on explicit objective and constraint definitions rather than a single displayed value metric.

## Layer 5 — Human-in-the-Loop

### Pre-optimization gate

The user may:

- Review model projections and uncertainty
- Lock selected players
- Exclude selected players
- Exclude unavailable/questionable players when desired
- Incorporate late injury/inactive information
- Choose supported optimization preferences

These actions become optimizer constraints or objective configuration; they do not mutate the underlying ML prediction.

### Post-optimization gate

Candidate lineups are recommendations. The user retains authority to accept, modify, rerun, or reject them. The system does not automatically enter paid contests.

## Layer 6 — Lineup Optimizer

The MVP optimization objective is to maximize modeled lineup fantasy points subject to legal platform and human constraints.

Conceptually:

```text
maximize Σ(projected_points_i × selected_i)

subject to:
- total salary <= platform salary cap
- platform roster-position counts
- FLEX eligibility
- player/slate eligibility
- lock/exclude constraints
```

The optimizer is intentionally separate from the ML model: ML estimates player outcomes; optimization selects the best legal combination under the selected objective.

## Layer 7 — Recommendation and Evaluation

The recommendation layer should expose:

- Player selections
- Salary used / salary remaining
- Projected lineup points
- Player projections and value
- Human locks/exclusions
- Relevant warnings or uncertainty

Historical backtests and live 2026 predictions will be stored before outcomes are known so evaluation is reproducible and resistant to hindsight bias.

## Isolation from Season-Long Core

DFS services must consume stable GridironGPT interfaces rather than rewriting season-long scoring or draft behavior.

Key invariant:

> DFS experiments must not mutate authoritative season-long ranking scores, Draft Assistant state, waiver workflows, or weekly season-long lineup logic.

Successful DFS components may later be promoted deliberately into shared infrastructure only after testing and explicit approval.
