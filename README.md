![Python](https://img.shields.io/badge/Python-3.11-blue)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)






🏈 GridironGPT

GridironGPT is a fantasy football intelligence platform designed to track player news, injuries, roster movement, and training camp developments while generating actionable fantasy football insights.

The platform combines player data, news ingestion, fantasy signal scoring, timelines, team reports, and player comparisons to help identify draft risers, fallers, and emerging opportunities.

🚀 Features
Training Camp Intelligence
ESPN NFL RSS news ingestion
Player recognition and matching
Daily camp digest
Team camp reports
Player timelines
Camp risers and fallers
Draft Watch rankings
Fantasy Signal Engine

GridironGPT converts football news into fantasy signals.

Signal	Score
Positive	+1.0
Monitor	-0.5
Negative	-1.0
Unknown	0.0

These signals power:

Draft Watch
Scorecards
Player Comparisons
Team Reports
Risers & Fallers
Player Intelligence

Generate player reports:

gg report --player "Tank Dell"

View player timelines:

gg timeline --player "Tank Dell"

Generate fantasy scorecards:

gg score --player "Tank Dell"

Compare players:

gg compare --player1 "Tank Dell" --player2 "Christian Watson"
Team Intelligence

Generate team-wide camp reports:

gg report-team --team HOU
Daily Workflow

Update all available data:

gg update-all

Generate the daily camp digest:

gg digest

View draft movement:

gg draft-watch
gg risers
gg fallers
🏗 Architecture
RSS News Feeds
        ↓
Player Matcher
        ↓
Fantasy Signal Engine
        ↓
Scorecards
Timelines
Comparisons
Team Reports
Draft Watch
🧪 Development & Testing

Run tests:

export PYTHONPATH=$(pwd)
pytest
🛠 Technology Stack
Python 3.11
FAISS
RSS Feed Processing
JSON Data Pipelines
Fantasy Signal Scoring
CLI-Based Workflow
🔮 Roadmap
BUY / HOLD / SELL recommendations
Additional fantasy news sources
Historical trend tracking
Dynasty league support
Automated scheduled updates
Streamlit dashboard
LLM-powered draft assistant
