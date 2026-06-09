from dataclasses import dataclass
from typing import Dict, List
from intelligence.relationships_loader import load_relationships

@dataclass
class Relationship:
    target: str
    relationship_type: str
    multiplier: float
    note: str = ""


ENTITY_RELATIONSHIPS: Dict[str, List[Relationship]] = {
    "Joe Burrow": [
        Relationship("Ja'Marr Chase", "qb_to_wr1", 0.35, "QB injury affects WR1 value"),
        Relationship("Tee Higgins", "qb_to_wr2", 0.30, "QB injury affects WR2 value"),
        Relationship("Chase Brown", "qb_to_rb", 0.15, "QB injury may affect offensive efficiency"),
    ],
    "Jalen Hurts": [
        Relationship("A.J. Brown", "qb_to_wr1", 0.35),
        Relationship("DeVonta Smith", "qb_to_wr2", 0.30),
        Relationship("Saquon Barkley", "qb_to_rb", 0.20),
    ],
    "Patrick Mahomes": [
        Relationship("Travis Kelce", "qb_to_te1", 0.35),
        Relationship("Rashee Rice", "qb_to_wr1", 0.30),
        Relationship("Isiah Pacheco", "qb_to_rb", 0.15),
    ],
}


def get_related_entities(entity_name: str) -> List[Relationship]:
    relationships = load_relationships()
    raw_relationships = relationships.get(entity_name, [])

    return [
        Relationship(
            target=r["target"],
            relationship_type=r["relationship_type"],
            multiplier=r["multiplier"],
            note=r.get("note", "")
        )
        for r in raw_relationships
    ]


def propagate_impact(entity_name: str, signal_score: float) -> List[dict]:
    """
    Converts a direct signal on one entity into downstream fantasy impacts.

    Example:
    Joe Burrow injury = -10
    Ja'Marr Chase receives -3.5
    Tee Higgins receives -3.0
    """

    related = get_related_entities(entity_name)
    impacts = []

    for relationship in related:
        propagated_score = round(signal_score * relationship.multiplier, 2)

        impacts.append(
            {
                "source": entity_name,
                "target": relationship.target,
                "relationship_type": relationship.relationship_type,
                "source_score": signal_score,
                "multiplier": relationship.multiplier,
                "propagated_score": propagated_score,
                "note": relationship.note,
            }
        )

    return impacts

def format_impacts(entity_name: str, signal_score: float) -> str:
    impacts = propagate_impact(entity_name, signal_score)

    if not impacts:
        return f"No related entity impacts found for {entity_name}."

    lines = [f"Impact propagation for {entity_name} ({signal_score}):"]

    for impact in impacts:
        lines.append(
            f"- {impact['target']}: {impact['propagated_score']} "
            f"({impact['relationship_type']})"
        )

    return "\n".join(lines)
