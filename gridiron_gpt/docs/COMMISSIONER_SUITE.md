# Commissioner Suite

## Purpose

The Commissioner Suite extends GridironGPT beyond player recommendations into league operations, schedule quality, playoff planning, historical records, and live draft support.

```text
League Settings
      ↓
Schedule / Playoffs / Draft / History
      ↓
Commissioner Analytics
      ↓
Streamlit Product App + REST-ready Services
```

## Implemented Capabilities

### Advanced Schedule Operations

- Divisional double round-robin guarantees
- Cross-division single meetings
- Exact divisional home/away reversal
- Balanced overall home/away totals
- Configurable regular-season and playoff duration
- Schedule quality score
- Longest home/away streak analysis
- Divisional-game distribution by week
- Repeat-opponent analysis
- Ranked home/away alternatives
- Constraint validation for maximum streaks, rivalry week, and consecutive repeat opponents

### Playoff Planning

- Four-team bracket
- Six-team bracket with top-two seed byes
- Eight-team bracket
- Round and matchup labels suitable for UI rendering and export

### League History

- Per-league, per-season JSON archive
- Champion and runner-up
- Final standings
- Schedule, draft, transaction, and award payloads
- Season discovery and retrieval

### Commissioner Insights

- Points-scored leader
- Best current record
- Expected-wins versus actual-wins luck signal
- Deterministic narrative output that can later be enriched by Cortex

### Live Draft Room

- Snake-order state machine
- On-the-clock tracking
- Duplicate and out-of-turn protection
- Draft board persistence in Streamlit session state
- Best-available recommendations using the Fantasy Decision Engine
- Roster-aware positional need bonus

### Export and Delivery

- CSV schedule export
- iCalendar (`.ics`) schedule export
- SMTP email with CSV attachment

## Streamlit

Launch:

```bash
streamlit run product_app.py
```

Product navigation now includes:

- Decision Center
- Commissioner Hub
- League Settings
- Schedule Generator
- API information

The Commissioner Hub contains Schedule Lab, Playoffs, League History, Insights, and Draft Room tabs.

## Current Boundaries

The following integrations require provider-specific work and are not represented as complete platform integrations yet:

- Direct write-back to CBS, ESPN, Yahoo, or Sleeper league schedules
- Automatic import of historical league seasons from those platforms
- Google Calendar account authorization and direct calendar insertion (the `.ics` export is available now)
- Fully generated PDF commissioner packets
- Multi-user authentication and cloud-backed shared draft-room state
- Live websocket draft synchronization

These belong naturally in Phase H or provider-specific integration work. The current services are designed so those adapters can be added without changing scheduling, bracket, history, or draft-domain logic.

## Validation

Focused tests cover:

- Schedule analytics
- Constraint validation
- Ranked schedule alternatives
- Four-, six-, and eight-team bracket behavior
- League-history persistence
- Commissioner insight generation
- Snake draft order and recommendation behavior
- CSV and iCalendar export
