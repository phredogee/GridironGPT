# GridironGPT DFS Known Issues

## Open design/data questions

### Weekly DFS salary source

A reliable and permitted method for obtaining current DraftKings and FanDuel NFL slate salaries still needs to be confirmed. The architecture therefore requires a modular provider/import boundary with CSV/manual-import fallback where appropriate.

### Historical DFS salary coverage

Historical salary/slate coverage for backtesting has not yet been finalized. Backtesting scope may depend on what historical salary data can be obtained consistently.

### Platform scoring target

The first ML implementation will target player-week fantasy production, but the final platform-scoring strategy still needs to be finalized during data/model design. The architecture should avoid unnecessarily coupling the core ML model to one DFS platform.

### Feature availability

Candidate feature families are defined, but the exact production feature set depends on the existing GridironGPT data inventory and Phase 2 EDA.

### Player identity reconciliation

DraftKings/FanDuel identifiers may not match existing GridironGPT/NFL provider identifiers. A canonical player-mapping strategy will be required before reliable slate joins.

### Late status changes

Injuries, inactive announcements, and depth-chart changes can occur close to kickoff. The human-review gate and refresh workflow must account for these changes without introducing post-kickoff information into training/evaluation.

## Protection of season-long core

DFS work must not alter authoritative season-long rankings, draft state, waiver logic, or weekly lineup behavior unless a separate tested product decision explicitly promotes shared functionality.
