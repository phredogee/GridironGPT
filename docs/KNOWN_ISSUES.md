# Known Issues and Risk Register

## DFS Capstone Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| DFS salary/slate data unavailable or changes format | Medium | High | Use modular platform/provider adapters and support permitted CSV/import fallback workflows. |
| NFL data source changes | Medium | Medium | Keep source-specific logic behind adapters and preserve reproducible intermediate datasets. |
| Player identity mismatch across NFL and DFS sources | Medium | High | Use canonical player IDs and explicit identity mapping/validation. |
| Data leakage from future or post-kickoff information | Medium | High | Generate features chronologically and enforce the rule that only information available before kickoff may be used. |
| Model overfitting | Medium | High | Use chronological train/validation/test partitions and compare against a simple baseline. |
| ML models fail to beat the baseline | Medium | Medium | Evaluate multiple candidate models, refine features, and report results transparently rather than assuming ML must win. |
| Late injury/inactive information changes a slate | High | Medium | Refresh available information and require human review before optimization. |
| Scope creep | High | High | Complete MVP milestones before stretch features; keep season-long GridironGPT improvements outside Capstone scope. |
| DFS changes disrupt season-long GridironGPT | Low | High | Isolate development on `dfs-capstone`, preserve system boundaries, and run regression tests before integration. |
| Compute/storage requirements become excessive | Low | Medium | Begin with efficient classical ML, compact player-week datasets, and expand only when justified by measurable benefit. |

## Model and Evaluation Limitations

Fantasy-point outcomes contain substantial variance from injuries, game scripts, coaching decisions, weather, turnovers, and other events that cannot be perfectly predicted. Model output is therefore probabilistic decision support rather than a guarantee.

Evaluation must distinguish model quality from unusual late-breaking events where practical. Error analysis by position and time period will be used to identify systematic weaknesses.

## DFS Data Access

The project does not assume that DraftKings or FanDuel provide a stable public DFS salary API. Platform salary/slate ingestion must use permitted sources or user-provided/platform-provided import files where available. The architecture should not depend on prohibited scraping or automated contest-entry behavior.

## Injury and Context Coverage

Reliable structured injury, participation, depth-chart, snap-share, weather, and game-environment data may not all be available during the MVP. These are optional enrichments unless a reliable source is established. Missing optional context must not prevent the core projection/optimization pipeline from operating.

## Human-in-the-Loop Dependency

Late news can make an otherwise valid optimized lineup undesirable. The system therefore requires an explicit human review gate before optimization and a human decision gate after candidate lineups are produced. Human controls reduce—but do not eliminate—the risk of stale or incomplete information.

## Existing Season-Long Boundaries

DFS development must not silently change authoritative season-long rankings, draft state, waiver logic, or weekly lineup behavior. Shared services must have explicit interfaces and regression coverage before integration.