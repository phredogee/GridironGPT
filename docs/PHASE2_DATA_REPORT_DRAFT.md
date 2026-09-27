# Phase 2 Data Pipeline and Exploratory Analysis Report — Draft

**Project:** GridironGPT DFS Capstone  
**Milestone:** Phase 02 — Data Pipeline and Exploratory Analysis  
**Due:** October 3, 2026  
**Deliverable:** Data Report and Preprocessed Dataset

## 1. Project and Data Objective

The DFS extension of GridironGPT is intended to support data-driven daily fantasy football decisions for DraftKings and FanDuel. The prediction component will estimate player fantasy production before a game begins, while a later optimization component will use projections, salary information, and platform roster rules to construct candidate lineups. The human user remains responsible for reviewing the information and making the final lineup decision.

Phase 2 focuses on creating a reproducible historical dataset, cleaning and transforming the data, engineering pregame features, separating development periods chronologically, performing exploratory data analysis, and establishing a simple baseline that later machine-learning models must improve upon.

The initial individual-player modeling scope is QB, RB, WR, and TE. Team defense/special teams (DST) will require a separate team-level treatment and is not represented by individual defensive-player rows in the current modeling table.

## 2. Data Acquisition and Collection

Historical NFL player-week statistics were acquired from **nflverse through the `nflreadpy` Python package**. The Phase 2 historical period covers the 2020 through 2025 NFL regular seasons.

The source extraction produced **107,359 regular-season rows** with **150 source columns**. The pipeline preserves a raw Parquet snapshot before applying player-level cleaning or feature transformations. This makes the workflow reproducible and keeps the original acquired data separate from derived datasets.

The project organizes generated data into four main stages:

- `data/dfs/raw/` — source snapshots before player-level cleaning.
- `data/dfs/interim/` — cleaned canonical player-week records.
- `data/dfs/processed/` — feature-engineered modeling datasets.
- `data/dfs/reports/` — quality audits, statistical summaries, baseline results, and figures.

The primary acquisition and preprocessing entry point is `scripts/build_dfs_player_week_dataset.py`.

### Privacy and Ethical Considerations

The current Phase 2 dataset contains public professional-football performance information rather than private personal records. The project does not use sensitive personal information for the current player-performance baseline. Data-source access and downstream use should continue to follow applicable source and platform terms.

Predictions are treated as estimates rather than guarantees. The system is designed as decision support: it does not automatically enter contests, and the user retains final authority over lineup decisions.

## 3. Data Cleaning and Quality Assessment

The raw regular-season extraction contained **107 rows** without usable player identity/position information. These records were preserved in the raw snapshot but excluded from the canonical player-level modeling dataset because they could not be reliably associated with a selectable DFS player.

After this cleaning step, the canonical table contained **107,252 valid player-week rows**.

The initial DFS offensive population was then limited to the QB, RB, WR, and TE position groups, producing **35,515 player-week observations**:

| Position | Rows |
|---|---:|
| QB | 3,901 |
| RB | 9,755 |
| WR | 14,603 |
| TE | 7,256 |
| **Total** | **35,515** |

A dedicated Week 5 audit verified:

- 0 duplicate player-game keys.
- 0 unexpected missing three-game rolling predictions among baseline-ready rows.
- 0 NaN or infinite engineered numeric values.
- 31,830 baseline-ready observations.
- 3,685 retained cold-start observations.
- Correct chronological split membership.

The automated audit completed with `CHECKS PASSED: True`.

## 4. Feature Engineering and Transformation

The processed player-week dataset contains **71 columns**, including **33 engineered lag/rolling features**. Historical features were created from variables such as fantasy production, targets, carries, receptions, passing yards, rushing yards, receiving yards, target share, air-yards share, and WOPR.

For the initial feature set, lag-1, three-game rolling, and five-game rolling historical values are calculated within player and season. The current game is shifted out before rolling calculations are performed. This prevents the target game's outcome from being included in its own predictors and reduces target leakage.

Bye weeks are not inserted as artificial zero-performance games. Rolling windows operate on previous recorded player appearances. Historical rolling features currently reset at the season boundary.

A `has_prior_game` flag explicitly identifies observations that have usable current-season history. This preserves cold-start records rather than silently removing them from the processed dataset.

## 5. Train, Validation, and Test Strategy

A chronological split was selected instead of a random split so that model development more closely represents prediction of future football seasons from historical seasons.

| Split | Seasons | Rows |
|---|---|---:|
| Training | 2020–2023 | 23,472 |
| Validation | 2024 | 5,935 |
| Test | 2025 | 6,108 |

The 2026 season is reserved for live evaluation as the capstone progresses. Keeping later seasons outside the training period reduces the risk of future-season information leaking into model development.

## 6. Exploratory Data Analysis

### Position-Level Fantasy Production

Mean weekly PPR production differs substantially across the four offensive position groups:

| Position | Mean PPR | Median PPR |
|---|---:|---:|
| QB | 13.80 | 13.82 |
| RB | 7.49 | 4.90 |
| WR | 7.44 | 5.00 |
| TE | 5.55 | 3.60 |

