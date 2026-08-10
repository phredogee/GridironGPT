# GridironGPT Known Issues

This file tracks active limitations only. Completed work belongs in `CHANGELOG.md`.

## Historical Calibration

This is the largest remaining intelligence-quality gap. Cortex has not yet been comprehensively replayed against historical NFL seasons to quantify recommendation, prediction, confidence, and propagation accuracy.

Needed work:
- Historical season replay
- Recommendation-vs-outcome measurement
- Source reliability measurement
- Position-specific thresholds
- Signal-category calibration
- Confidence-vs-outcome analysis
- Relationship-propagation effectiveness

## Player and Signal Coverage

The ingestion/runtime pipeline is operational; remaining gaps are mostly interpretation and identity coverage.

- Some headlines contain no resolvable player.
- Rare aliases and deep-roster players can still be missed.
- Some stories remain `unknown_impact` because deterministic classification is intentionally conservative.
- Structured injury, transaction, practice, snap, route, and red-zone evidence can be expanded.

These are intelligence-quality limitations, not failures of the automatic ingestion → Cortex handoff.

## Advisor Intent Coverage

Advisor behavior is strongest for questions that clearly identify players. Broader fantasy intent still needs richer routing and context.

Examples needing continued improvement:
- start/sit questions
- waiver prioritization
- multi-player comparisons
- trade evaluation
- DST streaming
- roster-aware recommendations

Some presentation profiles are still derived from the scored-player evidence map rather than consuming every Cortex scorecard dimension directly.

## Dual Presentation / Cortex Scoring Paths

Some existing Streamlit product surfaces still consume the established `data_ingest.player_scores` scored-player map while Cortex owns the newer persistent multidimensional intelligence model.

This is intentional for v1.0 compatibility, but post-v1 work should reduce duplicated concepts and move presentation toward engine-owned scorecards where practical. Presentation code must not become an independent reasoning engine.

## Knowledge Graph UI

The graph viewer is operational as a first pass, but dense relationship sets can still become visually difficult to inspect.

Future improvements:
- stronger filtering by relationship type
- evidence-path inspection
- historical relationship changes
- improved navigation for large neighborhoods
- additional layout controls

## Commissioner Analytics

The Commissioner Suite supports league settings, scheduling, balancing, alternatives, rivalry constraints, playoff brackets, draft workflows, exports, and league history. Deeper visual analytics remain post-v1 work, including schedule fairness, strength of schedule, Luck Index, and historical team-performance analysis.

## Persistence / Scalability

Cortex core state uses repository-backed local JSON/JSONL implementations while parts of the live article/signal path can use Supabase. This is suitable for current local development and v1 architecture validation but is not the final scale-out persistence design.

Long-term needs:
- production database strategy
- transactional writes where required
- efficient historical queries
- concurrent/background processing
- repository migration tooling
- retention and backup policies

## Multi-process / Multi-user Runtime

The Streamlit application shares one Cortex facade per session, which is correct for the current application model. A future multi-worker or multi-user deployment will need explicit coordination around shared persistent state, concurrent writes, caching, and background ingestion.

## Provider Reliability

Provider isolation, retry/backoff, fail-open downstream processing, and ingestion observability exist. Live providers can still experience network, schema, rate-limit, or upstream availability changes outside GridironGPT's control.

Provider health should eventually be durable across processes and surfaced with production alerting.

## Deployment

The local runtime architecture is validated, but production deployment is not yet the v1.0 acceptance target. Authentication, background scheduling, worker topology, secrets management, monitoring, backups, and deployment automation remain productionization work.

## Branch Reconciliation

`refactor/extract-cortex` contains the current architecture. `main` has a small set of later README-only commits that are not yet reconciled with the branch. Those documentation changes should be reviewed during release preparation rather than merged blindly because they predate the final Cortex architecture.

## Current Regression Baseline

```text
702 passed
```

This is the verified regression boundary entering final v1.0 stabilization.
