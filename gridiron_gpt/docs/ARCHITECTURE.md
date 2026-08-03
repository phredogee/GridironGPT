# GridironGPT Architecture

## System Boundary

GridironGPT is the football product layer. **Gridiron Cortex** is the reusable intelligence engine.

### GridironGPT owns
- NFL provider integration and normalization
- Player catalog and aliases
- Football-specific relationships and league concepts
- Fantasy decision workflows
- Commissioner and draft workflows
- Streamlit presentation and visualization composition

### Cortex owns
- Evidence processing and entity resolution
- Signal interpretation
- Relationship reasoning and propagation
- Multidimensional scoring
- Prediction and recommendation
- Explanation and historical intelligence

## Runtime Architecture

```text
NFL Sources
  ├─ ESPN NFL RSS
  ├─ NBC NFL / ProFootballTalk
  ├─ RotoWire NFL
  └─ nflverse / nflreadpy
          ↓
GridironGPT Ingestion
          ↓
Normalize / Resolve / Deduplicate
          ↓
Supabase live articles + signals
          ↓
Gridiron Cortex
 Observe → Understand → Reason → Evaluate
       → Predict → Decide → Explain → Remember
          ↓
Player Scores / Recommendations / Evidence
          ↓
Visualization Models
          ↓
Streamlit Components
          ↓
Dashboard / Advisor / Players / Commissioner
```

## Live Data Path

```text
RSS item
  ↓
player resolution + impact classification
  ↓
raw article / signal persistence
  ↓
news_loader merges persisted + local evidence
  ↓
calculate_player_scores()
  ↓
Cortex-adjusted scores
  ↓
Advisor / Dashboard
```

Database uniqueness protects `story_hash`; duplicate stories are treated as normal skipped evidence rather than fatal ingestion errors.

## Intelligence and Propagation

Cortex maintains football relationships such as `throws_to`, `hands_off_to`, `backs_up`, `target_competitor`, and `depth_chart_competitor`. Propagation uses relationship strength, confidence, semantic direction, and hop decay. Strongest-path selection prevents duplicate graph paths from multiplying the same downstream effect.

## Scoring

Persistent player intelligence includes Overall, Opportunity, Health, Hype, Risk, and Momentum dimensions. Presentation may derive simplified profiles from scored evidence while the long-term UI should expose engine-owned multidimensional scorecards directly.

## Visualization Architecture

```text
scores / signals
      ↓
gridiron_gpt.intelligence.visualization_models
      ↓
chart-ready models
      ↓
apps.streamlit.components.intelligence_charts
      ↓
Advisor / Dashboard / Cortex Explorer
```

Current shared visualizations include confidence/signal agreement, signal-impact bars, Cortex timeline, recommendation distribution, team momentum, and position rankings. Presentation code must not become a second scoring engine.

## Advisor 2.0

Natural-language questions flow through `RosterAdvisor`, current Cortex scores, recommendation/confidence functions, supporting signals, and shared visualization components. Evidence is shown by default; developer workflow details are collapsed.

## Dashboard 2.0

The dashboard consumes the same scored-player map as the Advisor. It presents live summary metrics, BUY/WATCH/risk candidates, recommendation distribution, team momentum, position rankings, and the ranked-player table.

## Commissioner Architecture

Commissioner capabilities are deterministic league-product services and remain separate from Cortex scoring.

```text
League Settings
      ↓
Schedule Generator
      ↓
Constraint / Balance Logic
      ↓
Schedule Analytics / Alternatives
      ↓
Exports / Delivery
```

Other services cover playoff brackets, draft workflows, league history, and commissioner insights. Scheduling supports configurable teams, divisions, season length, playoff start, and playoff duration. Divisional home/away requirements are hard constraints where configuration permits; remaining assignments are optimized for balance.

## Persistence Strategy

The project currently uses a hybrid model: Supabase for live article/signal data plus repository abstractions for Cortex events, scorecards, relationships, and history. JSON/JSONL remain appropriate development implementations. Reasoning components depend on repository contracts rather than storage technology.

## UI Architecture

```text
streamlit_app.py
      ↓
App shell / navigation
      ↓
Page modules
      ↓
Reusable components
      ↓
View / visualization models
      ↓
Domain and Cortex services
```

Near-black structural surfaces, green interaction accents, and lighter input controls form the current visual language. Navigation behavior is owned by the shared app shell.

## Testing Boundary

Current full regression checkpoint:

```text
619 passed
```

Major feature batches must preserve this regression boundary.

## Next Architectural Work

1. Cortex Explorer unified player dossier.
2. Interactive knowledge-graph presentation.
3. Commissioner analytics visualizations.
4. Live ingestion activity/health on Dashboard 2.0.
5. Historical calibration and outcome replay.
6. Production persistence, scheduling, authentication, and background processing.
