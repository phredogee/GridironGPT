"""
Entity relationship engine for impact propagation.

This module converts a direct signal on one entity into downstream fantasy impacts.
It intentionally returns dictionaries to preserve compatibility with the current
Signal Impact API, recommendation engine, and Streamlit dashboard.
"""

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from gridiron_gpt.intelligence.relationships_loader import load_relationships

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Relationship:
    target: str
    relationship_type: str
    multiplier: float
    note: str = ""
    team: Optional[str] = None

    def __post_init__(self):
        if not self.target or not isinstance(self.target, str):
            raise ValueError("Relationship target must be a non-empty string.")

        if not isinstance(self.multiplier, (int, float)):
            raise ValueError("Relationship multiplier must be numeric.")

        if not 0.0 <= float(self.multiplier) <= 1.0:
            raise ValueError(
                f"Relationship multiplier must be between 0.0 and 1.0. "
                f"Got {self.multiplier} for {self.target}."
            )


@lru_cache(maxsize=128)
def get_related_entities(entity_name: str) -> tuple[Relationship, ...]:
    """
    Return configured relationships for a source entity.

    Results are cached to avoid repeatedly loading relationship data during
    scoring and dashboard rendering.
    """
    if not entity_name or not isinstance(entity_name, str):
        logger.warning("Invalid entity name passed to get_related_entities: %r", entity_name)
        return tuple()

    try:
        relationships = load_relationships()
    except Exception as exc:
        logger.error("Failed to load relationships: %s", exc)
        return tuple()

    raw_relationships = relationships.get(entity_name, [])
    related = []

    for raw in raw_relationships:
        try:
            related.append(
                Relationship(
                    target=raw["target"],
                    relationship_type=raw["relationship_type"],
                    multiplier=float(raw["multiplier"]),
                    note=raw.get("note", ""),
                    team=raw.get("team"),
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            logger.warning(
                "Skipping invalid relationship for %s: %r (%s)",
                entity_name,
                raw,
                exc,
            )

    return tuple(related)


def propagate_impact(
    entity_name: str,
    signal_score: float,
    max_hops: int = 1,
    _visited: Optional[set[str]] = None,
) -> list[dict]:
    """
    Convert a direct signal into downstream fantasy impacts.

    Args:
        entity_name: Source player/entity receiving the direct signal.
        signal_score: Direct signal score.
        max_hops: Maximum relationship depth. Defaults to 1 for current behavior.
        _visited: Internal set used to avoid circular propagation.

    Returns:
        List of dictionaries compatible with the current Signal Impact API.
    """
    if _visited is None:
        _visited = set()

    if not entity_name or not isinstance(entity_name, str):
        logger.warning("Invalid entity name passed to propagate_impact: %r", entity_name)
        return []

    if not isinstance(signal_score, (int, float)):
        logger.warning("Invalid signal score for %s: %r", entity_name, signal_score)
        return []

    if max_hops <= 0:
        return []

    if entity_name in _visited:
        logger.debug("Circular relationship detected for %s. Stopping propagation.", entity_name)
        return []

    _visited.add(entity_name)

    related = get_related_entities(entity_name)
    impacts = []

    for relationship in related:
        propagated_score = round(float(signal_score) * relationship.multiplier, 2)

        impact = {
            "source": entity_name,
            "target": relationship.target,
            "relationship_type": relationship.relationship_type,
            "source_score": float(signal_score),
            "multiplier": relationship.multiplier,
            "propagated_score": propagated_score,
            "note": relationship.note,
            "team": relationship.team,
            "hop": len(_visited),
            "confidence": round(max(0.1, 1.0 - ((len(_visited) - 1) * 0.15)), 2),
        }

        impacts.append(impact)

        if max_hops > 1:
            impacts.extend(
                propagate_impact(
                    relationship.target,
                    propagated_score,
                    max_hops=max_hops - 1,
                    _visited=_visited.copy(),
                )
            )

    return impacts


def format_impacts(entity_name: str, signal_score: float) -> str:
    """Format propagated impacts as a human-readable report."""
    impacts = propagate_impact(entity_name, signal_score)

    if not impacts:
        return f"No related entity impacts found for {entity_name}."

    lines = [
        f"Impact propagation for {entity_name} (score: {signal_score:+.1f}):",
        "─" * 50,
    ]

    for impact in impacts:
        direction = "📈" if impact["propagated_score"] > 0 else "📉"

        lines.append(
            f"{direction} {impact['target']}: "
            f"{impact['propagated_score']:+.2f} "
            f"[{impact['relationship_type']}; "
            f"confidence: {impact['confidence']:.0%}]"
        )

        if impact.get("note"):
            lines.append(f"   Note: {impact['note']}")

    return "\n".join(lines)
