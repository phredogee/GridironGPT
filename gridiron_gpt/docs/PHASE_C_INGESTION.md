# Phase C — Data Ingestion Architecture

## Purpose

Phase C establishes the boundary between external NFL information and Gridiron Cortex. Providers are responsible for supplying facts; adapters normalize those facts; Cortex owns interpretation and intelligence.

## Current Pipeline

```text
External Provider
      ↓
SourceAdapter
      ↓
SourceRecord
      ↓
EventNormalizer
      ↓
RawEvent
      ↓
EvidenceAggregator
      ↓
CanonicalEventRepository
      ↓
CanonicalEvent
      ↓
Cortex
```

## News Sources

Current named RSS providers:

- ESPN NFL
- RotoWire NFL

RSS records are player-resolved before normalization. One article may emit several player-specific records when multiple players are identified.

### Multi-Player Identity

All player events derived from one article retain shared article provenance, while the event fingerprint includes the player subject.

```text
Article A
├── Player A event → unique fingerprint
├── Player B event → unique fingerprint
└── Player C event → unique fingerprint
```

A repeated fetch of Article A for Player A remains a duplicate.

## Player Resolution

Current matching supports:

- Full catalog names
- Suffixless aliases (`Jr.`, `Sr.`)
- Football-name aliases
- Possessive normalization
- Multi-player headline extraction

Live smoke testing improved resolved NFL-player records from approximately 64% to 76% after alias hardening.

Non-fantasy positions are intentionally retained because defensive and offensive-line evidence may later propagate through Cortex relationships.

## Canonical Evidence

Canonical events are persisted through a repository abstraction.

Properties:

- Restart-safe identity
- Append-only history
- Cross-source corroboration
- Duplicate-evidence suppression
- Source provenance
- Confidence aggregation

The repository, not process-local memory, is authoritative for canonical event state.

## Structured nflverse Statistics

`NFLVersePlayerStatsAdapter` converts weekly nflverse/nflreadpy player statistics into source-neutral records.

Adapters preserve facts and context; they do not make fantasy recommendations.

### Statistical Context

Each weekly player record can contain:

```text
stats
stat_context
team_share_context
```

`stat_context` includes:

- Prior-game count
- Rolling baseline
- Current values
- Deltas
- Touches
- Scrimmage yards

`team_share_context` includes:

- Carry share
- Target share
- Pass-attempt share
- Prior share baseline
- Current share
- Share deltas

## Statistical Interpretation

Structured nflverse events use `StatisticalEventInterpreter` rather than headline sentiment rules.

```text
Structured Stats
      ↓
StatisticalEventInterpreter
      ↓
Base performance impact
+ historical trend adjustment
+ team-share adjustment
      ↓
statistics / performance Signal
```

This prevents words appearing in generated/statistical headlines from accidentally invoking news sentiment logic.

Current weights are deterministic development heuristics. Historical calibration is future work.

## Validation

Focused C3.7 regression gate:

```text
43 passed
```

Coverage includes:

- nflverse adaptation
- structured-stat interpretation
- contextual statistical reasoning
- team opportunity share
- signal-processing regression behavior

## Next Engineering Target — Reliability

The next Phase C subsystem should make provider execution resilient.

Target capabilities:

```text
Provider execution
├── timeout
├── retry
├── exponential backoff
├── rate-limit awareness
├── failure isolation
├── structured result/status
└── health metrics
```

A failure in one provider must not prevent healthy providers from reaching Cortex.

After reliability, ingestion observability should expose provider health, event counts, duplicates, failures, latency, and last-success timestamps.
