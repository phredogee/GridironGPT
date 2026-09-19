# GridironGPT DFS — Phase 2 Data Pipeline

## Purpose

This document defines the data-acquisition and preprocessing plan for Phase 02 of the Capstone project: **Data Pipeline and Exploratory Analysis**.

Phase 2 deliverables are a data report and a reproducible preprocessed dataset suitable for exploratory analysis, baseline modeling, and later ML development.

## Canonical Observation

The core modeling unit is **one NFL player in one game/week**.

Each row should contain identifiers, only pregame-known features, and a postgame target used for training/evaluation.

## Leakage Rule

For a player in Week N, predictive features may use only information that would have been available before that player's Week N kickoff.

Week N outcomes may appear only in the target fields for that observation. Rolling features must therefore be shifted so the current game's results never contribute to its own predictors.

## Verified Core Source

GridironGPT already includes a structured nflverse adapter at:

`gridiron_gpt/gridiron_gpt/data_ingest/nflreadpy_adapter.py`

The adapter uses `nflreadpy` and exposes:

- `load_players()`
- `load_rosters(season)`
- `load_weekly_player_stats(season)`
- `fetch_nflverse_snapshot(season)`

The weekly player-stat source was locally verified for seasons 2020–2025. Every season returned the same 150-column schema.

### Verified historical coverage

| Season | Rows | Columns | Observed week range |
|---|---:|---:|---:|
| 2020 | 17,602 | 150 | 1–21 |
| 2021 | 18,969 | 150 | 1–22 |
| 2022 | 18,831 | 150 | 1–22 |
| 2023 | 18,643 | 150 | 1–22 |
| 2024 | 18,983 | 150 | 1–22 |
| 2025 | 19,422 | 150 | 1–22 |

The observed week range includes postseason records, so the modeling pipeline should filter by `season_type` rather than assume all listed weeks are regular season.

## Verified Weekly-Stat Fields

The nflverse player-week data includes identity, context, offensive production, usage, efficiency, defensive/special-teams statistics, kicking/punting statistics, and fantasy scoring.

Particularly relevant offensive fields include:

- `player_id`
- `player_name`
- `player_display_name`
- `position`
- `position_group`
- `season`
- `week`
- `season_type`
- `game_id`
- `team`
- `opponent_team`
- `attempts`
- `completions`
- `passing_yards`
- `passing_tds`
- `passing_interceptions`
- `passing_air_yards`
- `passing_epa`
- `passing_cpoe`
- `carries`
- `rushing_yards`
- `rushing_tds`
- `rushing_epa`
- `receptions`
- `targets`
- `receiving_yards`
- `receiving_tds`
- `receiving_air_yards`
- `receiving_yards_after_catch`
- `receiving_epa`
- `target_share`
- `air_yards_share`
- `wopr`
- `fantasy_points`
- `fantasy_points_ppr`

## Existing GridironGPT Contextual Assets

The existing daily pipeline separately ingests and persists:

- news
- injuries
- roster moves
- score snapshots / trend signals

These are treated as contextual GridironGPT signals, not as the authoritative historical performance source.

They may later become supplemental pregame features if they can be timestamped and aligned without leakage.

## DFS-Specific Gaps

The Capstone still needs a reproducible permitted method for obtaining or importing:

- DraftKings slate/player salaries
- FanDuel slate/player salaries
- DraftKings scoring and roster constraints
- FanDuel scoring and roster constraints

Injury/availability data will be evaluated for reliability before being made mandatory for the MVP dataset.

Optional/stretch sources include weather, betting/game-environment context, snap share, and depth-chart information.

## Canonical Player-Week Schema

### Identifiers

- `player_id`
- `season`
- `week`
- `season_type`
- `game_id`
- `team`
- `opponent_team`
- `position`

### Pregame feature candidates

Current-game stat fields are raw outcomes and must not be used directly as predictors for that same game. They will be transformed into shifted historical features such as:

