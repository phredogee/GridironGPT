# GridironGPT

**Fantasy Football Intelligence Platform powered by Gridiron Cortex**

GridironGPT turns NFL news, injuries, roster movement, practice reports, and structured football data into persistent, explainable fantasy-football intelligence.

Instead of treating every headline as an isolated update, GridironGPT uses **Gridiron Cortex** to resolve entities, interpret signals, propagate effects through football relationships, update multidimensional player scorecards, generate recommendations, and preserve the full decision trail for Replay.

## Current v1.0 Architecture

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
Entity Resolution
    ↓
Signal Processing
    ↓
Knowledge Graph Propagation
    ↓
Scorecards + Recommendations + Explanations
    ↓
Persistent Event Bus / Replay
    ↓
Dashboard / Advisor / Players / Explorer / Inspector
```

The production ingestion path automatically forwards normalized events into Cortex. Provider ingestion remains **fail-open** if downstream Cortex processing is unavailable, preventing unnecessary provider retries.

## Core Capabilities

- Multi-source NFL ingestion
- Normalized `RawEvent` contract
- Duplicate-safe processing
- Player and team entity resolution
- Deterministic signal interpretation
- Relationship-aware knowledge-graph propagation
- Multidimensional player scorecards
- Confidence and fantasy recommendations
- Evidence chains and explanations
- Persistent Cortex event history
- Restart-safe decision Replay
- Player trends and trajectory
- Cortex Explorer and Inspector
- Dashboard and Advisor experiences
- Commissioner and league-management workflows

## Persistent Decision Trail

Cortex does more than produce a recommendation. Each decision is correlated to the input event and persisted through the Cortex event bus.

```text
RawEvent fingerprint
      ↓
correlation_id
      ↓
Cortex processing events
      ↓
cortex_events.jsonl
      ↓
ReplayEngine
```

A verified integration test simulates an application restart and reconstructs the prior Cortex decision from persistence without reprocessing the source article.

## Quality Baseline

Current verified regression checkpoint:

```text
702 passed
```

The suite covers engine reasoning, ingestion reliability, automatic runtime handoff, downstream fail-open behavior, persistence, restart semantics, Replay reconstruction, presentation models, and commissioner workflows.

## Application Surfaces

The Streamlit application includes:

- **Dashboard** — recommendations, rankings, momentum, and activity
- **Advisor** — natural-language fantasy questions with supporting evidence
- **Players** — score, trend, momentum, and recent-signal intelligence
- **Cortex Explorer** — player dossiers and knowledge-graph exploration
- **Cortex Inspector** — manual diagnostic events through the real Cortex facade
- **Ingestion Status** — provider health and persisted ingestion-run diagnostics
- **Replay / Mission Control** — inspection of prior Cortex decisions and processing history

## Technology

- Python
- Streamlit
- pytest
- RSS and structured NFL data adapters
- JSON / JSONL repository implementations
- Supabase-backed live-data paths where configured
- Knowledge-graph reasoning
- Repository-driven persistence boundaries

## Running Locally

From the project application directory:

```bash
cd gridiron_gpt
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. streamlit run streamlit_app.py
```

Run the full regression suite with:

```bash
pytest -q
```

## Documentation

Contributor and architecture documentation lives under `gridiron_gpt/docs/`:

- `PROJECT_OVERVIEW.md`
- `ARCHITECTURE.md`
- `CHANGELOG.md`
- `ROADMAP.md`
- `COMMANDS.md`
- `KNOWN_ISSUES.md`
- `DEPLOYMENT_PLAN.md`

Additional documents cover the cognitive architecture, domain model, ingestion design, data pipelines, design system, and commissioner suite.

## v1.0 Status

The core Cortex architecture is in **stabilization/release preparation**, not major subsystem expansion. Automatic ingestion, persistent scorecards, event-bus history, knowledge-graph reasoning, and Replay are implemented. Remaining work is focused on final validation, release reconciliation, and later production/cloud hardening.

## Author

Built by Alfredo Garza as an AI, data-engineering, automation, and sports-analytics portfolio project.
