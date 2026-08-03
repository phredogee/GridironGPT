# GridironGPT Project Overview

## Vision

GridironGPT is a fantasy-football intelligence and league-management platform powered by **Gridiron Cortex**. It converts live NFL evidence into persistent, explainable player intelligence and combines that intelligence with flexible commissioner, scheduling, draft, and league-history tools.

GridironGPT is the flagship application built on Cortex. Cortex owns reusable reasoning; GridironGPT owns football-domain workflows and presentation.

## Current System

```text
ESPN / NBC / ProFootballTalk / RotoWire / nflverse
                    ↓
             Live Ingestion
                    ↓
       Normalize + Deduplicate
                    ↓
              Supabase
                    ↓
          Gridiron Cortex
                    ↓
 Resolve → Classify → Propagate → Score → Recommend → Explain
                    ↓
         Visualization Models
                    ↓
 Dashboard / Advisor / Players / Commissioner Suite
```

## Major Capabilities

### Live Football Intelligence
- Multi-source RSS ingestion
- Structured nflverse statistical context
- Duplicate-safe persistence
- Player/entity resolution
- Signal classification and scoring
- Relationship-aware propagation
- Confidence and recommendation generation
- Scorecard and momentum history

### Advisor 2.0
- Natural-language player questions
- Recommendation, score, and confidence cards
- Supporting evidence and headlines
- Signal-impact visualization
- Cortex timeline
- Health, opportunity, momentum, risk, and upside profile
- Collapsed developer/reasoning details

### Dashboard 2.0
- Live player and recommendation metrics
- BUY/WATCH/risk candidates
- Recommendation distribution
- Team momentum
- Position rankings
- Cortex-ranked player table

### Commissioner Suite
- Configurable league settings
- Team/division management
- Flexible roster limits
- Schedule generation
- Divisional home/away guarantees
- Cross-division scheduling
- Home/away balancing
- Schedule quality analytics and alternate schedules
- Rivalry constraints
- CSV/iCalendar exports and schedule delivery support
- Playoff bracket generation with configurable playoff weeks
- Draft-room workflows
- League history and commissioner insights

## Persistence

The project uses repository abstractions so storage can evolve without coupling intelligence logic to a specific backend. Current development combines Supabase-backed live article/signal persistence with repository-based Cortex state and historical snapshots.

## Quality Baseline

Current full-suite checkpoint:

```text
619 passed
```

This checkpoint follows live signal integration, Commissioner Suite expansion, Advisor 2.0, and Dashboard 2.0 visualization wiring.

## Design Principles

1. Cortex owns intelligence; GridironGPT owns football product behavior.
2. Evidence and provenance come before conclusions.
3. Live data must be deduplicated and auditable.
4. User-facing recommendations should explain why.
5. League configuration should be flexible rather than hard-coded to one platform.
6. Visualization models remain separate from Streamlit rendering.
7. Shared UI components should be reused across product surfaces.
8. Provider failures should not take down unrelated ingestion sources.
9. Infrastructure should remain replaceable behind contracts.
10. Tests define the regression boundary for every major development batch.

## Product Direction

The current development focus is the user experience around the proven intelligence engine: richer live dashboards, Cortex Explorer player dossiers, knowledge-graph visualization, commissioner analytics, and production deployment.

The long-term question GridironGPT should answer is:

> What happened, why does it matter, who else is affected, how confident is Cortex, and what should a fantasy manager or commissioner do next?