- `fantasy_points_lag_1`
- `fantasy_points_roll3`
- `fantasy_points_roll5`
- `targets_roll3`
- `targets_roll5`
- `carries_roll3`
- `carries_roll5`
- `receptions_roll3`
- `passing_yards_roll3`
- `rushing_yards_roll3`
- `receiving_yards_roll3`
- `target_share_roll3`
- `air_yards_share_roll3`
- `wopr_roll3`
- prior-week bye indicator
- opponent/context features
- availability/injury status when reliable

### DFS fields

- `dk_salary`
- `fd_salary`
- platform/slate identifiers as needed

### Targets

The source already provides:

- `fantasy_points`
- `fantasy_points_ppr`

Later platform adapters may derive:

- `dk_fantasy_points`
- `fd_fantasy_points`

## Initial Historical Scope

The initial historical modeling corpus will use **2020–2025** nflverse player-week data.

Regular-season records should be selected using `season_type` rather than a hard-coded week cutoff.

This provides six consecutive seasons with a stable 150-column source schema.

## Proposed Chronological Split

Initial split for Phase 2 / Phase 3:

- **Training:** 2020–2023
- **Validation:** 2024
- **Test:** 2025
- **Live evaluation:** 2026 as the season progresses

This split preserves temporal ordering and leaves the most recent completed season completely unseen during model fitting and tuning.

The exact split can be revised if EDA reveals a strong data-quality reason, but random row-level splitting will not be used.

## Pipeline Design

```text
NFL / DFS Sources
        |
        v
Raw immutable inputs
        |
        v
Regular-season filtering + player identity normalization
        |
        v
Cleaning + quality checks
        |
        v
Canonical player-week table
        |
        v
Shifted / leakage-safe feature engineering
        |
        v
Chronological train / validation / test split
        |
        +--> Exploratory Data Analysis
        |
        +--> Baseline model
        |
        v
Phase 3 ML development
```

## Storage Plan

The pipeline will separate data by processing stage rather than overwrite source data:

```text
data/dfs/
├── raw/          # source snapshots; do not manually modify
├── interim/      # normalized/joined intermediate tables
├── processed/    # ML-ready player-week dataset
└── reports/      # EDA tables/derived outputs if appropriate
```

Large generated datasets should not automatically be committed to Git. Code, schemas, small samples, metadata, and documentation should be versioned; generated data should follow repository size/licensing rules.

## Data Quality Checks

Phase 2 should measure and document:

- duplicate player-week observations
- missing player IDs
- missing/invalid team or position values
- impossible or negative statistics where not valid
- salary missingness
- unmatched player identities across providers
- historical field/schema changes
- regular-season/postseason separation
- missing weeks and bye-week handling
- target missingness
- first-game / insufficient-history handling for rolling features

## Week 4 Definition of Done

Week 4 is complete when:

1. Existing GridironGPT data sources and fields have been audited.
2. Required external/DFS-specific sources are identified.
3. Historical coverage is selected based on verified availability.
4. The canonical player-week schema is refined from actual source fields.
5. Storage locations and source documentation are established.
6. Privacy, licensing/access, and ethical considerations are documented.
7. At least one reproducible acquisition path is demonstrated for the core NFL data.


## Reproducible Player-Week Build

Phase 2 now includes:

`gridiron_gpt/scripts/build_dfs_player_week_dataset.py`

Run from the repository's `gridiron_gpt` directory:

```bash
python scripts/build_dfs_player_week_dataset.py
```

The script:

- loads 2020–2025 player statistics through `nflreadpy`
- filters to `season_type == "REG"`
- preserves all source fields in a raw Parquet snapshot
- writes a smaller canonical player-week Parquet table
- labels rows as train / validation / test by season
- writes a JSON data-quality report with row counts, missingness, week ranges, and duplicate-key checks

Generated outputs are written beneath `data/dfs/` and should be treated as reproducible artifacts rather than hand-edited source files.

## Phase 2 Next Steps

1. Verify regular-season row counts after filtering `season_type`.
2. Inspect player and roster schemas and define the identity join strategy.
3. Implement the first reproducible 2020–2025 raw player-week build.
4. Add leakage-safe lag/rolling feature generation.
5. Inspect injury/availability assets and determine whether they are usable for the MVP.
6. Define the permitted DK/FD salary import strategy.
7. Run initial data-quality checks and begin EDA.
