# Roadmap

## v1.1 - Continuous Intelligence

### Completed
- Runtime scheduled ingestion composition.
- ESPN NFL and RotoWire NFL provider integration.
- Provider retry/timeout/fail-open behavior.
- Player-resolution performance optimization.
- Persistent ingestion-run observability.
- Cortex accepted-versus-duplicate metrics.
- Daily GitHub Actions production ingestion with Supabase run persistence.
- Persistent 2026 canonical player/roster state.
- Persistent 2026 canonical schedule/game state.
- Availability classification.
- Next-game, opponent/location, and bye-week schedule context.
- Stable GSIS identity propagation through Cortex entity resolution.
- FootballContextService integration into production CortexFacade.
- Factual football context in explanations.
- End-to-end facade integration coverage for football context.
- RankingService repository-read fix and basic overall/position ranking validation.
- Multi-signal event classification while preserving the legacy single-best classification contract.
- Compound event evidence retained on one Signal rather than multiplied into several scored Signals.
- Context-aware relationship propagation driven by structured football classifications.
- Regression guards preventing classification count from inflating direct player impact.
- Compound football developments surfaced in explanations/evidence chains.
- Live ESPN/RotoWire camp-news audit using persisted Cortex events and canonical events.
- Production-derived taxonomy coverage for season-ending injuries, team-drill returns, walkthrough participation, and QB competitions.
- Generic absence disambiguation so `won't play` does not automatically imply an injury.
- Full regression baseline advanced to 915 passing tests.

### Next - Camp and News Signal Quality
- Continue auditing live provider output for role changes, depth-chart movement, coach comments, camp performance, and preseason usage.
- Distinguish event subject from related/affected players when one article resolves to multiple entities.
- Reconcile overlapping language/rule vocabularies so football concepts and event taxonomy do not drift independently.
- Improve role/opportunity interpretation for camp battles and depth-chart changes beyond QB-specific competition language.
- Add explicit low-value/editorial story suppression where feature or analytics articles should not influence fantasy scoring.
- Evaluate source quality and distinctiveness before adding additional providers.
- Feed richer structured developments into explanations and relationship context without weakening deduplication or score-safety guarantees.

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
- Let the production collector continue accumulating meaningful historical evidence.
- Review scorecard behavior against multi-day real-world evidence.
- Run combined ingestion + football-state refresh + Cortex validation.
- Evaluate provider freshness, source quality, and evidence overlap.
- Add operational safeguards for long-running history growth and log/data retention.
- Continue regression-testing multi-signal classification against real camp/news phrasing.

## Later
- Add richer official/current injury state when reliable 2026 structured data becomes available.
- Add deeper depth-chart and role history.
- Add player production, projections, and statistical baselines.
- Add matchup-strength and schedule-quality adjustments where they are demonstrably useful.
- Expand provider coverage where sources add distinct value rather than duplicate volume.
- Improve historical/trend views using accumulated Cortex state.
- Strengthen deployment strategy beyond a workstation-dependent scheduler.
- Continue extracting reusable intelligence-engine capabilities from football-specific application concerns.