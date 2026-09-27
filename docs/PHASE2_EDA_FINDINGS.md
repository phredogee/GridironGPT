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

## Usage and Production Patterns

For RB/WR/TE observations, weekly opportunities are defined as **carries + targets**. The pattern analysis found a Pearson correlation of **0.7103** between weekly opportunities and PPR fantasy points. Targets alone correlated **0.7052** with PPR points, carries correlated **0.3762**, and receptions had the strongest measured association at **0.7817**.

These are descriptive associations and should not be interpreted as proof that additional opportunities cause a specific fantasy-point increase. They do, however, support using workload and receiving-usage information as candidate predictive features.

The opportunity buckets show a clear increase in observed fantasy production as weekly workload increases:

| Weekly opportunities | Rows | Mean PPR | Median PPR |
|---|---:|---:|---:|
| 0–2 | 12,164 | 1.56 | 0.50 |
| 3–5 | 7,653 | 5.94 | 5.00 |
| 6–10 | 6,788 | 11.18 | 10.00 |
| 11–15 | 2,591 | 14.81 | 13.10 |
| 16–20 | 1,315 | 15.87 | 14.40 |
| 21+ | 1,103 | 20.25 | 19.30 |

Players with 21 or more carries/targets averaged **20.25 PPR points**, compared with **1.56** for observations with only 0–2 opportunities. This reinforces workload as an important signal to investigate during model development while still recognizing that opportunity and production are jointly influenced by role, game environment, player quality, and other factors.

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

### Additional Baseline Patterns

Across all 31,830 baseline-ready observations, actual and predicted PPR points have a correlation of **0.5832**. The baseline's mean signed error is **-0.0997 points**, so its predictions are close to balanced overall with a small average underprediction. The median absolute error is **3.40 points**.

Position-level actual/predicted correlations were:

- QB: **0.4848**
- RB: **0.5890**
- WR: **0.5340**
- TE: **0.4816**

The median absolute errors were 5.41 for QB, 3.25 for RB, 3.47 for WR, and 2.82 for TE. These results reinforce that the simple rolling baseline behaves differently across positions and provide a useful reason to evaluate later models both overall and by position rather than relying on one aggregate metric.

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

The quantitative pattern analysis now supports interpretation of the usage chart: higher observed workload is strongly associated with higher observed PPR production in this historical dataset, with an opportunity/PPR correlation of 0.7103 and steadily increasing mean PPR scoring across the defined opportunity buckets.

## Current Limitations

- The current individual-player model population is based on nflverse QB/RB/WR/TE position groups, not yet DraftKings/FanDuel slate eligibility.
- DraftKings and FanDuel salary data has not yet been joined to the historical modeling table.
- DST requires a separate team-level dataset/model rather than individual defensive-player rows.
- The baseline excludes cold-start observations from its error calculation because no prior current-season appearance exists.
- The rolling features currently reset at each season boundary; prior-season history is not automatically used for Week 1.
- The current baseline is intentionally simple and does not account for opponent, injuries, salary, projected role changes, or game environment.

## Phase 2 Interpretation

The Phase 2 pipeline has established a reproducible dataset, leakage-safe historical features, a chronological split, a documented cold-start population, descriptive position-level statistics, quantitative workload/production patterns, and a reproducible baseline. The EDA indicates that recent workload deserves meaningful attention in later predictive modeling, while the baseline results establish a concrete benchmark against which future models can be evaluated. These outputs provide the evidence needed for the next modeling phase while satisfying the core statistical-analysis, pattern-identification, visualization, and baseline-model portions of the Phase 2 milestone.
