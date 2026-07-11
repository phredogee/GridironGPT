# Known Issues

## Current

- RSS ingestion currently generates relatively few signals.
- Player catalog coverage is incomplete.
- Some valid players are not detected.
- Duplicate article handling exists but duplicate signal detection does not.
- Signal decay has not been implemented.
- Recency weighting has not been implemented.
- Score history persistence has not been implemented.
- Source reliability scoring has not been implemented.

## Metrics Snapshot

Latest RSS Run:

Articles Found: 27
Signals Saved: 5
Skipped: 22

Primary Bottleneck:
Player detection and impact classification.

# Graph Propagation Engine

## Status

**Partially Implemented**

The graph-based propagation framework is operational and tested. Several enhancements remain before it is considered production-ready.

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

The Cortex Inspector currently does not visualize:

* graph traversal
* propagation candidates
* hop counts
* propagation weights
* reasoning chains

A future update should expose the full propagation path for debugging and explainability.

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
