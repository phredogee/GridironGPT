"""Deprecated compatibility package.

Use :mod:`gridiron_cortex.remember` for new code.
"""

from gridiron_cortex.remember import (
    EventRepository,
    JsonEventRepository,
    JsonPlayerScorecardRepository,
    JsonRelationshipRepository,
    PlayerScorecardRepository,
    RelationshipRepository,
)

__all__ = [
    "EventRepository",
    "JsonEventRepository",
    "PlayerScorecardRepository",
    "JsonPlayerScorecardRepository",
    "RelationshipRepository",
    "JsonRelationshipRepository",
]
