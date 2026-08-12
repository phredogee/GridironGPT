# Roadmap

## v1.1 - Continuous Intelligence

### Completed
- Runtime scheduled ingestion composition.
- ESPN NFL and RotoWire NFL provider integration.
- Provider retry/timeout/fail-open behavior.
- Player-resolution performance optimization.
- Persistent ingestion-run observability.
- Cortex accepted-versus-duplicate metrics.
- Hourly local ingestion schedule.
- Persistent 2026 canonical player/roster state.
- Persistent 2026 canonical schedule/game state.
- Availability classification.
- Next-game, opponent/location, and bye-week schedule context.
- Stable GSIS identity propagation through Cortex entity resolution.
- FootballContextService integration into production CortexFacade.
- Factual football context in explanations.
- End-to-end facade integration coverage for football context.
- RankingService repository-read fix and basic overall/position ranking validation.

### Next - Fantasy Ranking Score
- Define a dedicated fantasy-ranking model separate from Cortex `overall_score`.
- Establish baseline fantasy value for the relevant draftable player population.
- Define weighted ranking inputs and explicit provenance for each component.
- Incorporate roster role and availability without allowing temporary news volume to dominate baseline player value.
- Incorporate Cortex momentum/trend as an adjustment rather than the entire ranking score.
- Produce trustworthy overall and QB/RB/WR/TE lists.
- Add ranking explanations showing why a player moved and which inputs contributed.
- Add regression fixtures with known ordering expectations.

### v1.1 Stabilization
- Let the production-like local collector continue accumulating meaningful historical evidence.
- Review scorecard behavior against multi-day real-world evidence.
- Run combined ingestion + football-state refresh + Cortex validation.
- Evaluate provider freshness, source quality, and evidence overlap.
- Add operational safeguards for long-running history growth and log/data retention.

## Later
- Add richer official/current injury state when reliable 2026 structured data becomes available.
- Add depth-chart and role history.
- Add player production, projections, and statistical baselines.
- Add matchup-strength and schedule-quality adjustments where they are demonstrably useful.
- Expand provider coverage where sources add distinct value rather than duplicate volume.
- Improve historical/trend views using accumulated Cortex state.
- Strengthen deployment strategy beyond a workstation-dependent scheduler.
- Continue extracting reusable intelligence-engine capabilities from football-specific application concerns.