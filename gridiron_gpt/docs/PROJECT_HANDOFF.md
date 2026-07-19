# GridironGPT Project Handoff

## Overview

GridironGPT is a fantasy football intelligence platform that ingests NFL news, injuries, roster moves, and player signals, then converts those events into actionable fantasy football recommendations.

The project began as a CLI-based fantasy analysis tool and has evolved into a Streamlit-based dashboard with confidence scoring, momentum tracking, and trend analysis.

---
## Documentation

- docs/project_handoff.md
- docs/roadmap.md
- docs/architecture.md
- docs/deployment_plan.md

## Current Architecture

### Data Sources

Current:

* ESPN NFL RSS feed
* Injury data
* Roster move data

Future:

* Multi-source RSS ingestion
* Fantasy-focused feeds
* Team-specific feeds
* Coaching and coordinator tracking

---

## Intelligence Layer

### Signal Scoring

Signals are assigned weighted values based on impact:

* Positive
* Negative
* Monitor
* Neutral

Player scores are generated from aggregated signals.

---

### Confidence Scoring

Confidence is derived from signal agreement.

Examples:

* Multiple positive signals = higher confidence
* Mixed positive and negative signals = lower confidence

Displayed as a percentage.

---

### Recency Weighting

Newer signals have greater impact.

Current weighting model:

* 0–1 days = 100%
* 2–7 days = 85%
* 8–14 days = 65%
* 15–30 days = 40%
* 30+ days = 20%

---

### Velocity Engine

Tracks player momentum over time.

Examples:

* Heating up
* Cooling off
* Stable
* Single-day signal

Velocity is expressed as:

+X.XX per week

---

## Current CLI Commands

### Rankings

```bash
gg rankings
```

Shows highest scoring players.

---

### Recommendations

```bash
gg recommendations
```

Shows:

* BUY
* WATCH
* HOLD
* MONITOR
* SELL

---

### Scorecard

```bash
gg score --player "Player Name"
```

Displays:

* Current score
* Recommendation
* Confidence
* Signal breakdown

---

### Trends

```bash
gg trend --player "Player Name"
```

Displays:

* Trend history
* Velocity
* Momentum
* Daily signals

---

### Trend  Reports

```bash
gg hot
gg cold
```

Displays:

* Rising players
* Falling players

Based on velocity and confidence.

---

## Streamlit Dashboard

### Dashboard Tab

Features:

* BUY candidates
* WATCH candidates
* Risk candidates
* Rankings

---

### Players Page

Features:

* Player selector
* Trend chart
* Scorecard

---

### Trends Tab

Features:

* Hot players
* Cold players
* Velocity
* Confidence

---

## Recent Major Features Completed

* Confidence scoring
* Recency weighting
* Velocity analysis
* Trend deduplication
* Hot player report
* Cold player report
* Streamlit dashboard tabs

---

## June 2026 – Impact Propagation Foundation

Completed:

* JSON-driven Entity Relationship Engine
* Relationship validation and loading framework
* Signal Impact API
* Impact propagation scoring
* Recommendation engine integration
* Package migration into `gridiron_gpt/intelligence`

---

## June 2026 Development Summary

### Completed

#### Entity Relationship Engine

Implemented a JSON-driven relationship framework capable of propagating impacts between related fantasy football entities.

Features:

* Relationship modeling
* Relationship validation
* Impact propagation
* Configurable JSON definitions

Example:

Joe Burrow
→ Ja'Marr Chase
→ Tee Higgins

#### Signal Impact API

Added a reusable intelligence layer for converting player signals into system-wide impacts.

Functions:

* generate_signal_impacts()
* format_signal_impact_report()

#### Recommendation Integration

Recommendations now support:

* Base signal scores
* Relationship propagation
* Adjusted scores
* Impact-aware recommendations

---

## Current Package Structure

Repository Root:

gridiron_gpt/

Application Code:

gridiron_gpt/gridiron_gpt/

Intelligence Engine:

gridiron_gpt/gridiron_gpt/intelligence/

Data:

gridiron_gpt/data/

Tests:

gridiron_gpt/tests/

---

## Current Development Focus

### V4 – Automatic Signal Propagation

Goal:

Convert propagated impacts into generated downstream signals.

Example:

Joe Burrow injury
↓
Generate signal for Ja'Marr Chase
↓
Generate signal for Tee Higgins

This represents Phase 2 of the Impact Propagation Engine roadmap.


### Entity Relationship Engine

Files:

* `gridiron_gpt/intelligence/entity_relationships.py`
* `gridiron_gpt/intelligence/relationships_loader.py`
* `gridiron_gpt/intelligence/signal_impact_api.py`
* `data/relationships.json`

Capabilities:

* Define player relationships in JSON
* Propagate signal impacts between related entities
* Generate system-wide impact scores
* Support future multi-hop impact propagation

Example:

Joe Burrow injury signal

→ Ja'Marr Chase impact

→ Tee Higgins impact

→ Future offensive ecosystem impacts

### Recommendation Engine Integration

Recommendations now support:

* Base signal score
* Propagated relationship impacts
* Adjusted recommendation scoring

This represents Phase 1 of the Impact Propagation Engine roadmap.

---

## Development Environment

Primary development environment:

* Windows 11
* WSL2 Debian
* VS Code
* GitHub
* Python virtual environments

Typical workflow:

```bash
source venv/bin/activate
git pull
streamlit run streamlit_app.py
```

---

## Long-Term Vision

Transform GridironGPT from a fantasy news tracker into a fantasy intelligence engine.

Goal:

Event occurs
→ Determine affected entities
→ Calculate impact
→ Generate recommendations

Examples:

* Offensive line injuries
* Coaching changes
* Coordinator changes
* QB injuries
* Target-share changes
* Depth chart changes

This future capability is referred to as the Impact Propagation Engine.

---

## Current Package Structure

Repository Root:

gridiron_gpt/

Primary Application Code:

gridiron_gpt/gridiron_gpt/

Intelligence Engine:

gridiron_gpt/gridiron_gpt/intelligence/

Data Files:

gridiron_gpt/data/

Tests:

gridiron_gpt/tests/

Note:

The intelligence engine was relocated into the primary application package in June 2026. New intelligence modules should be added under:

gridiron_gpt/gridiron_gpt/intelligence/
