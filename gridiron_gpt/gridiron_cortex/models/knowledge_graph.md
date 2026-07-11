from dataclasses import dataclass, field

from gridiron_cortex.models.entity_relationship import EntityRelationship


@dataclass
class GraphNode:
    entity_id: str
    entity_name: str
    entity_type: str
    team: str | None = None


@dataclass
class GraphEdge:
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    strength: float
    confidence: float
    active: bool = True
    reason: str = ""


@dataclass
class KnowledgeGraph:
    root_entity_id: str
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)


@dataclass
class RelationshipPath:
    source_entity_id: str
    target_entity_id: str
    relationships: list[EntityRelationship] = field(
        default_factory=list
    )

    @property
    def hop_count(self) -> int:
        return len(self.relationships)

    @property
    def combined_strength(self) -> float:
        result = 1.0

        for relationship in self.relationships:
            result *= relationship.strength

        return result

    @property
    def combined_confidence(self) -> float:
        result = 1.0

        for relationship in self.relationships:
            result *= relationship.confidence

        return result
