"""Cortex Reason faculty.

Models relationships, applies relationship semantics, and propagates effects
between connected entities.
"""

from gridiron_cortex.reason.relationship_engine import RelationshipEngine
from gridiron_cortex.reason.relationship_semantics import (
    RelationshipSemantic,
    RelationshipSemantics,
)

__all__ = [
    "RelationshipEngine",
    "RelationshipSemantic",
    "RelationshipSemantics",
]
