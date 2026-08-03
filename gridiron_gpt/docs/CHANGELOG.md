# Changelog

## 2026-08-03 — Live Platform & UI Modernization

### Added
- Supabase-backed live signal loading into the player scoring path.
- Duplicate-safe raw article persistence for unique `story_hash` collisions.
- Shared visualization models and Streamlit intelligence charts.
- Advisor 2.0 recommendation, confidence, signal-impact, Cortex-profile, timeline, and supporting-headline views.
- Dashboard 2.0 recommendation distribution, team momentum, position rankings, and live Cortex ranking views.
- Expanded Commissioner Suite with configurable league settings, schedule generation, schedule alternatives/analytics, rivalry constraints, configurable playoff duration, draft workflows, league history, and schedule exports/delivery support.

### Changed
- Dashboard and Advisor now consume the live scored-player map rather than relying only on local/static presentation data.
- UI chart calculations are separated from Streamlit rendering.
- Project documentation now reflects the live product architecture and current roadmap.
- Commissioner scheduling treats divisional home/away requirements as hard constraints where configuration permits and optimizes remaining assignments for balance.

### Fixed
- Duplicate RSS stories no longer terminate ingestion with a Supabase unique-key error.
- Advisor top-recommendation confidence path typo corrected.
- Small-league schedule generation no longer assumes every schedule can achieve an impossible home/away spread.
- Schedule analytics quality scoring handles balanced reference schedules correctly.
- CSV and iCalendar schedule exports validated against generated schedules.

### Validation

```text
619 passed
```

This is the current full regression checkpoint.

### Next
- Cortex Explorer player dossier
- Interactive knowledge graph UI
- Dashboard ingestion activity/health feed
- Commissioner analytics visualizations
- Historical intelligence calibration

---

## Historical Milestones

The repository history and prior commits preserve the detailed development sequence for Cortex foundation, persistent intelligence, semantic propagation, nflverse integration, evidence reasoning, multidimensional scoring, ingestion reliability, football context, and earlier test checkpoints.
