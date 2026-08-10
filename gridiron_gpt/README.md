<p align="center">
  <img src="assets/banners/cortex_engine_banner.png" alt="Gridiron Cortex Engine" width="100%">
</p>

# GridironGPT

**Fantasy Football Intelligence Platform powered by Gridiron Cortex**

GridironGPT converts NFL news and structured football evidence into persistent, explainable fantasy-football intelligence. The application owns football-domain workflows and presentation; **Gridiron Cortex** owns reusable intelligence processing, scoring, propagation, recommendations, explanations, and decision history.

## v1.0 Intelligence Pipeline

```text
NFL Providers
    ↓
Provider Adapters
    ↓
IngestionService
    ↓
Normalize + Deduplicate
    ↓
RawEvent
    ↓
Gridiron Cortex
    ↓
Resolve → Classify → Propagate → Score
    ↓
Recommend → Explain
    ↓
Event Bus + Persistent Scorecards
    ↓
Replay / Dashboard / Advisor / Explorer / Inspector
```

Runtime ingestion automatically forwards normalized events into Cortex through an injected event-processor boundary. If Cortex is temporarily unavailable, ingestion remains fail-open so a successful provider fetch is not incorrectly retried.

## Gridiron Cortex

Cortex provides the reusable reasoning layer behind GridironGPT:

- entity resolution
- signal interpretation
- evidence and confidence handling
- football relationship propagation
- multidimensional scorecards
- recommendations
- explanations and evidence chains
- event-bus observability
- persisted decision history
- Replay reconstruction

## Product Surfaces

- **Dashboard** — recommendation metrics, rankings, momentum, and activity
- **Advisor** — natural-language fantasy questions with evidence
- **Players** — score, confidence, trend, momentum, and recent signals
- **Cortex Explorer** — player dossiers and knowledge-graph views
- **Cortex Inspector** — diagnostic event processing through the real facade
- **Ingestion Status** — provider health and run history
- **Replay / Mission Control** — persisted decision-trail inspection
- **Commissioner Suite** — configurable league and scheduling workflows

## Persistence and Replay

Cortex persists core engine artifacts through repository-backed JSON/JSONL implementations during local development. Event history and player scorecards survive application restarts.

A production-path integration test verifies:

```text
Provider record
    ↓
Runtime ingestion
    ↓
Cortex decision
    ↓
Event + scorecard persistence
    ↓
Application restart
    ↓
Replay reconstruction
```

Replay rebuilds the prior decision from persisted correlated events rather than reprocessing the original article.

## Quality Baseline

Current verified regression checkpoint:

```text
702 passed
```

## Project Structure

```text
gridiron_gpt/
├── apps/streamlit/        # Streamlit pages and reusable components
├── data_ingest/           # Football data and legacy presentation scoring paths
├── ingestion/             # Provider adapters, normalization, runtime composition
├── intelligence/          # Football-product intelligence helpers
├── gridiron_cortex/       # Cortex engine and facade
├── docs/                  # Architecture, roadmap, commands, known issues, deployment
├── scripts/               # Smoke/utility scripts
├── tests/                 # Regression and integration tests
├── assets/                # Branding assets
└── streamlit_app.py       # Main application entry point
```

## Run Locally

From this directory:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest -q
PYTHONPATH=. streamlit run streamlit_app.py
```

## Core Documentation

Start with:

- `docs/PROJECT_OVERVIEW.md`
- `docs/ARCHITECTURE.md`
- `docs/CHANGELOG.md`
- `docs/ROADMAP.md`
- `docs/COMMANDS.md`
- `docs/KNOWN_ISSUES.md`
- `docs/DEPLOYMENT_PLAN.md`

Specialized documents cover cognitive architecture, ingestion, data pipelines, the domain model, design system, and commissioner features.

## Current Status

The core Cortex architecture is complete for the v1.0 stabilization boundary. Automatic ingestion, persistent scorecards, event-bus decision history, knowledge-graph reasoning, and Replay are implemented. Current work is release validation and later production/cloud hardening rather than adding another major engine subsystem.

## License

This project is licensed under the MIT License.
