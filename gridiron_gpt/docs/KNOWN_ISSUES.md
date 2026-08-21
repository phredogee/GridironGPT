# GridironGPT Known Issues

This file tracks active limitations only. Completed work belongs in `CHANGELOG.md`.

## Historical Calibration

This remains the largest intelligence-quality gap. Cortex and the fantasy ranking model have not yet been comprehensively replayed against historical NFL seasons to quantify recommendation, ranking, confidence, propagation, and projection accuracy.

Needed work:
- Historical season replay.
- Ranking-vs-outcome measurement.
- Recommendation-vs-outcome measurement.
- Projection calibration.
- Source reliability measurement.
- Position-specific thresholds.
- Confidence-vs-outcome analysis.
- Relationship-propagation effectiveness.

## Draft Assistant — Advisory Only

The current roster-aware Draft Assistant is intentionally conservative.

Current limitations:
- Roster needs use starter-oriented defaults of QB 1, RB 2, WR 2, TE 1 unless a custom target service is supplied.
- Roster needs do not yet account for league-specific FLEX, superflex, bench, kicker, or DST requirements.
- Roster advice is presentation-only and does not reorder Best Available or Best Value.
- Position scarcity and tier drop-off are not yet included in a unified "Best Fit Right Now" recommendation.
- Draft stage / current pick context is not yet part of roster advice.
- Live draft state is held in Streamlit session state and is not yet a durable multi-session draft repository.

These are deliberate boundaries rather than regressions. The next planned milestone is a tested Best Fit advisory service downstream of production rankings.

## Ranking and Projection Calibration

Projected production is now included in the production ranking model at its configured weight, but that weight still requires outcome-based calibration over a larger historical sample.

The current architecture protects against accidental double-counting: downstream tier, Best Available, Best Value, roster, and presentation layers should consume the production score rather than independently applying projection weight again.

## Player and Signal Coverage

The ingestion/runtime pipeline is operational; remaining gaps are mostly interpretation and identity coverage.

- Some headlines contain no resolvable player.
- Rare aliases and deep-roster players can still be missed.
- Some stories remain `unknown_impact` because deterministic classification is intentionally conservative.
- Structured injury, transaction, practice, snap, route, and red-zone evidence can be expanded.

## Advisor Intent Coverage

General Advisor behavior is strongest for questions that clearly identify players. Broader fantasy intent still needs richer routing and context.

Examples needing continued improvement:
- start/sit questions,
- waiver prioritization,
- multi-player comparisons,
- trade evaluation,
- DST streaming,
- multi-week add/drop recommendations.

The live Draft Assistant now has roster-aware context, but that logic is not yet unified with every natural-language Advisor intent.

## Dual Presentation / Cortex Scoring Paths

Some Streamlit surfaces still consume the established `data_ingest.player_scores` map while Cortex owns the persistent multidimensional intelligence model.

This remains a compatibility concern. Presentation should continue moving toward engine/domain-owned contracts where practical without creating another scoring engine in the UI.

## Knowledge Graph UI

The graph viewer is operational as a first pass, but dense relationship sets can be difficult to inspect.

Future improvements:
- stronger relationship filtering,
- evidence-path inspection,
- historical relationship changes,
- improved large-neighborhood navigation,
- additional layout controls.

## Commissioner Analytics

The Commissioner Suite is operational, but deeper visual analytics remain future work, including schedule fairness, strength of schedule, Luck Index, and richer historical team-performance analysis.

## Persistence / Scalability

Cortex core state uses repository-backed local JSON/JSONL implementations while parts of the live article/signal path can use Supabase. This is appropriate for current development but is not the final scale-out design.

Long-term needs:
- production database strategy,
- transactional writes where required,
- efficient historical queries,
- concurrent/background processing,
- repository migration tooling,
- retention and backup policies.

## Multi-process / Multi-user Runtime

The current Streamlit session model is suitable for local single-user development. A future multi-worker or multi-user deployment will need explicit coordination around shared persistent state, concurrent writes, caching, draft sessions, and background ingestion.

## Provider Reliability

Provider isolation, retry/backoff, fail-open downstream processing, and ingestion observability exist. Live providers can still experience network, schema, rate-limit, or upstream availability changes outside GridironGPT's control.

## Deployment

Production deployment is not yet the current acceptance target. Authentication, background scheduling, worker topology, secrets management, monitoring, backups, and deployment automation remain productionization work.

## Branch / Release Reconciliation

`develop/v1.1` is the current development source of truth. Release preparation still needs a deliberate review of divergence with `main` and any stale experimental branches before merge/tag work. Documentation or code from older branches should not be reintroduced blindly when it conflicts with the current ranking and draft-state architecture.

## Current Regression Baseline

```text
869 passed
```

This is the protected regression boundary for the current roster-aware Draft Assistant architecture.
