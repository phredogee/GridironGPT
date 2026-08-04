from __future__ import annotations

from enum import StrEnum


class CortexEventType(StrEnum):
    ARTICLE_RECEIVED = "article_received"
    PLAYER_RESOLVED = "player_resolved"
    SIGNAL_CREATED = "signal_created"
    SIGNAL_UPDATED = "signal_updated"
    PROPAGATION_COMPLETED = "propagation_completed"
    SCORE_UPDATED = "score_updated"
    RECOMMENDATION_CHANGED = "recommendation_changed"
    CONFIDENCE_UPDATED = "confidence_updated"
