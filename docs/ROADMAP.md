# Roadmap

## DFS Capstone - Fall 2026

The DFS Capstone is developed on the `dfs-capstone` branch and is intentionally separated from core season-long GridironGPT work. Each phase has an explicit definition of done.

### Phase 1 - Project Proposal

**Milestone:** scope, architecture, technical approach, timeline, success metrics, risks, ethics, and human-in-the-loop design documented and ready for instructor review.

### Phase 2 - Data Foundation

**Milestone:** a reproducible historical player-week dataset is assembled, cleaned, explored, and documented. Pregame feature generation is repeatable and preserves chronological integrity.

Key work:
- Build historical player-week records.
- Validate player identity mapping.
- Perform exploratory data analysis.
- Build rolling and contextual features.
- Establish missing-data handling.
- Verify that no post-kickoff information leaks into features.

### Phase 3A - Baseline

**Milestone:** recent rolling fantasy-point baseline is implemented and evaluated on chronological holdout data.

### Phase 3B - ML Development

**Milestone:** linear regression, random forest regression, and gradient-boosted regression candidates are trained and evaluated using the same chronological framework.

### Phase 3C - Model Selection

**Milestone:** the final projection model is selected and documented using MAE, RMSE, predicted-versus-actual correlation, positional error analysis, and baseline comparison.

### Phase 4A - DFS Platform Integration

**Milestone:** DraftKings and FanDuel salary/slate inputs, scoring rules, roster constraints, and eligibility adapters are operational through permitted data/import workflows.

### Phase 4B - Optimization

**Milestone:** the optimizer generates candidate lineups satisfying 100% of implemented salary, roster, position, FLEX, platform, and user constraints.

### Phase 4C - Human-in-the-Loop Controls

**Milestone:** the user can review projection/value information, lock players, exclude players, account for late information, and set relevant strategy constraints before optimization. Candidate lineups can be accepted, modified, or rejected after optimization.

### Phase 4D - GridironGPT Integration

**Milestone:** DFS functionality operates inside the GridironGPT product boundary without disrupting season-long draft, waiver, ranking, or weekly-lineup functionality.

### Phase 5A - Evaluation

**Milestone:** historical backtesting and live 2026 weekly evaluation are completed and documented, including model errors and comparison with baseline strategies.

### Phase 5B - Final Delivery

**Milestone:** regression testing, documentation, final report, demonstration workflow, and final presentation are complete.

## MVP Priority Order

The minimum viable Capstone is complete only when the reproducible dataset, baseline, selected ML model, DFS platform input, value analysis, HITL controls, legal optimizer, backtesting, and integration are working. Stretch features such as richer uncertainty modeling, individual-stat prediction, additional contextual feeds, and more advanced optimization strategies come only after the MVP.

## Existing GridironGPT Work

Season-long GridironGPT remains an active product outside the Capstone scope. Core improvements may continue independently, but they are not counted as new DFS Capstone development and should not be allowed to create scope creep in the Capstone schedule.