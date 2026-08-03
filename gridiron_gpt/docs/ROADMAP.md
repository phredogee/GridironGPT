# GridironGPT Roadmap

## Vision

Build GridironGPT into a complete fantasy-football intelligence and commissioner platform powered by the reusable Gridiron Cortex engine.

## Current Status

| Area | Status |
|---|---|
| Cortex Foundation | Complete |
| Intelligence & Reasoning | Complete |
| Multi-source Ingestion | Complete / operational |
| Football Context | Operational and expanding |
| Fantasy Decision Engine | Operational and expanding |
| Commissioner Suite | Operational |
| Advisor 2.0 | Complete first pass |
| Dashboard 2.0 | Complete first pass |
| Visualization Layer | Operational |
| Cortex Explorer | Next |
| Knowledge Graph UI | Planned |
| Production / Cloud | Planned |

Current full regression checkpoint: **619 passed**.

## UI Modernization — Current

### Advisor 2.0 — Complete first pass
- Structured recommendation cards
- Confidence visualization
- Signal impact chart
- Supporting evidence/headlines
- Cortex timeline
- Health / Opportunity / Momentum / Risk / Upside profile
- Developer workflow collapsed by default

### Dashboard 2.0 — Complete first pass
- Live recommendation metrics
- Top BUY/WATCH/risk candidates
- Recommendation distribution
- Team momentum visualization
- Position rankings
- Live Cortex player rankings

### Cortex Explorer — Next
Create a player intelligence dossier containing:
- Current recommendation and confidence
- Multidimensional Cortex profile
- Score and confidence history
- Recent evidence timeline
- News history
- Related players and teams
- Propagation effects
- Injury/availability context
- Opportunity context

### Knowledge Graph Viewer
- Interactive player/team relationships
- Expandable graph navigation
- Relationship type and strength
- Propagation direction and effect
- Evidence path inspection

## Commissioner Analytics — Next

Build visual analytics on top of the completed Commissioner Suite:
- Schedule fairness
- Home/away balance
- Strength of schedule
- Luck Index
- Standings history
- Team performance history
- Rivalry and divisional schedule analysis

## Draft Center

Expand the existing draft-room foundation into a live draft command center:
- Snake and configurable draft formats
- Remaining player tiers
- Cortex draft value
- Roster construction
- Position scarcity
- Reach/value indicators
- Recommendations that exclude drafted players

## Intelligence Improvements

Continue improving the engine using live evidence:
- Player alias coverage
- Unknown-impact classification
- Injury/availability interpretation
- Opportunity and usage reconciliation
- Historical calibration
- Confidence calibration
- Relationship-effectiveness measurement

## Production / Cloud

After product workflows stabilize:
- Scheduled ingestion
- Durable database-first repositories
- Background workers/queues
- Authentication
- Multi-user and multi-league support
- Monitoring and alerting
- Backups
- Deployment automation
- Cost controls

## Guiding Principles

1. Cortex owns intelligence.
2. GridironGPT owns football-domain product behavior.
3. Evidence comes before conclusions.
4. Preserve provenance and history.
5. Prefer football semantics over generic math.
6. Keep infrastructure replaceable.
7. Make league settings configurable.
8. Keep visualization calculations separate from rendering.
9. Do not ship placeholder metrics when live values are available.
10. Maintain a passing regression suite after every major implementation batch.
