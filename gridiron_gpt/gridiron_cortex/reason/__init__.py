"""Cortex Reason faculty.

Models relationships, applies relationship semantics, and propagates effects
between connected entities.

``RelationshipEngine`` is intentionally imported lazily. The engine depends on
``PropagationPlanner``, while the planner depends on relationship semantics.
Eagerly importing the engine from this package initializer therefore creates a
circular import when callers import the planner directly.
"""

from gridiron_cortex.reason.relationship_semantics import (
    RelationshipSemantic,
    RelationshipSemantics,
)

__all__ = [
    "RelationshipEngine",
    "RelationshipSemantic",
    "RelationshipSemantics",
]


def __getattr__(name: str):
    if name == "RelationshipEngine":
        from gridiron_cortex.reason.relationship_engine import RelationshipEngine

        return RelationshipEngine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
