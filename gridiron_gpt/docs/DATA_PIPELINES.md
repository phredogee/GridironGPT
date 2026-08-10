# Data Pipelines

## Purpose

This document tracks the external data sources that feed GridironGPT and Gridiron Cortex.

Each pipeline should:

* retrieve data from one external source;
* normalize source-specific fields;
* preserve source metadata;
* avoid duplicate records;
* emit data in a format that downstream Cortex components can process;
* fail safely when the source is unavailable.

---

## Pipeline Architecture

```text
External Source
      ↓
Source Adapter
      ↓
Normalizer
      ↓
Deduplication
      ↓
Event or Signal Factory
      ↓
Gridiron Cortex
      ↓
Persistence
```

Source adapters should remain independent from scoring logic.

The adapter is responsible for retrieving and cleaning source data. The signal factory is responsible for deciding whether the data represents a meaningful fantasy-football change.

---

## Active Pipelines

| Pipeline             | Type            | Status | Primary Purpose                                  |
| -------------------- | --------------- | -----: | ------------------------------------------------ |
| ESPN NFL RSS         | News            | Active | General NFL news and player updates              |
| NBC ProFootballTalk  | News            | Active | NFL news, transactions, injuries, and commentary |
| RotoWire NFL         | Fantasy news    | Active | Player-specific fantasy updates                  |
| nflreadpy / nflverse | Structured data | Active | Players, rosters, and weekly statistics          |

---

# RSS News Pipeline

## Sources

```text
ESPN NFL RSS
NBC ProFootballTalk
RotoWire NFL
```

## Entry Points

```text
gridiron_gpt/data_ingest/rss_news_fetcher.py
gridiron_gpt/pipelines/cortex_rss_pipeline.py
```

## Processing Flow

```text
RSS feed
   ↓
fetch_rss_news()
   ↓
Headline and summary extraction
   ↓
Player matching
   ↓
Unmatched-item handling
   ↓
Cortex event processing
```

## Configuration

RSS feeds are configured through:

```env
GRIDIRON_RSS_FEEDS="Source Name|https://feed-url,Second Source|https://feed-url"
```

The legacy single-feed configuration remains available as a fallback:

```env
GRIDIRON_RSS_URL="https://feed-url"
GRIDIRON_RSS_SOURCE="Source Name"
```

When `GRIDIRON_RSS_FEEDS` is defined, it takes priority.

## Current Matching Rules

The player matcher supports:

* exact full names;
* first initial and surname;
* position and surname;
* manually configured aliases;
* optional team and position hints.

Surname-only matching is intentionally disabled because it produced false positives such as:

```text
Hall of Fame → Breece Hall
would likely → Isaiah Likely
Jackson → multiple unrelated players
```

## Unmatched Items

Articles without a high-confidence player match are written to:

```text
data/cortex/unmatched_news.jsonl
```

Unmatched records should be reviewed periodically to identify:

* missing aliases;
* incomplete player catalog records;
* team-only stories;
* multi-player headlines;
* non-fantasy-relevant articles.

## RSS Pipeline Limitations

* Some headlines reference players only by surname.
* Some stories affect several players.
* Some sources include opinion-heavy content.
* Duplicate stories may appear across feeds.
* Feed availability and article formatting may change.

---

# nflreadpy / nflverse Pipeline

## Purpose

The nflverse pipeline supplies structured NFL information that complements news-based signals.

Current datasets include:

* player identities;
* seasonal rosters;
* weekly player statistics.

## Entry Points

```text
gridiron_gpt/data_ingest/nflreadpy_adapter.py
gridiron_gpt/data_ingest/nflverse_normalizer.py
gridiron_gpt/intelligence/nflverse_signal_factory.py
```

## Processing Flow

```text
nflreadpy
    ↓
Raw Polars DataFrames
    ↓
Python record conversion
    ↓
nflverse normalization
    ↓
Weekly record comparison
    ↓
Opportunity and production signals
```

## Current Snapshot Volume

A 2025 snapshot produced approximately:

```text
Players:               25,033
Roster records:         3,137
Weekly stat records:   19,421
```

Counts may change when nflverse datasets are updated.

## Adapter Responsibilities

The adapter:

* calls nflreadpy loaders;
* converts Polars rows into Python dictionaries;
* converts dates and other values into JSON-safe formats;
* groups datasets into one season snapshot;
* reports record counts.

The adapter does not assign fantasy impact scores.

## Normalizer Responsibilities

The normalizer converts source-specific rows into stable internal records.

Example roster record:

```python
{
    "source": "nflverse",
    "event_type": "roster_snapshot",
    "player_id": "00-0033873",
    "player_name": "Patrick Mahomes",
    "team": "KC",
    "position": "QB",
    "season": 2025,
    "status": "ACT",
    "metadata": {...},
}
```

Example weekly-stat record:

```python
{
    "source": "nflverse",
    "event_type": "weekly_player_stats",
    "player_id": "00-0033873",
    "player_name": "Patrick Mahomes",
    "team": "KC",
    "position": "QB",
    "season": 2025,
    "week": 1,
    "statistics": {...},
    "metadata": {...},
}
```

## Current Signal Types

The weekly signal factory currently emits two broad categories.

### Opportunity Signals

These measure changes in player usage.

Current metrics:

* targets;
* carries.

Opportunity signals receive higher confidence because usage is generally more predictive than one-game production.

### Production Signals

These measure changes in statistical output.

Current metrics:

