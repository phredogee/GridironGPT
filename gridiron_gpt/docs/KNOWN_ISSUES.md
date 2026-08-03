# GridironGPT Known Issues

This file tracks active limitations only. Completed work belongs in the changelog.

## Live Ingestion Coverage

Live multi-source ingestion is operational and duplicate-safe. Current gaps are primarily classification/coverage issues rather than pipeline failures.

- Some headlines contain no resolvable player.
- Rare aliases and deep-roster players can still be missed.
- Some resolved stories remain `unknown_impact` because the deterministic vocabulary is intentionally conservative.
- Additional structured injury, transaction, practice, snap, route, and red-zone evidence would improve context.

## Signal / Confidence Calibration

Scoring and confidence are deterministic and explainable, but they have not yet been comprehensively calibrated against historical fantasy outcomes.

Needed work:
- Historical replay
- Source reliability measurement
- Position-specific thresholds
- Signal-category calibration
- Confidence-vs-outcome analysis
- Propagation-effectiveness measurement

## Advisor Semantics

Advisor 2.0 now presents live evidence visually, but natural-language intent coverage is still limited.

- Player-name questions are strongest.
- Broad start/sit, waiver, trade, DST, and multi-player comparison questions need richer intent routing.
- Health / Opportunity / Momentum / Risk / Upside bars currently derive from available scored evidence; they should eventually consume the full multidimensional Cortex scorecard directly.

## Dashboard

Dashboard 2.0 uses live scored data for recommendations, team momentum, and position rankings.

Remaining work:
- Latest ingestion/headline activity feed
- Explicit last-refresh timestamp
- Live ingestion health summary
- Remove any remaining development-only status values
- More historical trend visualization as snapshots accumulate

## Cortex Explorer

A unified player dossier does not yet exist. Player intelligence is currently spread across Players, Trends, Trajectory, Advisor, and Inspector views.

Planned consolidation includes recommendation, score history, confidence history, evidence timeline, availability, opportunity, relationships, propagation, and news.

## Knowledge Graph UI

Relationship propagation works in the engine, but there is no full interactive graph explorer yet.

Needed work:
- Expand/collapse relationships
- Relationship type/strength display
- Propagation direction
- Evidence-path inspection
- Player/team navigation

## Commissioner Analytics

The Commissioner Suite supports league settings, schedule generation, balancing, alternatives, rivalry constraints, playoff brackets, draft workflows, exports, and league history.

Visual analytics remain to be added for:
- Schedule fairness
- Home/away balance
- Strength of schedule
- Luck Index
- Historical standings/team performance

## Persistence / Scalability

The project currently mixes Supabase-backed live article/signal persistence with repository-based JSON/JSONL development state.

Long-term work:
- Consolidate production persistence strategy
- Transactional writes where required
- Efficient historical queries
- Concurrent/background processing
- Repository migration without coupling Cortex to a database vendor

## Provider Reliability

Provider isolation, retry/backoff, timeout handling, and observability exist, but network clients can still have provider-specific limitations. Provider health should eventually be durable across processes and exposed in the production dashboard.

## Historical Validation

This remains the largest intelligence-quality gap. Cortex has not yet been comprehensively replayed against historical NFL seasons to quantify recommendation, prediction, confidence, and relationship accuracy.

## Current Regression Baseline

```text
619 passed
```

This baseline should remain green through the UI modernization and Cortex Explorer work.
