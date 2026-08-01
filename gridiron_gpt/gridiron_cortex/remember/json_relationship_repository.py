import json
from dataclasses import asdict
from pathlib import Path

from gridiron_cortex.models.entity_relationship import EntityRelationship
from gridiron_cortex.remember.relationship_repository import (
    RelationshipRepository,
)


class JsonRelationshipRepository(RelationshipRepository):
    """
    Append-only JSONL repository for relationship history.

    The latest matching snapshot represents the current relationship state.
    """

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.touch(exist_ok=True)

    def save(self, relationship: EntityRelationship) -> None:
        try:
            with self.file_path.open("a", encoding="utf-8") as file:
                file.write(json.dumps(asdict(relationship)) + "\n")
        except OSError as exc:
            raise RuntimeError(
                f"Unable to save relationship to: {self.file_path}"
            ) from exc

    def get_current(
        self,
        active_only: bool = True,
    ) -> list[EntityRelationship]:
        current = self._get_latest_relationships()

        relationships = list(current.values())

        if active_only:
            relationships = [
                relationship
                for relationship in relationships
                if relationship.active
            ]

        return relationships

    def get_outgoing(
        self,
        source_entity_id: str,
        active_only: bool = True,
    ) -> list[EntityRelationship]:
        current = self._get_latest_relationships()

        return [
            relationship
            for relationship in current.values()
            if relationship.source_entity_id == source_entity_id
            and (relationship.active or not active_only)
        ]

    def get_incoming(
        self,
        target_entity_id: str,
        active_only: bool = True,
    ) -> list[EntityRelationship]:
        current = self._get_latest_relationships()

        return [
            relationship
            for relationship in current.values()
            if relationship.target_entity_id == target_entity_id
            and (relationship.active or not active_only)
        ]

    def get_between(
        self,
        source_entity_id: str,
        target_entity_id: str,
        relationship_type: str | None = None,
    ) -> list[EntityRelationship]:
        relationships = []

        for relationship in self._read_all():
            if relationship.source_entity_id != source_entity_id:
                continue

            if relationship.target_entity_id != target_entity_id:
                continue

            if (
                relationship_type is not None
                and relationship.relationship_type != relationship_type
            ):
                continue

            relationships.append(relationship)

        return relationships

    def _get_latest_relationships(
        self,
    ) -> dict[tuple[str, str, str], EntityRelationship]:
        latest = {}

        for relationship in self._read_all():
            key = (
                relationship.source_entity_id,
                relationship.target_entity_id,
                relationship.relationship_type,
            )
            latest[key] = relationship

        return latest

    def _read_all(self) -> list[EntityRelationship]:
        relationships = []

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()

                    if not line:
                        continue

                    try:
                        record = json.loads(line)
                        relationships.append(
                            EntityRelationship(**record)
                        )
                    except (json.JSONDecodeError, TypeError):
                        continue

        except OSError as exc:
            raise RuntimeError(
                f"Unable to read relationships from: {self.file_path}"
            ) from exc

        return relationships