* receptions;
* passing yards;
* rushing yards;
* receiving yards;
* passing touchdowns;
* rushing touchdowns;
* receiving touchdowns.

Production signals receive lower confidence because weekly output is volatile.

## Signal Thresholds

Signals are emitted only when a metric changes by more than its configured minimum threshold.

Examples:

```text
Targets: minimum change of 3
Carries: minimum change of 4
Passing yards: minimum change of 100
Rushing yards: minimum change of 40
Receiving yards: minimum change of 40
```

Thresholds are currently global and will later become position-specific.

## Week Comparison Rules

The signal factory:

* groups records by player;
* sorts records by season and week;
* does not compare records across seasons;
* ignores invalid or reversed week order;
* skips large gaps between appearances;
* generates one signal per qualifying metric change.

## Current Confidence Model

```text
Opportunity signal confidence: 0.92
Production signal confidence:  0.72
```

These values are heuristic and are not yet based on historical predictive accuracy.

## Current nflverse Limitations

* Comparisons are based on recent appearances rather than rolling baselines.
* Bye weeks and missed games require careful handling.
* Single-game production can still be noisy.
* Opponent quality is not considered.
* Game scripts are not considered.
* Position-specific expectations are not yet applied.
* Signals are not yet automatically converted into Cortex `RawEvent` objects.

---

# Planned Pipelines

## Sleeper

Purpose:

* fantasy player identifiers;
* league rosters;
* transactions;
* ownership and availability data;
* fantasy-specific metadata.

Planned status:

```text
Not started
```

---

## NFL Injuries and Participation

Purpose:

* official injury status;
* practice participation;
* inactive lists;
* injured reserve movement;
* return-to-play progression.

Potential sources:

* nflverse injuries;
* official team injury reports;
* official NFL transaction feeds.

Planned status:

```text
Not started
```

---

## Depth Charts

Purpose:

* starter changes;
* positional competition;
* promotions and demotions;
* opportunity propagation.

Potential sources:

* nflverse depth charts;
* team depth charts;
* fantasy data providers.

Planned status:

```text
Not started
```

---

## NFL Draft

Purpose:

* prospect identities;
* combine results;
* draft capital;
* landing spots;
* rookie depth-chart competition;
* veteran opportunity impact.

Potential sources:

* nflverse draft picks;
* nflverse combine data;
* manually curated prospect rankings.

Planned status:

```text
Not started
```

---

## Transactions

Purpose:

* signings;
* trades;
* releases;
* waivers;
* practice-squad movement;
* suspensions.

Planned status:

```text
Not started
```

---

## Team and Beat-Writer Feeds

Purpose:

* training-camp observations;
* first-team repetitions;
* role changes;
* coaching comments;
* local injury reporting.

Risks:

* source reliability;
* duplicated reporting;
* speculative language;
* inconsistent formatting.

Planned status:

```text
Future
```

---

# Planned Signal Improvements

## Rolling Baselines

Replace simple week-to-week comparisons with:

* three-game rolling averages;
* seasonal averages;
* recent trend weighting;
* position-specific baselines.

Example:

```text
Targets were 38% above the player's recent three-game average.
```

## Multi-Source Evidence Fusion

Combine independent evidence from multiple sources.

Example:

```text
ESPN:
Player expected to start.

NBC:
Coaches praised increased workload.

nflverse:
Snap share increased from 42% to 71%.
```

Combined output:

```text
Opportunity increased
Confidence: high
Evidence sources: 3
```

## Source Reliability

Each source should eventually receive:

* trust score;
* historical accuracy;
* recency weight;
* duplication penalty;
* primary-source bonus.

## Position-Specific Rules

Examples:

* quarterback passing-volume rules;
* running back carry and target rules;
* wide receiver target-share rules;
* tight end route and target rules;
* defensive player participation rules.

---

# Pipeline Operational Requirements

Every pipeline should support:

* retry with backoff;
* request timeout;
* local caching where appropriate;
* clear error reporting;
* dry-run mode where practical;
* source-level metrics;
* deterministic tests without live network calls;
* duplicate protection;
* audit-friendly stored metadata.

---

# Testing

Current pipeline coverage includes:

```text
RSS player matching
RSS event processing
ESPN dry-run pipeline
nflreadpy adapter
nflverse normalization
nflverse weekly signal generation
Cortex event pipeline
Cortex engine pipeline
```

Current project status:

```text
99 automated tests passing
```

The full suite is run with:

```bash
pytest -q
```

Focused nflverse tests:

```bash
pytest -q \
  tests/test_nflreadpy_adapter.py \
  tests/test_nflverse_normalizer.py \
  tests/test_nflverse_signal_factory.py
```

Focused RSS and Cortex tests:

```bash
pytest -q \
  tests/test_rss_player_matching.py \
  tests/test_event_pipeline.py \
  tests/test_engine_pipeline.py
```

---

# Extension Checklist

When adding a new pipeline:

1. Create a source adapter.
2. Add environment or configuration support.
3. Convert source data into JSON-safe records.
4. Add a normalizer.
5. Define duplicate behavior.
6. Define whether records are events, snapshots, or evidence.
7. Add signal-generation rules only when meaningful.
8. Preserve source metadata.
9. Add mocked unit tests.
10. Run the complete test suite.
11. Update this document.
12. Update `CHANGELOG.md`, `ARCHITECTURE.md`, `ROADMAP.md`, and `KNOWN_ISSUES.md`.
