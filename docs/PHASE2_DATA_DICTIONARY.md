# Phase 2 — DFS Offensive Dataset Data Dictionary

## Dataset

**Submission candidate:** `data/dfs/processed/dfs_offense_player_week_2020_2025_reg.parquet`

This dataset contains regular-season QB, RB, WR, and TE player-week observations for the DFS capstone. It is produced from nflverse player statistics through `nflreadpy`. The processed table contains **35,515 rows and 71 columns**. Historical features are calculated within player and season, with the current game shifted out to reduce target leakage. Cold-start rows are retained and identified by `has_prior_game`.

## Naming Convention for Engineered Features

Eleven historical source variables are transformed using three leakage-safe feature types:

- `_lag1` — value from the player's immediately previous appearance in the same season.
- `_roll3` — mean of up to the player's previous three appearances in the same season.
- `_roll5` — mean of up to the player's previous five appearances in the same season.

The 11 historical source variables are `fantasy_points`, `fantasy_points_ppr`, `targets`, `carries`, `receptions`, `passing_yards`, `rushing_yards`, `receiving_yards`, `target_share`, `air_yards_share`, and `wopr`. This creates **33 engineered lag/rolling columns**.

## Base and Administrative Columns

| Column | Meaning | Role |
|---|---|---|
| `player_id` | Stable player identifier from the source dataset | Identifier |
| `player_name` | Source player name | Identifier/display |
| `player_display_name` | Display-form player name | Display |
| `position` | Player's listed position | Descriptive feature |
| `position_group` | Position grouping; Phase 2 offense table retains QB/RB/WR/TE | Modeling group |
| `season` | NFL season year | Time/index |
| `week` | Regular-season week | Time/index |
| `season_type` | Season type; this table is filtered to `REG` | Filter/context |
| `game_id` | Source game identifier | Identifier |
| `team` | Player's team for the observation | Context |
| `opponent_team` | Opposing team | Context |
| `split` | Chronological modeling split: train, validation, or test | Evaluation control |
| `has_prior_game` | True when a player has a prior appearance in the same season | Cold-start flag |

## Passing Columns

| Column | Meaning |
|---|---|
| `completions` | Completed passes |
| `attempts` | Passing attempts |
| `passing_yards` | Passing yards |
| `passing_tds` | Passing touchdowns |
| `passing_interceptions` | Interceptions thrown |
| `passing_air_yards` | Air yards on pass attempts |
| `passing_epa` | Passing expected points added from the source data |
| `passing_cpoe` | Completion percentage over expected from the source data |

## Rushing Columns

| Column | Meaning |
|---|---|
| `carries` | Rushing attempts |
| `rushing_yards` | Rushing yards |
| `rushing_tds` | Rushing touchdowns |
| `rushing_epa` | Rushing expected points added from the source data |

## Receiving and Usage Columns

| Column | Meaning |
|---|---|
| `receptions` | Receptions |
| `targets` | Receiving targets |
| `receiving_yards` | Receiving yards |
| `receiving_tds` | Receiving touchdowns |
| `receiving_air_yards` | Air yards associated with receiving targets |
| `receiving_yards_after_catch` | Receiving yards after catch |
| `receiving_epa` | Receiving expected points added from the source data |
| `target_share` | Player's share of team receiving targets |
| `air_yards_share` | Player's share of team receiving air yards |
| `wopr` | Weighted Opportunity Rating from the source data |
| `special_teams_tds` | Special-teams touchdowns credited to the player |

## Fantasy-Point Columns

| Column | Meaning | Phase 2 use |
|---|---|---|
| `fantasy_points` | Source fantasy-point total | Historical/statistical field |
| `fantasy_points_ppr` | Source PPR fantasy-point total | **Current Phase 2 prediction target** |

`fantasy_points_ppr` is the current modeling target. Current-game statistical fields must not be used as pregame predictors of that same game's target. The engineered lag/rolling features are the leakage-safe historical versions used for baseline/model development.

## Engineered Historical Columns

For each source variable below, the processed dataset contains `<variable>_lag1`, `<variable>_roll3`, and `<variable>_roll5`.

| Source variable | Historical information represented |
|---|---|
| `fantasy_points` | Recent standard fantasy scoring |
| `fantasy_points_ppr` | Recent PPR fantasy scoring |
| `targets` | Recent receiving-target workload |
| `carries` | Recent rushing workload |
| `receptions` | Recent receiving production/workload |
| `passing_yards` | Recent passing-yard production |
| `rushing_yards` | Recent rushing-yard production |
| `receiving_yards` | Recent receiving-yard production |
| `target_share` | Recent share of team targets |
| `air_yards_share` | Recent share of team air yards |
| `wopr` | Recent weighted receiving opportunity |

Example columns include:

- `fantasy_points_ppr_lag1`
- `fantasy_points_ppr_roll3`
- `fantasy_points_ppr_roll5`
- `targets_lag1`, `targets_roll3`, `targets_roll5`
- `carries_lag1`, `carries_roll3`, `carries_roll5`
- `receptions_lag1`, `receptions_roll3`, `receptions_roll5`

The same three suffixes apply to all 11 historical source variables listed above.

## Feature Engineering Rules

- Features are grouped by `player_id` and `season`.
- Observations are ordered chronologically by player, season, week, and game.
- The current game's value is shifted out before lag/rolling calculations.
- Rolling windows use up to 3 or 5 prior player appearances, rather than treating bye weeks as zero-production games.
- Historical features reset at season boundaries in the current Phase 2 implementation.
- Cold-start observations are retained rather than deleted.
- DST is not represented by individual defensive-player rows and is planned as a separate team-level modeling pipeline.

## Chronological Split

| Split | Seasons | Rows |
|---|---|---:|
| Training | 2020–2023 | 23,472 |
| Validation | 2024 | 5,935 |
| Test | 2025 | 6,108 |

The split preserves time order rather than randomly mixing observations from different seasons. The project reserves 2026 for later live evaluation.

## Quality and Missing-Value Notes

The Week 5 preprocessing audit reported:

- **0** duplicate player-game keys.
- **0** baseline-ready rows missing the 3-game rolling PPR feature.
- **0** NaN/infinite numeric anomalies among engineered lag/rolling features.
- **31,830** baseline-ready rows.
- **3,685** retained cold-start rows.

Null historical values are expected for cold-start observations because those players have no earlier appearance in the same season from which to construct lagged features.

## Submission Note

The Parquet file is the authoritative processed dataset because it preserves data types and null values efficiently. If the course submission system or instructor requires a human-readable format, a CSV export of the same 71-column table can be created for submission without changing the underlying observations or feature definitions.
