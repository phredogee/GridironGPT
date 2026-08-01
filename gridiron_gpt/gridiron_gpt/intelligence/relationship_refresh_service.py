from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from gridiron_cortex.models.entity_relationship import (
    EntityRelationship,
)


RelationshipKey = tuple[str, str, str]


@dataclass(frozen=True)
class RelationshipRefreshResult:
    """
    Summary of one relationship-graph refresh.
    """

    proposed: int
    current: int

    new: int
    changed: int
    unchanged: int
    stale: int

    written: int


def _relationship_key(
    relationship: EntityRelationship,
) -> RelationshipKey:
    """
    Return the stable identity of a relationship.

    Relationship history may contain many snapshots, but source,
    target, and type identify the logical relationship.
    """

    return (
        relationship.source_entity_id,
        relationship.target_entity_id,
        relationship.relationship_type,
    )


def _relationship_state(
    relationship: EntityRelationship,
) -> tuple:
    """
    Return the fields that define meaningful relationship state.

    Timestamp fields are intentionally excluded so identical relationships
    are not treated as changed merely because they were regenerated later.
    """

    return (
        relationship.source_entity_name,
        relationship.source_entity_type,
        relationship.target_entity_name,
        relationship.target_entity_type,
        relationship.relationship_type,
        relationship.strength,
        relationship.confidence,
        relationship.reason,
        relationship.source_team,
        relationship.target_team,
        relationship.active,
    )


def _index_relationships(
    relationships: Iterable[EntityRelationship],
) -> dict[RelationshipKey, EntityRelationship]:
    """
    Index relationships by their stable graph key.
    """

    return {
        _relationship_key(relationship): relationship
        for relationship in relationships
    }


def _build_inactive_snapshot(
    relationship: EntityRelationship,
    timestamp: str,
) -> EntityRelationship:
    """
    Create an inactive snapshot for a relationship no longer present
    in the proposed graph.
    """

    return EntityRelationship(
        source_entity_id=relationship.source_entity_id,
        source_entity_name=relationship.source_entity_name,
        source_entity_type=relationship.source_entity_type,
        target_entity_id=relationship.target_entity_id,
        target_entity_name=relationship.target_entity_name,
        target_entity_type=relationship.target_entity_type,
        relationship_type=relationship.relationship_type,
        strength=relationship.strength,
        confidence=relationship.confidence,
        reason=relationship.reason,
        source_team=relationship.source_team,
        target_team=relationship.target_team,
        first_seen=relationship.first_seen,
        last_updated=timestamp,
        active=False,
    )


def _build_active_snapshot(
    proposed: EntityRelationship,
    previous: EntityRelationship | None,
    timestamp: str,
) -> EntityRelationship:
    """
    Normalize a new or changed relationship snapshot.

    Existing relationships preserve their original first_seen timestamp.
    """

    return EntityRelationship(
        source_entity_id=proposed.source_entity_id,
        source_entity_name=proposed.source_entity_name,
        source_entity_type=proposed.source_entity_type,
        target_entity_id=proposed.target_entity_id,
        target_entity_name=proposed.target_entity_name,
        target_entity_type=proposed.target_entity_type,
        relationship_type=proposed.relationship_type,
        strength=proposed.strength,
        confidence=proposed.confidence,
        reason=proposed.reason,
        source_team=proposed.source_team,
        target_team=proposed.target_team,
        first_seen=(
            previous.first_seen
            if previous is not None and previous.first_seen
            else proposed.first_seen or timestamp
        ),
        last_updated=timestamp,
        active=True,
    )


class RelationshipRefreshService:
    """
    Compare a newly generated relationship graph with Cortex's current
    persisted graph and write only meaningful state changes.
    """

    def __init__(self, knowledge_service):
        self.knowledge = knowledge_service

    def preview(
        self,
        proposed_relationships: list[EntityRelationship],
    ) -> RelationshipRefreshResult:
        """
        Compare proposed relationships to current graph state
        without persisting any changes.
        """

        current_relationships = (
            self.knowledge.get_current_relationships(
                active_only=True
            )
        )

        current_index = _index_relationships(
            current_relationships
        )

        proposed_index = _index_relationships(
            proposed_relationships
        )

        new_count = 0
        changed_count = 0
        unchanged_count = 0
        stale_count = 0

        for key, proposed in proposed_index.items():
            current = current_index.get(key)

            if current is None:
                new_count += 1
                continue

            if _relationship_state(current) == _relationship_state(
                proposed
            ):
                unchanged_count += 1
            else:
                changed_count += 1

        for key in current_index:
            if key not in proposed_index:
                stale_count += 1

        return RelationshipRefreshResult(
            proposed=len(proposed_index),
            current=len(current_index),
            new=new_count,
            changed=changed_count,
            unchanged=unchanged_count,
            stale=stale_count,
            written=0,
        )

    def refresh(
        self,
        proposed_relationships: list[EntityRelationship],
    ) -> RelationshipRefreshResult:
        timestamp = datetime.now(timezone.utc).isoformat()

        current_relationships = (
            self.knowledge.get_current_relationships(
                active_only=True
            )
        )

        current_index = _index_relationships(
            current_relationships
        )

        proposed_index = _index_relationships(
            proposed_relationships
        )

        new_count = 0
        changed_count = 0
        unchanged_count = 0
        stale_count = 0
        written_count = 0

        for key, proposed in proposed_index.items():
            current = current_index.get(key)

            if current is None:
                snapshot = _build_active_snapshot(
                    proposed=proposed,
                    previous=None,
                    timestamp=timestamp,
                )

                self.knowledge.save_relationship(snapshot)

                new_count += 1
                written_count += 1
                continue

            if _relationship_state(current) == _relationship_state(
                proposed
            ):
                unchanged_count += 1
                continue

            snapshot = _build_active_snapshot(
                proposed=proposed,
                previous=current,
                timestamp=timestamp,
            )

            self.knowledge.save_relationship(snapshot)

            changed_count += 1
            written_count += 1

        for key, current in current_index.items():
            if key in proposed_index:
                continue

            inactive = _build_inactive_snapshot(
                relationship=current,
                timestamp=timestamp,
            )

            self.knowledge.save_relationship(inactive)

            stale_count += 1
            written_count += 1

        return RelationshipRefreshResult(
            proposed=len(proposed_index),
            current=len(current_index),
            new=new_count,
            changed=changed_count,
            unchanged=unchanged_count,
            stale=stale_count,
            written=written_count,
        )
