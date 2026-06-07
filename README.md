![Python](https://img.shields.io/badge/Python-3.11-blue)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

# 🏈 GridironGPT

### Fantasy Football Intelligence Platform

GridironGPT transforms training camp news, injury reports, roster movement, and player updates into actionable fantasy football insights.

Instead of manually tracking dozens of news sources, GridironGPT automatically aggregates signals and helps identify:

🔥 Draft Risers
⚠ Injury Risks
📈 Positive Momentum
📉 Negative Trends
🏆 Draft-Day Opportunities

---

## ✨ What It Does

```text
NFL News
    ↓
Player Matching
    ↓
Fantasy Signal Engine
    ↓
Draft Intelligence
```

The platform continuously converts football news into fantasy recommendations through a scoring system that powers reports, comparisons, timelines, and rankings.

---

## 🚀 Key Features

| Feature               | Description                           |
| --------------------- | ------------------------------------- |
| 📰 News Ingestion     | Pulls NFL news from RSS feeds         |
| 🧠 Player Matching    | Maps headlines to real NFL players    |
| 📈 Draft Watch        | Tracks fantasy risers and fallers     |
| 📋 Daily Digest       | Consolidated camp intelligence report |
| ⏱ Player Timelines    | Historical player activity tracking   |
| 🏈 Team Reports       | Team-wide training camp summaries     |
| ⚖ Player Comparisons  | Compare fantasy outlooks              |
| 🎯 Fantasy Scorecards | Signal-based player evaluations       |

---

# 📊 Fantasy Signal Engine

Every player update is converted into a fantasy signal.

| Signal      | Score |
| ----------- | ----- |
| 🟢 Positive | +1.0  |
| 🟡 Monitor  | -0.5  |
| 🔴 Negative | -1.0  |
| ⚪ Unknown   | 0.0   |

Example:

```text
Tank Dell

+1.0 First-team reps
+1.0 Working with first-team offense
+1.0 Positive camp report
-0.5 Limited practice

Total Score: +2.5

Recommendation:
BUY / MOVE UP WATCHLIST
```

---

# 🏈 Player Intelligence

### Generate Player Reports

```bash
gg report --player "Tank Dell"
```

### View Player Timeline

```bash
gg timeline --player "Tank Dell"
```

### Generate Fantasy Scorecard

```bash
gg score --player "Tank Dell"
```

Example Output:

```text
🏈 Tank Dell Scorecard

Current Score: +2.5

Recommendation:
BUY / MOVE UP WATCHLIST
```

---

# ⚖ Player Comparisons

Compare players using current training camp signals.

```bash
gg compare --player1 "Tank Dell" --player2 "Christian Watson"
```

Example:

```text
Tank Dell        +2.5
Christian Watson +1.0

Edge: Tank Dell

Recommendation:
Prefer Tank Dell based on current camp signals.
```

---

# 📈 Draft Intelligence

### Draft Watch

```bash
gg draft-watch
```

### Camp Risers

```bash
gg risers
```

### Camp Fallers

```bash
gg fallers
```

---

# 🏟 Team Intelligence

Generate team-wide camp reports.

```bash
gg report-team --team HOU
```

Includes:

* Player News
* Injury Updates
* Roster Movement
* Fantasy Outlooks

---

# 📰 Daily Workflow

### Update All Sources

```bash
gg update-all
```

### Generate Daily Digest

```bash
gg digest
```

This creates a consolidated report containing:

* Training Camp News
* Injury Reports
* Roster Movement
* Fantasy Outlooks

---

# 🏗 Architecture

```text
RSS News Feeds
        │
        ▼
 Player Matcher
        │
        ▼
 Fantasy Signal Engine
        │
 ┌──────┼──────┐
 ▼      ▼      ▼
Score  Timeline Reports
Cards
        │
        ▼
 Draft Watch
 Comparisons
 Recommendations
```

---

# 🛠 Technology Stack

* Python 3.11
* FAISS Vector Search
* RSS Feed Processing
* JSON Data Pipelines
* Fantasy Signal Scoring Engine
* CLI-Based Workflow

---

# 🔮 Roadmap

### Near-Term

* [ ] BUY / HOLD / SELL Recommendations
* [ ] Additional News Sources
* [ ] Historical Trend Analysis
* [ ] Automated Daily Updates

### Future

* [ ] Streamlit Dashboard
* [ ] Dynasty League Support
* [ ] LLM-Powered Draft Assistant
* [ ] Live Fantasy Draft Companion

---

## 👨‍💻 Author

Built by Alfredo Garza as part of an ongoing portfolio focused on AI, data engineering, automation, and sports analytics.