QB has the highest average PPR production. For RB, WR, and TE, the mean is higher than the median, showing that higher-scoring observations in the upper part of the distribution influence the average.

### Workload and Fantasy Production

For RB, WR, and TE, weekly opportunities were defined as **carries + targets**. Historical opportunities show a strong positive association with observed PPR fantasy production.

| Usage measure | Correlation with PPR points |
|---|---:|
| Receptions | 0.7817 |
| Carries + targets | 0.7103 |
| Targets | 0.7052 |
| Carries | 0.3762 |

These correlations describe historical associations and do not establish that workload alone causes fantasy scoring. They do support further use of recent workload and receiving-volume information as candidate predictive features.

Opportunity buckets make the pattern easier to interpret:

| Weekly opportunities | Rows | Mean PPR | Median PPR |
|---|---:|---:|---:|
| 0–2 | 12,164 | 1.56 | 0.50 |
| 3–5 | 7,653 | 5.94 | 5.00 |
| 6–10 | 6,788 | 11.18 | 10.00 |
| 11–15 | 2,591 | 14.81 | 13.10 |
| 16–20 | 1,315 | 15.87 | 14.40 |
| 21+ | 1,103 | 20.25 | 19.30 |

Observed mean production rises from **1.56 PPR points** in the 0–2 opportunity group to **20.25 points** for observations with 21 or more opportunities.

### EDA Visualizations

The reproducible EDA workflow generates the following figures for the final report:

1. PPR fantasy-point distribution by position.
2. Mean PPR points by position.
3. Three-game baseline MAE/RMSE by position.
4. Actual versus predicted PPR points.
5. Weekly opportunities versus PPR production for RB/WR/TE.

The figures are generated under `data/dfs/reports/figures/` by `scripts/run_dfs_phase2_eda.py`.

## 7. Baseline Model

The Phase 2 baseline predicts a player's current PPR fantasy production using the mean of up to the player's previous three appearances in the same season. Because the current observation is shifted out first, the baseline uses only prior performance information.

The baseline can be evaluated on **31,830 observations** with available prior-game history.

| Group | Rows | MAE | RMSE |
|---|---:|---:|---:|
| Overall | 31,830 | 4.87 | 6.86 |
| QB | 3,415 | 6.57 | 8.50 |
| RB | 8,762 | 4.74 | 6.78 |
| WR | 13,173 | 4.96 | 6.97 |
| TE | 6,480 | 3.99 | 5.65 |

The overall baseline therefore establishes approximately **4.87 MAE and 6.86 RMSE** as the initial benchmark for later predictive models.

Across the baseline-ready population, actual and predicted PPR production have a correlation of **0.5832**. The median absolute error is **3.40 points**, and mean signed error is **-0.10 points**, indicating little overall directional bias in the rolling prediction.

QB has the largest absolute error under this simple baseline, while TE has the smallest. These values should not be interpreted as proof that one position is inherently more predictable than another because the scoring scales and distributions differ by position.

## 8. Cold-Start Handling

There are **3,685 observations** without a prior current-season appearance:

| Position | Cold-start rows |
|---|---:|
| QB | 486 |
| RB | 993 |
| WR | 1,430 |
| TE | 776 |

These observations remain in the processed dataset and are explicitly flagged. They are excluded only from the rolling-baseline error calculation because the baseline has no previous current-season performance from which to generate a prediction.

Future modeling can investigate previous-season history, rookie/position priors, roster role, and other pregame context for these cases.

## 9. Limitations

The current Phase 2 dataset has several known limitations:

- The offensive population is based on nflverse position groups rather than historical DraftKings/FanDuel slate eligibility.
- Historical DraftKings and FanDuel salary information has not yet been joined to the player-week table.
- DST requires a separate team-level data pipeline/model.
- Rolling features reset at season boundaries, leaving first appearances as cold starts.
- The initial baseline does not yet account for opponent strength, injuries, projected role changes, salary, weather, or game environment.
- Historical associations found during EDA should not be interpreted as causal relationships.

These limitations are documented rather than hidden and will guide later modeling and integration work.

## 10. Phase 2 Conclusions

Phase 2 established a reproducible historical data pipeline and a validated preprocessed modeling dataset. The workflow progressed from 107,359 raw regular-season observations to a 35,515-row QB/RB/WR/TE modeling population with leakage-safe historical features and chronological train/validation/test splits.

Exploratory analysis found meaningful position-level scoring differences and a strong historical association between workload and PPR fantasy production. The three-game rolling baseline produced an overall MAE of 4.87 and RMSE of 6.86, providing a concrete benchmark for subsequent machine-learning models.

The next phase can use this foundation to train and compare predictive models, evaluate them against the established baseline, incorporate additional pregame context, and eventually connect player projections to platform salary/value analysis and constrained lineup optimization.

## 11. Phase 2 Submission Artifacts

Planned submission package:

- Phase 2 Data Report (final formatted document).
- Preprocessed QB/RB/WR/TE player-week dataset.
- EDA figures embedded in the report.
- Supporting reproducibility scripts and quality reports retained in the GitHub repository.

**Draft status:** Core report narrative and verified quantitative findings are complete. Remaining work is final formatting, figure placement/captions, final dataset packaging, and submission review.
