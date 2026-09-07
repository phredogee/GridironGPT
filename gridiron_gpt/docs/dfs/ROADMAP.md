# GridironGPT DFS Roadmap

## Phase 1 — Project Proposal

- Finalize project scope and research question
- Document existing GridironGPT vs. new Capstone work
- Finalize technical framework
- Define prediction target and candidate feature families
- Define human-in-the-loop placement
- Define success metrics
- Define risks, mitigations, and ethics
- Submit Capstone proposal presentation

## Phase 2 — Data Foundation

- Inventory existing GridironGPT APIs and reusable data
- Identify DFS-specific data gaps
- Implement DraftKings/FanDuel slate import/provider boundary
- Build canonical player identity mapping for DFS joins
- Construct historical player-week dataset
- Enforce pre-kickoff feature cutoffs to prevent leakage
- Perform EDA and data-quality analysis
- Engineer initial feature set
- Establish chronological train/validation/test splits

### Exit criteria

- Reproducible historical dataset
- Documented feature definitions
- Verified no known post-kickoff leakage
- Baseline dataset statistics and EDA complete

## Phase 3 — Model Development

- Implement simple recent-performance baseline
- Train initial linear/regularized model
- Train tree-based candidate model(s)
- Tune candidate models
- Compare MAE, RMSE, correlation, and baseline improvement
- Perform error analysis by position/context
- Select production candidate for DFS integration
- Document model limitations and uncertainty

### Exit criteria

- Reproducible trained-model pipeline
- Evaluation report
- Selected candidate model justified by measured results

## Phase 4 — DFS Integration

- Implement normalized DFS platform models
- Implement DraftKings rules/config adapter
- Implement FanDuel rules/config adapter
- Implement player value analysis
- Implement human review controls
  - lock player
  - exclude player
  - late-status review
  - supported strategy/preference selection
- Implement constrained lineup optimizer
- Validate legal-lineup generation
- Integrate DFS flow into GridironGPT without modifying season-long ranking behavior
- Add unit/integration/system tests

### Exit criteria

- Working DraftKings and FanDuel MVP flows
- Human-in-the-loop before and after optimization
- Valid optimized lineup output
- Existing season-long regression suite remains healthy

## Phase 5 — Evaluation and Delivery

- Historical DFS backtesting
- Live 2026 weekly validation using predictions saved before kickoff
- Compare model/optimizer results with baseline strategies
- Final error and failure analysis
- Complete technical and user documentation
- Prepare live demonstration
- Prepare final Capstone report and presentation

## Stretch Goals

Only pursue after MVP exit criteria are met:

- Floor/ceiling estimates
- Prediction intervals or calibrated uncertainty
- Multiple lineup generation
- Exposure limits
- Cash/tournament objective profiles
- QB/pass-catcher and game-stack correlation logic
- Ownership/leverage modeling
- Additional DFS contest formats
