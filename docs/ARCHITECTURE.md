# Architecture

## System Boundary

GridironGPT owns provider integration, ingestion scheduling, application composition, and user-facing views. Gridiron Cortex owns intelligence processing, deduplication, scoring, recommendations, explanations, persistence, and replay.

## Ingestion Pipeline

1. Scheduled runner invokes configured providers.
2. Provider adapters retrieve source records.
3. Player resolution maps article text to NFL entities.
4. Records are normalized into RawEvents.
5. Ingestion forwards each event to the configured Cortex processor.
6. Cortex fingerprints the event and rejects previously processed evidence.
7. New evidence moves through entity resolution, signal processing, relationship propagation, scoring, recommendation, and explanation stages.
8. Cortex state and event-bus history are persisted for restart recovery and replay.
9. Ingestion-run diagnostics are persisted independently for operational observability.

## Failure Model

Provider retrieval uses bounded attempts and timeout handling. Provider failures are isolated so healthy providers can continue. Downstream processor failures are fail-open from the ingestion perspective and are recorded as processor failures rather than causing provider refetches.

## Deduplication Contract

Ingestion may normalize the same source evidence on successive scheduled runs. Cortex remains the authority for determining whether evidence is new. Ingestion captures the Cortex result and reports accepted events separately from duplicates ignored.

## Performance

RSS retrieval uses an explicit HTTP timeout before feed parsing. Player alias resolution caches the ordered alias catalog and performs a cheap literal pre-check before regex boundary matching. On the 2026-08-10 ESPN feed, player-resolution time improved from approximately 20.6 seconds to 0.22 seconds while preserving the test baseline.

## Persistence

Cortex data-directory persistence supports event history, score state, and replay across application restarts. Ingestion run history is persisted separately and feeds the Streamlit Ingestion Status view.