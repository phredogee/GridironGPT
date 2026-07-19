from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EvidenceNode:
    """One node in a Cortex causal evidence graph."""

    node_id: str
    faculty: str
    node_type: str
    summary: str

    entity_name: str | None = None

    parents: list[str] = field(default_factory=list)

    value: float | str | None = None

    reasons: list[str] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceGraph:
    """Structured causal graph explaining a Cortex recommendation."""

    entity_name: str
    action: str
    confidence: float

    root_node_ids: list[str] = field(default_factory=list)

    terminal_node_ids: list[str] = field(default_factory=list)

    nodes: list[EvidenceNode] = field(default_factory=list)

    def get_node(self, node_id: str) -> EvidenceNode | None:
        """Return a node by ID."""

        for node in self.nodes:
            if node.node_id == node_id:
                return node

        return None

    def get_children(self, node_id: str) -> list[EvidenceNode]:
        """Return nodes that directly depend on the supplied node."""

        return [
            node
            for node in self.nodes
            if node_id in node.parents
        ]

    def get_roots(self) -> list[EvidenceNode]:
        """Return the graph's root nodes."""

        return [
            node
            for node in self.nodes
            if node.node_id in self.root_node_ids
        ]

    def get_terminals(self) -> list[EvidenceNode]:
        """Return the graph's terminal decision nodes."""

        return [
            node
            for node in self.nodes
            if node.node_id in self.terminal_node_ids
        ]
