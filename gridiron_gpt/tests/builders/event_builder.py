from datetime import datetime, timezone

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.models.canonical_event import CanonicalEvent
from gridiron_cortex.models.source_evidence import SourceEvidence
from gridiron_cortex.models.engine_context import EngineContext

def build_event(
    *,
    player: str = "Tank Dell",
    team: str = "HOU",
    headline: str = "Returns to first-team offense",
    source: str = "NBC Sports",
) -> RawEvent:
    return RawEvent(
        player=player,
        team=team,
        headline=headline,
        source=source,
        published_at=datetime.now(timezone.utc).isoformat(),
    )

def build_canonical_event(
    evidence=None,
    **kwargs,
) -> CanonicalEvent:

    defaults = {
        "event_key": "tank_dell",
        "player": "Tank Dell",
        "team": "HOU",
        "category": "injury",
        "subtype": "returned_to_practice",
        "polarity": "positive",
        "impact": 1.0,
        "confidence": 0.95,
        "evidence": evidence or [],
    }

    defaults.update(kwargs)
    return CanonicalEvent(**defaults)


def build_raw_event(**kwargs) -> RawEvent:
    defaults = {
        "headline": "Tank Dell returns to practice.",
        "source": "ESPN",
        "player": "Tank Dell",
        "team": "HOU",
    }

    defaults.update(kwargs)
    return RawEvent(**defaults)

def build_source_evidence(**kwargs) -> SourceEvidence:
    defaults = {
        "headline": "Tank Dell returns to practice.",
        "source": "ESPN",
        "confidence": 0.95,
    }
    defaults.update(kwargs)
    return SourceEvidence(**defaults)

def build_context(**kwargs) -> EngineContext:
    defaults = {
        "raw_event": build_raw_event(),
    }

    defaults.update(kwargs)
    return EngineContext(**defaults)
