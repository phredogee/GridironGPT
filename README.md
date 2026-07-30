# 🏈 GridironGPT

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Status](https://img.shields.io/badge/Status-Active_Development-brightgreen)
![Interface](https://img.shields.io/badge/Interface-CLI_%7C_Streamlit-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

### AI-Powered Fantasy Football Intelligence

GridironGPT is a fantasy football intelligence platform that transforms NFL news, injuries, roster moves, player usage, and performance data into structured signals, player scorecards, momentum reports, and explainable fantasy recommendations.

The application combines automated data ingestion, entity matching, semantic retrieval, signal processing, historical tracking, and interactive reporting. Its goal is not simply to summarize football news, but to explain how new information may affect the fantasy value of individual players and related teammates.

---

## Overview

Fantasy football managers often have to monitor multiple news feeds, injury reports, depth-chart changes, and training-camp updates before making decisions.

GridironGPT organizes that information into a repeatable intelligence pipeline:

```text
NFL Data and News Sources
            │
            ▼
     Data Ingestion
            │
            ▼
   Validation and Cleanup
            │
            ▼
 Player and Team Matching
            │
            ▼
   Story Deduplication
            │
            ▼
    Signal Extraction
            │
            ▼
 Fantasy Impact Scoring
            │
            ▼
 Momentum and Scorecards
            │
            ▼
 Reports, Rankings, and
 Explainable Recommendations
```

GridironGPT can help identify:

* Draft risers and fallers
* Positive and negative momentum
* Injury-related risk
* Opportunity changes
* Roster movement
* Training-camp trends
* Players requiring closer monitoring
* Potential BUY, HOLD, WATCH, or SELL decisions

---

## Key Features

| Feature                     | Description                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------- |
| Multi-source news ingestion | Collects NFL and fantasy football updates from multiple RSS sources                         |
| ESPN data pipeline          | Fetches, cleans, validates, and stores player information                                   |
| Player matching             | Connects articles and events to known NFL players and teams                                 |
| Story deduplication         | Prevents the same news story from being processed repeatedly                                |
| Signal deduplication        | Prevents duplicate events from affecting player scores more than once                       |
| Injury tracking             | Stores injury events and incorporates health-related risk                                   |
| Roster movement tracking    | Records signings, releases, promotions, and other roster changes                            |
| Fantasy signal processing   | Converts football events into structured positive, negative, neutral, or monitoring signals |
| Momentum engine             | Measures recent positive and negative movement over time                                    |
| Player scorecards           | Presents a structured view of player fantasy outlook                                        |
| Player intelligence reports | Combines current signals, recent events, and recommendations                                |
| Training-camp digest        | Produces consolidated reports from current camp activity                                    |
| Latest signal feed          | Displays recent fantasy-relevant events                                                     |
| Semantic advisor            | Uses embeddings and FAISS to retrieve relevant player information                           |
| Player comparisons          | Compares players using current signals and available context                                |
| Streamlit dashboard         | Provides an interactive visual interface                                                    |
| Command-line interface      | Supports ingestion, diagnostics, reports, and fantasy queries                               |

---

## Fantasy Intelligence Model

GridironGPT converts football information into normalized fantasy signals.

| Signal             | Base Impact |
| ------------------ | ----------: |
| Positive           |      `+1.0` |
| Monitor            |      `-0.5` |
| Negative           |      `-1.0` |
| Neutral or Unknown |       `0.0` |

A signal represents one fantasy-relevant event rather than an entire article.

For example:

```text
Event:
Tank Dell works with the first-team offense during practice.

Entity:
Tank Dell — WR, Houston Texans

Signal:
Positive opportunity signal

Impact:
+1.0

Reason:
First-team usage may indicate an increased offensive role.

Recommendation:
BUY / MOVE UP WATCHLIST
```

The scoring layer can combine multiple signals while retaining the event history needed to explain why a player's outlook changed.

---

## Player Intelligence

GridironGPT builds player-level intelligence from several forms of evidence:

* News mentions
* Practice participation
* First-team or second-team usage
* Injury status
* Transactions and roster movement
* Positive and negative camp reports
* Recent momentum
* Historical signal activity
* Team and teammate context

A player report can include:

```text
Player: Tank Dell
Team: Houston Texans
Position: WR

Current Outlook: Positive
Momentum: Rising
Recommendation: BUY

Recent Evidence:
+ First-team practice usage
+ Positive training-camp report
+ Increased opportunity
- Recent limited practice

Summary:
The positive opportunity signals currently outweigh the health concern,
but continued injury monitoring is recommended.
```

---

## Momentum Engine

The momentum engine evaluates the direction of a player's recent fantasy signals.

Rather than treating every event equally forever, momentum emphasizes current activity and helps distinguish between:

* A player receiving several recent positive updates
* A player whose earlier hype has cooled
* A player accumulating injury or role-related concerns
* A player with mixed or uncertain signals

Momentum reports support:

* Hot-player reports
* Cold-player reports
* Risers and fallers
* Player timelines
* Training-camp monitoring
* Draft watchlists

---

## Semantic Advisor

GridironGPT includes a semantic retrieval layer built with sentence-transformer embeddings and FAISS vector search.

The semantic advisor:

1. Converts player documents and football information into embeddings.
2. Stores those embeddings in a FAISS index.
3. Retrieves relevant records for a user question.
4. Provides the retrieved context to the configured response layer.
5. Produces a fantasy-focused answer grounded in available project data.

Example question:

```bash
python -m gridiron_gpt.cli ask "Why is Tank Dell a BUY?"
```

Other example questions:

```text
Which Houston wide receiver has the strongest momentum?

What recent news is affecting Christian Watson?

Compare Tank Dell and Christian Watson.

Which players have accumulated negative injury signals?

Why did this player's score change?
```

---

## Data Pipelines

### News Pipeline

```text
RSS Sources
     │
     ▼
Article Collection
     │
     ▼
Relevance Filtering
     │
     ▼
Story Hash Generation
     │
     ▼
Duplicate Detection
     │
     ▼
Player Matching
     │
     ▼
Signal Generation
     │
     ▼
Signal Persistence
```

### ESPN Pipeline

```text
ESPN Data
    │
    ▼
Fetch and Normalize
    │
    ▼
Schema Validation
    │
    ▼
Player Profile Updates
    │
    ▼
Ranking and Retrieval
```

### Daily Intelligence Pipeline

```text
Source Updates
      │
      ├── News
      ├── Injuries
      ├── Roster Moves
      └── Player Data
      │
      ▼
Signal Processing
      │
      ▼
Persistence
      │
      ▼
Momentum Report
      │
      ▼
Training-Camp Digest
      │
      ▼
Dashboard and CLI
```

---

## Architecture

GridironGPT is organized around several cooperating layers.

```text
┌─────────────────────────────────────────────┐
│              User Interfaces                │
│       Streamlit Dashboard and CLI           │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│          Reports and Intelligence           │
│ Player Reports, Digests, Rankings, Queries  │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│          Fantasy Intelligence Layer         │
│ Signals, Momentum, Scores, Recommendations  │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│       Entity and Relationship Context       │
│ Players, Teams, Aliases, Related Entities   │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│            Persistence Layer                │
│ Articles, Events, Signals, Scores, Indexes  │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│             Ingestion Layer                 │
│ RSS, ESPN, Injuries, Rosters, NFL Data      │
└─────────────────────────────────────────────┘
```

---

## Active Application Areas

The current implementation is primarily organized within the following areas:

```text
gridiron_gpt/
├── app/                         # Application services
├── cli/                         # Command-line commands
├── config/                      # Configuration
├── core/                        # Core advisor and application logic
├── dashboard/                   # Dashboard components
├── data/                        # Runtime data and persisted outputs
├── data_ingest/                 # Player and source ingestion
├── data_sources/                # External data-provider integrations
├── docs/                        # Project documentation
├── draft/                       # Draft intelligence functionality
├── ingestion/                   # Ingestion orchestration
├── intelligence/                # Fantasy intelligence services
├── models/                      # Domain and data models
├── pipelines/                   # Processing pipelines
├── scripts/                     # Operational and pipeline scripts
├── semantic/                    # Semantic search and retrieval
├── store/                       # Persistence utilities
├── tests/                       # Automated tests
├── validators/                  # Data and profile validation
├── __main__.py                  # Python module entry point
├── streamlit_app.py             # Streamlit application
├── requirements.txt             # Runtime dependencies
├── pyproject.toml               # Python project configuration
├── ARCHITECTURE.md              # Architecture notes
└── ROADMAP.md                   # Development roadmap
```

Some older directories remain in the repository while the application continues to be consolidated. See `ARCHITECTURE.md` for the currently recognized runtime path and areas requiring further review.

---

## Technology Stack

### Core

* Python 3.11+
* Click
* Streamlit
* Pandas
* NumPy

### AI and Retrieval

* Sentence Transformers
* FAISS
* Retrieval-Augmented Generation concepts
* Configurable LLM providers
* Local and API-backed language models

### Data

* ESPN data ingestion
* `nflreadpy`
* RSS feed processing
* JSON and JSONL persistence
* Player profile validation
* Event and story hashing

### Development

* Git and GitHub
* Pytest
* Pre-commit
* Linux and WSL
* Virtual environments

---

## Requirements

* Python 3.11 or newer
* Git
* A Python virtual environment
* Dependencies listed in `requirements.txt`
* Optional provider credentials for API-backed language models

Major dependencies include:

* `faiss-cpu`
* `sentence-transformers`
* `torch`
* `nflreadpy`
* `streamlit`
* `click`
* `pandas`

---

## Installation

Clone the repository:

```bash
git clone git@github.com:phredogee/GridironGPT.git
cd GridIronGPT
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the project dependencies:

```bash
pip install -r gridiron_gpt/requirements.txt
```

Set the repository root on `PYTHONPATH` when needed:

```bash
export PYTHONPATH="$(pwd)"
```

> The repository currently contains both root-level and nested project files. Run commands from the repository root unless a command specifically requires the `gridiron_gpt/` application directory.

---

## Running the Application

### Streamlit Dashboard

From the repository root:

```bash
streamlit run gridiron_gpt/streamlit_app.py
```

### Command-Line Interface

Display the available CLI commands:

```bash
python -m gridiron_gpt --help
```

Run the fantasy advisor:

```bash
python -m gridiron_gpt.cli ask "Why is Tank Dell a BUY?"
```

Depending on the local project configuration, a provider can be selected with environment variables:

```bash
LLM_PROVIDER=deepseek \
GRIDIRON_LLM=deepseek \
python -m gridiron_gpt.cli ask "Compare Tank Dell and Christian Watson."
```

---

## ESPN Commands

Ingest ESPN data for a selected week:

```bash
python -m gridiron_gpt espn intake --week 5
```

Preview the ingestion without saving:

```bash
python -m gridiron_gpt espn intake --week 5 --dry-run
```

Scan for missing or incomplete player entries:

```bash
python -m gridiron_gpt espn fix --week 5
```

Preview and validate the ESPN data structure:

```bash
python -m gridiron_gpt espn dry-run --week 5
```

---

## Running Tests

From the repository root:

```bash
export PYTHONPATH="$(pwd)"
pytest gridiron_gpt/tests/ -v
```

To stop after the first failure:

```bash
pytest gridiron_gpt/tests/ -x -v
```

To run a specific test file:

```bash
pytest gridiron_gpt/tests/test_pipeline.py -v
```

The exact number of passing tests may change as the project grows, so the README intentionally does not advertise a fixed test count.

---

## Environment Variables

| Variable            | Purpose                                                     |
| ------------------- | ----------------------------------------------------------- |
| `PYTHONPATH`        | Ensures the local `gridiron_gpt` package resolves correctly |
| `GRIDIRON_LLM`      | Selects the configured language-model backend               |
| `LLM_PROVIDER`      | Selects the provider used by the advisor                    |
| `HF_TOKEN`          | Optional Hugging Face token                                 |
| `OPENAI_API_KEY`    | Optional OpenAI provider credential                         |
| `ANTHROPIC_API_KEY` | Optional Anthropic provider credential                      |
| `DEEPSEEK_API_KEY`  | Optional DeepSeek provider credential                       |

Only configure credentials for providers you intend to use. Do not commit `.env` files or private API keys.

---

## Data and Repository Safety

The repository should not contain:

* API keys
* Authentication tokens
* Private league credentials
* Large generated model files
* Private user data
* Unlicensed proprietary datasets

Use `.env.example` to document expected settings and keep real credentials in a local `.env` file excluded by `.gitignore`.

---

## Current Capabilities

The following capabilities have been implemented or substantially developed:

* [x] ESPN player-data ingestion
* [x] Player profile validation
* [x] Semantic player retrieval
* [x] FAISS indexing
* [x] Multi-source RSS ingestion
* [x] Article relevance filtering
* [x] Story-level deduplication
* [x] Signal-level deduplication
* [x] Injury event persistence
* [x] Roster movement persistence
* [x] Daily pipeline processing
* [x] Player momentum engine
* [x] Hot and cold player reports
* [x] Player intelligence reports
* [x] Latest signal feed
* [x] Training-camp digest
* [x] Streamlit player intelligence interface
* [x] CLI-based querying
* [x] Automated tests for major workflows

---

## Roadmap

### Data Expansion

* [ ] Add additional reliable NFL news providers
* [ ] Expand structured injury sources
* [ ] Add depth-chart and transaction providers
* [ ] Strengthen `nflreadpy` integration
* [ ] Ingest rookie and future NFL draft classes
* [ ] Add team-level context and scoring

### Intelligence

* [ ] Improve alias and nickname resolution
* [ ] Strengthen multi-player headline processing
* [ ] Expand relationship-based impact propagation
* [ ] Add configurable signal decay
* [ ] Improve confidence scoring
* [ ] Preserve complete recommendation audit trails
* [ ] Add historical score comparisons

### Platform

* [ ] Consolidate duplicate and legacy directories
* [ ] Move persistent application data to a database
* [ ] Add scheduled cloud ingestion
* [ ] Add retry and backoff handling for unavailable providers
* [ ] Expose intelligence through an API
* [ ] Improve deployment and observability
* [ ] Add league-specific configuration

See `ROADMAP.md` for more detailed planning.

---

## Documentation

Project documentation is maintained in:

* [`ARCHITECTURE.md`](ARCHITECTURE.md)
* [`ROADMAP.md`](ROADMAP.md)
* [`docs/`](docs/)

As the project continues to mature, the documentation should be expanded to include:

```text
docs/
├── PROJECT_OVERVIEW.md
├── ARCHITECTURE.md
├── CHANGELOG.md
├── ROADMAP.md
├── COMMANDS.md
└── KNOWN_ISSUES.md
```

---

## Project Status

GridironGPT is under active development.

The repository currently contains a mixture of active application code, experimental modules, and legacy paths created during earlier development stages. Current work is focused on:

* Consolidating the active architecture
* Improving data-source reliability
* Expanding fantasy intelligence
* Strengthening persistence and auditability
* Separating reusable intelligence components from interface code
* Preparing the application for broader deployment

---

## License

This project is licensed under the MIT License.

See [`LICENSE`](LICENSE) for details.

---

## Author

**Alfredo Garza**

GridironGPT is an independent portfolio project focused on applied artificial intelligence, data engineering, intelligent automation, software architecture, and fantasy football analytics.

* GitHub: [phredogee](https://github.com/phredogee)
