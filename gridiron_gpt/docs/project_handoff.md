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

### Momentum Reports

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

### Player Tab

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
