# Phase 2 — Exploratory Data Analysis Findings

## Purpose

This document records the verified findings from the Phase 2 DFS exploratory analysis. It is intended to support the October 3 Data Report and keep report conclusions tied to reproducible outputs rather than informal observations.

## Dataset Used

The initial individual-player DFS modeling population contains **35,515** regular-season QB/RB/WR/TE player-week observations from 2020–2025.

- QB: 3,901 rows
- RB: 9,755 rows
- WR: 14,603 rows
- TE: 7,256 rows
- Baseline-ready rows with prior current-season history: **31,830**
- Retained cold-start rows: **3,685**

The Week 5 preprocessing audit passed with zero duplicate player-game keys, zero unexpected baseline-feature nulls among baseline-ready rows, and zero NaN/infinite numeric anomalies.

## Descriptive Findings

Mean PPR fantasy production differs by position:

| Position | Rows | Mean PPR | Median PPR | Baseline-ready rows |
|---|---:|---:|---:|---:|
| QB | 3,901 | 13.796 | 13.82 | 3,415 |
| RB | 9,755 | 7.487 | 4.90 | 8,762 |
| WR | 14,603 | 7.436 | 5.00 | 13,173 |
| TE | 7,256 | 5.553 | 3.60 | 6,480 |

QB has the highest average weekly PPR production in this dataset. RB, WR, and TE means exceed their medians, indicating that their scoring distributions are influenced by higher-scoring performances in the upper portion of the distribution. The generated boxplot should be used in the final report to show the distribution visually rather than relying only on averages.

## Baseline Model

The Phase 2 baseline predicts a player's current PPR fantasy points using the mean of up to the player's previous three appearances within the same season. The current game is shifted out before calculation, so the baseline does not use the target game's outcome as a predictor.

### Baseline Results

| Group | Evaluation Rows | MAE | RMSE |
|---|---:|---:|---:|
| ALL | 31,830 | 4.8734 | 6.8582 |
| QB | 3,415 | 6.5669 | 8.4986 |
| RB | 8,762 | 4.7431 | 6.7847 |
| WR | 13,173 | 4.9576 | 6.9720 |
| TE | 6,480 | 3.9861 | 5.6496 |

The overall benchmark for later models is therefore approximately **MAE 4.87 / RMSE 6.86**. A later ML model should be compared against this baseline on the appropriate chronological validation/test population rather than judged only by its standalone error.

QB has the largest baseline error by both MAE and RMSE, while TE has the smallest. This does not by itself prove that QB performance is intrinsically less predictable; it shows that this specific three-game rolling baseline produces larger absolute errors for QBs in the current dataset. Position-specific scoring scale should be considered when interpreting these values.

## Cold-Start Population

There are **3,685** offensive observations without a prior current-season appearance:

- QB: 486
- RB: 993
- WR: 1,430
- TE: 776

These rows are retained and flagged instead of being silently discarded. The current rolling baseline cannot make a history-based prediction for them. Later work can evaluate previous-season history, role/roster context, rookie defaults, position-level priors, or other pregame information as cold-start strategies.

## Chronological Split

The validated Week 5 split is:

- Training: 2020–2023 — **23,472** rows
- Validation: 2024 — **5,935** rows
- Test: 2025 — **6,108** rows
- 2026 is reserved for live evaluation as the season progresses.

This preserves temporal ordering and reduces the risk of future-season information leaking into model development.

## Generated EDA Figures

The EDA script produces:

1. `ppr_distribution_by_position.png` — PPR scoring distribution by QB/RB/WR/TE.
2. `mean_ppr_points_by_position.png` — mean PPR scoring by position.
3. `baseline_error_by_position.png` — MAE and RMSE for the three-game baseline by position.
4. `baseline_actual_vs_predicted.png` — actual versus rolling-baseline predicted PPR scoring.
5. `usage_vs_ppr_points.png` — average PPR scoring versus weekly opportunities (carries + targets) for RB/WR/TE.

The first four figures directly visualize already verified statistics. The usage chart should be interpreted from the generated artifact before making a stronger report claim about the shape or strength of the usage-production relationship.

## Current Limitations

- The current individual-player model population is based on nflverse QB/RB/WR/TE position groups, not yet DraftKings/FanDuel slate eligibility.
- DraftKings and FanDuel salary data has not yet been joined to the historical modeling table.
- DST requires a separate team-level dataset/model rather than individual defensive-player rows.
- The baseline excludes cold-start observations from its error calculation because no prior current-season appearance exists.
- The rolling features currently reset at each season boundary; prior-season history is not automatically used for Week 1.
- The current baseline is intentionally simple and does not account for opponent, injuries, salary, projected role changes, or game environment.

## Phase 2 Interpretation

The Phase 2 pipeline has established a reproducible dataset, leakage-safe historical features, a chronological split, a documented cold-start population, descriptive position-level statistics, and a quantitative baseline. These outputs provide the benchmark and evidence needed for the next modeling phase while also satisfying the core statistical-analysis and baseline-model portions of the Phase 2 milestone.
