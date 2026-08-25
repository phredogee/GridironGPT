# Roadmap

## v1.1 - Continuous Intelligence and Draft Decision Support

### Completed
- Runtime scheduled ingestion composition with ESPN NFL and RotoWire NFL.
- Provider retry/timeout/fail-open behavior and persistent ingestion observability.
- Daily GitHub Actions production ingestion with Supabase run persistence.
- Persistent 2026 canonical player/roster and schedule/game state.
- Stable GSIS identity propagation and FootballContextService integration.
- Multi-signal event classification on one Signal without direct-score multiplication.
- Context-aware relationship propagation driven by structured classifications.
- Production-derived taxonomy coverage for camp/news signals.
- Taxonomy integrity guards preventing malformed event rules from reaching production classification.
- Fantasy ranking and Best Fit decision infrastructure.
- Position-scarcity service measuring same-position depth, next-option score drop, and tier cliffs.
- Bounded scarcity integration into Best Fit without mutating production ranking scores.
- Draft Assistant scarcity explanations driven by the current undrafted candidate pool.
- Realistic scarcity scenarios covering position runs, tier cliffs, false urgency, and cost of waiting.
- Full regression baseline advanced to **939 passing tests**.

### Next - Draft Night Readiness
- Exercise the Draft Assistant against realistic full draft boards and live pick sequences.
- Add a concise draft decision summary that combines ranking, roster need, market value, and scarcity without duplicating underlying logic.
- Verify candidate-pool refresh and scarcity recalculation after every recorded pick.
- Improve draft-state ergonomics: drafted-player handling, recommendation refresh, and fast recovery from an incorrect pick entry.
- Add end-to-end Streamlit smoke scenarios for several rounds of a mock draft.
- Keep decision explanations deterministic; use any LLM layer only to explain established signals, not invent ranking/scarcity decisions.
- Freeze risky architecture changes close to the 2026-08-29 draft and prioritize reliability, data freshness, and usability.

### Next - Camp and News Signal Quality
- Continue auditing live provider output for role changes, depth-chart movement, coach comments, camp performance, and preseason usage.
- Distinguish event subject from related/affected players when one article resolves to multiple entities.
- Reconcile overlapping language/rule vocabularies so football concepts and event taxonomy do not drift independently.
- Improve role/opportunity interpretation beyond QB-specific competition language.
- Add explicit low-value/editorial story suppression where feature or analytics articles should not influence fantasy scoring.
- Evaluate source quality and distinctiveness before adding additional providers.

### v1.1 Stabilization
- Continue accumulating meaningful production evidence.
- Review scorecard behavior against multi-day real-world evidence.
- Run combined ingestion + football-state refresh + Cortex validation.
- Evaluate provider freshness, source quality, and evidence overlap.
- Add operational safeguards for history growth and retention.
- Continue regression-testing classification against live camp/news phrasing.

## Later
- Add richer official/current injury state when reliable structured data is available.
- Add deeper depth-chart and role history.
- Add player production, projections, and statistical baselines where they improve the production ranking model.
- Add matchup-strength and schedule-quality adjustments where demonstrably useful.
- Expand provider coverage only where sources add distinct value.
- Improve historical/trend views using accumulated Cortex state.
- Strengthen deployment strategy beyond workstation-dependent components.
- Continue extracting reusable intelligence-engine capabilities from football-specific application concerns.