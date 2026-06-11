# Intelligence Architecture

## Signal Flow

News / Injuries / Roster Moves
↓
Signal Scoring
↓
Player Score Calculation
↓
Entity Relationship Engine
↓
Signal Impact API
↓
Adjusted Player Scores
↓
Recommendations
↓
Dashboard / CLI Output

---

## Entity Relationship Engine

Purpose:

Model relationships between fantasy-relevant entities and propagate signal impacts across connected players.

Example:

Joe Burrow injury
↓
Ja'Marr Chase impact
↓
Tee Higgins impact
↓
Future offensive ecosystem impacts

---

## Components

### relationships.json

Stores relationship definitions.

Example:

```json
{
  "Joe Burrow": [
    {
      "target": "Ja'Marr Chase",
      "relationship_type": "qb_to_wr1",
      "multiplier": 0.35
    }
  ]
}
```

### relationships_loader.py

Responsibilities:

* Load relationship definitions
* Validate schema
* Return relationship mappings

### entity_relationships.py

Responsibilities:

* Relationship lookup
* Impact propagation
* Relationship traversal

### signal_impact_api.py

Responsibilities:

* Generate propagated impacts
* Calculate total system impact
* Produce standardized impact reports

---

## Future Roadmap

### V4

Automatic downstream signal generation.

### V5

Multi-hop propagation.

### V6

Relationship confidence weighting.

### V7

Graph-based ecosystem scoring.
