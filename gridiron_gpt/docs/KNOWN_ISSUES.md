## Known Issues

## Statistical Signal Generation

Current implementation compares adjacent weekly appearances.

Future improvements

- Rolling 3-game baselines
- Rolling seasonal averages
- Position-specific thresholds
- Strength-of-schedule adjustments
- Opponent normalization

---

## News Ingestion

Current RSS feeds

- ESPN
- NBC
- RotoWire

Future improvements

- Additional team feeds
- Beat writer aggregation
- Duplicate headline clustering
- Source reliability scoring

---

## Player Matching

Current matcher prioritizes precision over recall.

Known limitations

- Ambiguous surnames are intentionally ignored.
- Headlines without identifiable player names are skipped.
- Nickname coverage is still expanding.

---

## Signal Confidence

Current confidence values are heuristic.

Future work

- Bayesian confidence
- Historical accuracy tracking
- Source weighting
- Multi-source agreement scoring

---

## Knowledge Graph

Relationship propagation currently relies on static graph definitions.

Future work

- Editable graph
- Graph persistence
- Automatic relationship discovery

---

## Current Limitations

### Relationship Semantics

All relationships currently use the same propagation algorithm.

Desired behavior:

* Different relationship types should propagate signals differently.
* Positive and negative events should use independent propagation multipliers.
* Signal category should influence propagation behavior.

---

### Generic Relationship Weights

Propagation currently relies on:

* relationship strength
* relationship confidence
* hop decay

Future versions should also consider:

* player importance
* position
* roster role
* historical influence
* organizational hierarchy

---

### Static Hop Decay

Current values:

```text
Hop 0 = 1.00
Hop 1 = 0.85
Hop 2 = 0.65
Hop 3 = 0.40
Hop 4+ = 0.20
```

Future work:

* configurable decay profiles
* relationship-specific decay
* signal-specific decay
* historical calibration

---

### Explanation Engine Integration

Propagation candidates generate reasoning chains, but those explanations are not yet surfaced to users.

Future goal:

```text
Joe Burrow Injury

↓

Ja'Marr Chase

↓

Reason

Quarterback → Receiver

↓

Primary passing relationship

↓

Weight 0.80

↓

Score Adjustment
```

---

### Cortex Inspector

The Cortex Inspector now visualizes:

- pipeline status
- evidence and confidence
- cognitive trace
- evidence graph
- propagation
- predictions
- player scorecards
- score history
- explanations
- diagnostics

The Propagation view currently exposes:

- direct impact
- downstream propagated impacts
- hop count
- propagation weight
- relationship strength
- relationship confidence
- propagation path

### Remaining Inspector Limitations

The Inspector does not yet provide:

- interactive node-based graph visualization
- clickable propagation nodes
- live animated pipeline execution
- side-by-side comparison of multiple players
- event markers over historical score charts
- filtering by propagation depth
- filtering by relationship type
- graph-level search
- historical propagation replay

These are presentation limitations rather than core engine blockers.

---

## Relationship Graph Refresh

The current NFL relationship graph is generated from:

- nflverse player catalog
- nflverse depth charts
- active roster status
- latest available team depth-chart snapshot

The initial depth-aware graph contains approximately 579 active relationships.

### Current Limitation

Relationship refresh is manual.

Running a full refresh repeatedly appends another set of relationship snapshots to:

```text
data/cortex/relationships.jsonl

---

### Score Engine Integration

Propagation impacts are generated correctly, but additional validation is needed to ensure:

* duplicate impacts are avoided
* repeated graph paths are consolidated
* multiple simultaneous signals aggregate correctly

---

### Historical Signal Validation

The propagation engine has not yet been validated against historical NFL data.

Future work:

* replay historical seasons
* compare propagated scores against actual fantasy outcomes
* tune relationship strengths and confidence values

---

### Relationship Learning

Relationship strengths are currently manually assigned.

Future versions may learn relationship values automatically using:

* historical fantasy scoring
* snap counts
* target share
* coaching tendencies
* player usage trends
* machine learning

---

### Performance

Current graph traversal is sufficient for development.

Before production, benchmark:

* traversal latency
* graph size scalability
* propagation throughput
* memory usage
* concurrent signal processing

---

## Future Enhancements

* Semantic relationship rules
* Directional propagation
* Signal category weighting
* Relationship confidence learning
* Automatic graph updates
* Visual graph exploration
* Explainable propagation reports
* Historical replay engine
* Graph analytics dashboard
* Multi-event conflict resolution

## Migration Status

Completed

✔ Cortex Facade
✔ Knowledge Service
✔ Knowledge Graph Manager
✔ Propagation Planner
✔ Relationship Engine integration
✔ Persistent repositories

Remaining

- Retire legacy semantic pipeline
- Retire duplicate CLI modules
- Complete PHRED migration
- Split Cortex into standalone repository

---

## Overall Status

| Component                       | Status     |
| ------------------------------- | ---------- |
| Knowledge Graph                 | ✅ Complete |
| Graph Traversal                 | ✅ Complete |
| Propagation Planner             | ✅ Complete |
| Multi-Hop Propagation           | ✅ Complete |
| Cycle Protection                | ✅ Complete |
| Strongest Path Selection        | ✅ Complete |
| Relationship Engine Integration | ✅ Complete |
| Semantic Propagation Rules      | 🚧 Planned |
| Explanation Integration         | 🚧 Planned |
| Cortex Inspector Visualization  | 🚧 Planned |
| Historical Validation           | 🚧 Planned |
| Machine-Learned Relationships   | 🔮 Future  |
