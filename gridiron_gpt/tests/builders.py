from gridiron_cortex.models.canonical_event import CanonicalEvent
from gridiron_cortex.models.engine_context import EngineContext
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.models.source_evidence import SourceEvidence


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
