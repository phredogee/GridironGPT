from __future__ import annotations

from enum import Enum

from gridiron_gpt.football_state.models.player_state import CanonicalPlayerState


class PlayerAvailability(str, Enum):
    """Provider-neutral player availability categories."""

    AVAILABLE = "available"
    RESERVE = "reserve"
    UNAVAILABLE = "unavailable"
    RETIRED = "retired"
    RELEASED = "released"
    EXEMPT = "exempt"
    UNKNOWN = "unknown"


class PlayerAvailabilityClassifier:
    """Translate provider roster codes into stable football-state semantics."""

    STATUS_MAP = {
        "ACT": PlayerAvailability.AVAILABLE,
        "RES": PlayerAvailability.RESERVE,
        "RET": PlayerAvailability.RETIRED,
        "CUT": PlayerAvailability.RELEASED,
        "E14": PlayerAvailability.EXEMPT,
    }

    @classmethod
    def classify(cls, state: CanonicalPlayerState) -> PlayerAvailability:
        status = (state.roster_status or "").strip().upper()
        if not status:
            return PlayerAvailability.UNKNOWN
        return cls.STATUS_MAP.get(status, PlayerAvailability.UNKNOWN)
