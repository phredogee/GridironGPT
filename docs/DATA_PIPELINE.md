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

## Initial Data Inventory

### Existing GridironGPT assets

The `dfs-capstone` branch already contains a structured `gridiron_gpt/data/` area, including `clean/`, `injuries/`, `news/`, an ESPN API module, and existing NFL data artifacts. These assets will be audited before adding new collection code.

Previously documented GridironGPT/nflverse work provides a foundation for player identity, roster and weekly football-stat data. Phase 2 will verify actual field availability and historical consistency before those fields are accepted into the modeling dataset.

### DFS-specific gaps

The Capstone still needs a reproducible method for obtaining or importing:

- DraftKings slate/player salaries
- FanDuel slate/player salaries
- DraftKings scoring and roster constraints
- FanDuel scoring and roster constraints

Injury/availability data will be evaluated for reliability before being made mandatory for the MVP dataset.

Optional/stretch sources include weather, betting/game-environment context, snap share, and depth-chart information.

## Proposed Player-Week Schema

### Identifiers

- `player_id`
- `season`
- `week`
- `game_id`
- `team`
- `opponent`
- `position`

### Pregame feature candidates

- rolling fantasy points (3-game and/or 5-game)
- rolling targets
- rolling carries
- rolling receptions
- rolling passing yards
- rolling rushing yards
- rolling receiving yards
- rolling touchdowns
- home/away indicator
- days rest
- previous-week bye indicator
- opponent/context features
- availability/injury status when reliable

### DFS fields

- `dk_salary`
- `fd_salary`
- platform/slate identifiers as needed

### Target

- `actual_fantasy_points`

Platform-specific fantasy-point targets may be added if scoring differences require separate labels.

## Pipeline Design

```text
NFL / DFS Sources
        |
        v
Raw immutable inputs
        |
        v
Player identity normalization
        |
        v
Cleaning + quality checks
        |
        v
Canonical player-week table
        |
        v
Leakage-safe feature engineering
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
- missing weeks and bye-week handling
- target missingness

## Train / Validation / Test Strategy

Splitting will be chronological, not random. Exact season/week boundaries will be chosen after historical coverage is verified.

The test set must represent future observations relative to training data. No preprocessing statistic or rolling feature may use future games.

## Week 4 Definition of Done

Week 4 is complete when:

1. Existing GridironGPT data sources and fields have been audited.
2. Required external/DFS-specific sources are identified.
3. Historical coverage is selected based on verified availability.
4. The canonical player-week schema is refined from actual source fields.
5. Storage locations and source documentation are established.
6. Privacy, licensing/access, and ethical considerations are documented.
7. At least one reproducible acquisition path is demonstrated for the core NFL data.

## Phase 2 Next Steps

1. Locate and inspect the existing nflverse/nflreadpy acquisition code.
2. Verify historical seasons and weekly-stat columns available through that pipeline.
3. Inspect injury/availability assets and determine whether they are usable for the MVP.
4. Define the permitted DK/FD salary import strategy.
5. Lock historical coverage.
6. Implement the first reproducible raw-to-player-week dataset build.
