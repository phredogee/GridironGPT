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

### Next
- Let the production-like local collector accumulate meaningful historical data.
- Review scorecard behavior against multi-day real-world evidence.
- Expand provider coverage where sources add distinct value rather than duplicate volume.
- Improve historical/trend views using accumulated Cortex state.
- Evaluate provider freshness, source quality, and evidence overlap.
- Add operational safeguards for long-running history growth and log/data retention.

## Later
- Strengthen deployment strategy beyond a workstation-dependent scheduler.
- Continue extracting reusable intelligence-engine capabilities from football-specific application concerns.
- Evaluate richer structured NFL datasets for roster, injury, schedule, and statistical context.