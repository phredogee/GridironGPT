![Python](https://img.shields.io/badge/Python-3.13-blue)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Interface](https://img.shields.io/badge/Interface-Streamlit-red)
![Engine](https://img.shields.io/badge/Powered%20By-Gridiron%20Cortex-purple)

# 🏈 GridironGPT

### AI-Powered Fantasy Football Intelligence Platform

GridironGPT is an AI-powered fantasy football intelligence platform built around the **Gridiron Cortex** engine.

The platform transforms NFL news, injury reports, roster movement, practice updates, and player developments into structured fantasy football intelligence. Rather than only collecting headlines, GridironGPT identifies relevant entities, extracts fantasy signals, evaluates their impact, updates player scorecards, and generates explainable recommendations.

GridironGPT is designed to help fantasy managers identify:

* 🔥 Draft risers
* ⚠️ Injury and availability risks
* 📈 Positive momentum
* 📉 Negative trends
* 🎯 Waiver and roster opportunities
* 🏆 Draft-day value
* 🔄 Indirect impact between related players and teams

---

## ✨ What It Does

```text
NFL News and Football Events
            │
            ▼
      Event Ingestion
            │
            ▼
      Entity Resolution
            │
            ▼
      Signal Processing
            │
            ▼
       Impact Analysis
            │
            ▼
 Relationship Propagation
            │
            ▼
    Player Scorecards
            │
            ▼
Recommendation and Explanation
            │
            ▼
 Streamlit Dashboard and CLI
```

GridironGPT converts unstructured football information into structured, traceable fantasy intelligence.

Each event can contribute to:

* Player score changes
* Team-level effects
* Positional competition
* Opportunity changes
* Health and risk indicators
* Momentum tracking
* Fantasy recommendations
* Related-player impact

---

## 🚀 Key Features

| Feature                     | Description                                                           |
| --------------------------- | --------------------------------------------------------------------- |
| 🧠 Gridiron Cortex          | Modular intelligence engine that processes football events            |
| 📰 News Ingestion           | Collects NFL news, injury reports, and roster updates                 |
| 🧩 Entity Resolution        | Identifies players, teams, and related football entities              |
| 📡 Signal Processing        | Converts text into positive, negative, neutral, or monitoring signals |
| 🔄 Impact Propagation       | Distributes indirect impact across related players and teams          |
| 🎯 Recommendation Engine    | Produces BUY, HOLD, WATCH, MONITOR, and SELL recommendations          |
| 📊 Player Scorecards        | Tracks opportunity, health, hype, risk, momentum, and overall score   |
| 💡 Explainable Intelligence | Generates readable reasoning for recommendations                      |
| ♻️ Event Deduplication      | Prevents duplicate events from repeatedly affecting scores            |
| 📈 Draft Watch              | Tracks fantasy risers and fallers                                     |
| ⏱️ Player Timelines         | Maintains historical player activity and score changes                |
| ⚖️ Player Comparisons       | Compares players using current fantasy signals                        |
| 🏟️ Team Intelligence       | Produces team-level camp and roster summaries                         |
| 📋 Daily Digest             | Consolidates important football developments                          |
| 🖥️ Streamlit Dashboard     | Provides an interactive interface for exploring results               |
| 💻 Command-Line Tools       | Supports reports, updates, comparisons, and scoring workflows         |

---

# 🧠 Gridiron Cortex

Gridiron Cortex is the intelligence engine that powers GridIronGPT.

It processes raw football events through a modular pipeline:

```text
Raw Event
   │
   ▼
Entity Resolver
   │
   ▼
Signal Processor
   │
   ▼
Relationship Engine
   │
   ▼
Propagation Planner
   │
   ▼
Score Engine
   │
   ▼
Recommendation Engine
   │
   ▼
Explanation Engine
   │
   ▼
Engine Result
```

## Core Responsibilities

### Entity Resolution

Identifies the players, teams, and other football entities referenced in an incoming event.

Example:

```text
"Tank Dell returned to first-team practice for Houston."

Resolved Entities:
- Tank Dell — Player — HOU
- Houston Texans — Team — HOU
```

### Signal Processing

Determines the fantasy meaning of an event.

Signals may include:

* Positive opportunity
* Negative health news
* Increased role
* Reduced workload
* Roster competition
* Practice participation
* Team movement
* Neutral monitoring information

### Impact Analysis

Calculates how strongly an event should affect each entity.

Example:

```text
Tank Dell:
Direct Impact: +1.0

Houston Texans:
Team Impact: +0.3
```

### Relationship Propagation

Allows an event involving one entity to affect related entities.

For example:

```text
Quarterback Injury
        │
        ├── Negative impact on wide receivers
        ├── Negative impact on tight ends
        ├── Possible increase in running-back volume
        └── Team-level offensive downgrade
```

Propagation considers factors such as:

* Relationship type
* Relationship strength
* Confidence
* Hop count
* Propagation weight

### Score Updates

Gridiron Cortex updates persistent player scorecards after processing valid events.

### Recommendations

The recommendation engine translates score changes and current conditions into fantasy guidance.

Possible recommendations include:

* BUY
* HOLD
* WATCH
* MONITOR
* SELL

### Explanations

Each recommendation includes an explanation describing:

* What happened
* Which signal was identified
* How the player was affected
* Why the recommendation changed
* Whether related entities were affected

---

# 📊 Player Scorecards

Player scorecards provide a multi-dimensional view of a player's fantasy outlook.

| Category    | Description                            |
| ----------- | -------------------------------------- |
| Overall     | Combined fantasy outlook               |
| Opportunity | Expected role, workload, and usage     |
| Health      | Injury status and availability         |
| Hype        | Positive attention and market interest |
| Risk        | Uncertainty, competition, and downside |
| Momentum    | Direction and recent rate of change    |

Example:

```text
🏈 Tank Dell Player Scorecard

Overall:      52.0
Opportunity:  52.0
Health:       50.0
Hype:         52.0
Risk:         50.0
Momentum:     52.0

Recommendation:
BUY

Confidence:
70%
```

Scorecards are stored historically so the application can evaluate player movement over time rather than relying only on a single current score.

---

# 📡 Fantasy Signals

Each player update is converted into a structured fantasy signal.

| Signal               | Base Score |
| -------------------- | ---------: |
| 🟢 Positive          |       +1.0 |
| 🟡 Monitor           |       -0.5 |
| 🔴 Negative          |       -1.0 |
| ⚪ Neutral or Unknown |        0.0 |

Example:

```text
Tank Dell

+1.0 Returned to practice
+1.0 First-team repetitions
+1.0 Positive camp report
-0.5 Limited participation

Total Signal Score: +2.5

Recommendation:
BUY / MOVE UP WATCHLIST
```

Signals are also evaluated using factors such as:

* Confidence
* Recency
* Relationship strength
* Direct versus propagated impact
* Event type
* Duplicate detection

---

# ♻️ Event Deduplication

GridironGPT creates a fingerprint for each processed event.

Before applying a score change, the event repository checks whether the same event has already been processed.

```text
Incoming Event
      │
      ▼
Create Fingerprint
      │
      ▼
Check Event Repository
      │
 ┌────┴────┐
 │         │
New     Duplicate
 │         │
 ▼         ▼
Process   Ignore
```

Duplicate events return an engine result indicating:

```text
Duplicate event ignored.
```

This prevents repeated headlines or duplicated feeds from artificially inflating or reducing player scores.

---

# 🏈 Player Intelligence

## Generate a Player Report

```bash
gg report --player "Tank Dell"
```

## View a Player Timeline

```bash
gg timeline --player "Tank Dell"
```

## Generate a Fantasy Scorecard

```bash
gg score --player "Tank Dell"
```

Example output:

```text
🏈 Tank Dell Scorecard

Current Score: +2.5

Recommendation:
BUY / MOVE UP WATCHLIST
```

---

# ⚖️ Player Comparisons

Compare players using current fantasy signals, scorecards, and recent momentum.

```bash
gg compare --player1 "Tank Dell" --player2 "Christian Watson"
```

Example:

```text
Tank Dell         +2.5
Christian Watson  +1.0

Edge:
Tank Dell

Recommendation:
Prefer Tank Dell based on current signals and momentum.
```

---

# 📈 Draft Intelligence

## Draft Watch

```bash
gg draft-watch
```

## Camp Risers

```bash
gg risers
```

## Camp Fallers

```bash
gg fallers
```

## Draft Watch Example

<img width="408" height="235" alt="GridironGPT Draft Watch" src="https://github.com/user-attachments/assets/16908c8c-d20e-4d91-bc1a-ff228e9a5120" />

Draft Watch helps identify:

* Players gaining opportunity
* Players receiving positive camp reports
* Players losing depth-chart position
* Injury-related movement
* Emerging waiver and draft targets

---

# 🏟️ Team Intelligence

Generate team-wide reports:

```bash
gg report-team --team HOU
```

Team reports can include:

* Player news
* Injury updates
* Roster movement
* Positional competition
* Fantasy outlooks
* Team-level signal changes
* Related-player impact

---

# 📰 Daily Workflow

## Update Available Sources

```bash
gg update-all
```

## Generate the Daily Digest

```bash
gg digest
```

The daily digest consolidates:

* Training camp reports
* Injury developments
* Roster movement
* Player opportunity changes
* Fantasy recommendations
* Risers and fallers
* Players requiring additional monitoring

---

# 🖥️ Streamlit Dashboard

GridironGPT includes a Streamlit interface for viewing fantasy intelligence interactively.

The dashboard provides access to:

* Player recommendations
* Player scorecards
* Score trends
* Momentum indicators
* Draft Watch
* Signal rankings
* Cortex Inspector
* Engine explanations
* Processed events
* Propagated impacts

Run the application locally:

```bash
streamlit run streamlit_app.py
```

---

# 🔍 Cortex Inspector

The Cortex Inspector exposes the internal results of the intelligence pipeline.

It can display:

* Resolved entities
* Extracted signals
* Direct impacts
* Propagated impacts
* Score updates
* Recommendation confidence
* Explanation output
* Duplicate-event status

This supports transparency, debugging, and explainable AI development.

---

# 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │   Football Sources  │
                    │ RSS, injuries, news │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Data Ingestion    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Event Repository   │
                    │   Deduplication     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Entity Resolution  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Signal Processing  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Relationship and   │
                    │ Propagation Engine  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Score Engine     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Player Scorecards   │
                    │ Historical Storage  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Recommendation    │
                    │ Explanation Engine  │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
       ┌──────────────────┐        ┌──────────────────┐
       │ Streamlit UI     │        │ CLI and Reports  │
       └──────────────────┘        └──────────────────┘
```

---

# 📁 Project Structure

```text
GridironGPT/
├── gridiron_gpt/
│   ├── data_ingest/
│   ├── reports/
│   ├── scoring/
│   ├── retrieval/
│   └── utilities/
│
├── gridiron_cortex/
│   ├── engine/
│   ├── knowledge/
│   ├── models/
│   ├── persistence/
│   ├── propagation/
│   ├── repositories/
│   └── scoring/
│
├── data/
│   ├── cortex/
│   ├── news/
│   └── player data/
│
├── docs/
│   ├── PROJECT_OVERVIEW.md
│   ├── ARCHITECTURE.md
│   ├── CHANGELOG.md
│   ├── ROADMAP.md
│   ├── COMMANDS.md
│   └── KNOWN_ISSUES.md
│
├── tests/
├── streamlit_app.py
├── requirements.txt
└── README.md
```

The exact project structure may continue evolving as additional providers, persistence layers, and interfaces are added.

---

# 🛠️ Technology Stack

## Core Development

* Python 3.13
* Git
* GitHub
* Linux and WSL
* Visual Studio Code

## Application Interface

* Streamlit
* Command-line interface

## AI and Retrieval

* Local LLM integration with Ollama
* Retrieval-Augmented Generation
* FAISS vector search
* Natural-language query handling

## Data and Persistence

* RSS feed processing
* JSON data pipelines
* JSONL scorecard persistence
* Event fingerprinting
* Historical score tracking

## Intelligence Architecture

* Entity resolution
* Rule-based signal extraction
* Relationship modeling
* Signal propagation
* Confidence scoring
* Recommendation generation
* Explanation generation

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/phredogee/GridironGPT.git
cd GridironGPT
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Linux or WSL:

```bash
source .venv/bin/activate
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# ▶️ Running GridIronGPT

## Start the Streamlit Application

```bash
streamlit run streamlit_app.py
```

## Run CLI Commands

Examples:

```bash
gg update-all
gg digest
gg report --player "Tank Dell"
gg score --player "Tank Dell"
gg timeline --player "Tank Dell"
gg compare --player1 "Tank Dell" --player2 "Christian Watson"
gg draft-watch
gg risers
gg fallers
```

Available commands may vary as the CLI continues to evolve.

---

# 🧪 Example Cortex Event

Input:

```text
Tank Dell returned to first-team practice for Houston.
```

Possible engine result:

```text
Resolved Entities:
- Tank Dell
- Houston Texans

Signal:
Positive

Direct Player Impact:
+1.0

Team Impact:
+0.3

Recommendation:
BUY

Confidence:
70%

Explanation:
Tank Dell received a positive opportunity signal after returning
to first-team practice. His scorecard increased because the event
indicates improved availability and offensive involvement.
```

---

# ✅ Current Capabilities

* [x] RSS news ingestion
* [x] Player matching
* [x] Entity resolution
* [x] Fantasy signal processing
* [x] Event deduplication
* [x] Player scorecards
* [x] Historical scorecard persistence
* [x] Recommendation generation
* [x] Explanation generation
* [x] Relationship modeling
* [x] Signal propagation
* [x] Player timelines
* [x] Player comparisons
* [x] Draft Watch
* [x] Daily digest
* [x] Team reports
* [x] Streamlit dashboard
* [x] Cortex Inspector
* [x] Local LLM support

---

# 🔮 Roadmap

## Data Expansion

* [ ] Add additional NFL news providers
* [ ] Expand NBC Sports ingestion
* [ ] Add structured NFL data integrations
* [ ] Add draft-class and rookie data
* [ ] Improve player alias and nickname matching
* [ ] Improve multi-player headline handling
* [ ] Add source-health monitoring and fallback behavior

## Intelligence Engine

* [ ] Expand relationship types
* [ ] Improve multi-hop propagation
* [ ] Add configurable signal decay
* [ ] Add source reliability weighting
* [ ] Improve confidence calibration
* [ ] Add team and position-group scorecards
* [ ] Add deeper audit trails for propagated impacts
* [ ] Evaluate hybrid rule-based and machine-learning scoring

## Platform

* [ ] Migrate persistence to a database backend
* [ ] Add REST API support
* [ ] Add scheduled cloud ingestion
* [ ] Add authentication and user profiles
* [ ] Add league-specific scoring settings
* [ ] Add dynasty league support
* [ ] Add live draft companion features
* [ ] Add cloud deployment and monitoring

---

# 📚 Documentation

Project documentation is maintained in the `docs/` directory.

Recommended documentation structure:

```text
docs/
├── PROJECT_OVERVIEW.md
├── ARCHITECTURE.md
├── CHANGELOG.md
├── ROADMAP.md
├── COMMANDS.md
└── KNOWN_ISSUES.md
```

These documents cover:

* Project purpose and scope
* System architecture
* Development history
* Planned features
* Common commands
* Known limitations and technical issues

---

# ⚠️ Project Status

GridironGPT is under active development.

The application currently serves as both:

1. A functional fantasy football intelligence platform
2. An ongoing AI engineering and software architecture project

Features, commands, data sources, and internal architecture may change as the system evolves.

---

# 📄 License

This project is licensed under the MIT License.

See the `LICENSE` file for additional information.

---

# 👨‍💻 Author

Built by **Alfredo Garza** as part of an ongoing professional portfolio focused on:

* Artificial intelligence
* Data engineering
* Intelligent automation
* Software architecture
* Natural language processing
* Explainable AI
* Sports analytics

GitHub: [phredogee](https://github.com/phredogee)
