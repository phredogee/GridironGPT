from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from gridiron_cortex.models.entity_relationship import EntityRelationship
from gridiron_cortex.models.propagation import PropagationCandidate


@dataclass(frozen=True, slots=True)
class ExplorerRelationship:
    entity_id: str
    entity_name: str
    team: str | None
    relationship_type: str
    direction: str
    strength: float
    confidence: float
    reason: str


@dataclass(frozen=True, slots=True)
class ExplorerPropagation:
    entity_id: str
    entity_name: str
    team: str | None
    hop_count: int
    strength: float
    confidence: float
    propagation_weight: float
    projected_impact: float
    reason: str


def find_entity_id(
    player_name: str,
    relationships: Iterable[EntityRelationship],
) -> str | None:
    """Resolve a relationship-graph entity ID from its player name."""
    normalized = player_name.strip().casefold()
    for relationship in relationships:
        if relationship.source_entity_name.strip().casefold() == normalized:
            return relationship.source_entity_id
        if relationship.target_entity_name.strip().casefold() == normalized:
            return relationship.target_entity_id
    return None


def build_relationship_rows(
    entity_id: str,
    relationships: Iterable[EntityRelationship],
) -> list[ExplorerRelationship]:
    """Return immediate incoming/outgoing relationships for Explorer."""
    rows: list[ExplorerRelationship] = []
    for relationship in relationships:
        if relationship.source_entity_id == entity_id:
            rows.append(
                ExplorerRelationship(
                    entity_id=relationship.target_entity_id,
                    entity_name=relationship.target_entity_name,
                    team=relationship.target_team,
                    relationship_type=relationship.relationship_type,
                    direction="outgoing",
                    strength=float(relationship.strength),
                    confidence=float(relationship.confidence),
                    reason=relationship.reason,
                )
            )
        elif relationship.target_entity_id == entity_id:
            rows.append(
                ExplorerRelationship(
                    entity_id=relationship.source_entity_id,
                    entity_name=relationship.source_entity_name,
                    team=relationship.source_team,
                    relationship_type=relationship.relationship_type,
                    direction="incoming",
                    strength=float(relationship.strength),
                    confidence=float(relationship.confidence),
                    reason=relationship.reason,
                )
            )
    return sorted(
        rows,
        key=lambda row: (-(row.strength * row.confidence), row.entity_name),
    )


def build_propagation_rows(
    candidates: Iterable[PropagationCandidate],
    source_impact: float,
) -> list[ExplorerPropagation]:
    """Convert semantic propagation candidates into Explorer rows."""
    rows = [
        ExplorerPropagation(
            entity_id=candidate.entity_id,
            entity_name=candidate.entity_name,
            team=candidate.team,
            hop_count=int(candidate.hop_count),
            strength=float(candidate.relationship_strength),
            confidence=float(candidate.relationship_confidence),
            propagation_weight=float(candidate.propagation_weight),
            projected_impact=round(
                float(source_impact) * float(candidate.propagation_weight),
                3,
            ),
            reason=candidate.reason,
        )
        for candidate in candidates
    ]
    return sorted(rows, key=lambda row: abs(row.projected_impact), reverse=True)
