from gridiron_cortex.models.engine_context import EngineContext
from gridiron_cortex.models.raw_event import RawEvent


def build_raw_event() -> RawEvent:
    return RawEvent(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        player="Tank Dell",
        team="HOU",
        event_type="injury",
        published_at="2026-07-25T12:00:00+00:00",
        url="https://espn.com/test",
        sentiment="positive",
        impact_score=1.0,
        confidence=0.95,
    )


def test_engine_context_requires_raw_event():
    raw_event = build_raw_event()

    context = EngineContext(
        raw_event=raw_event,
    )

    assert context.raw_event is raw_event


def test_engine_context_defaults_are_empty():
    context = EngineContext(
        raw_event=build_raw_event(),
    )

    assert context.canonical_event is None
    assert context.contradiction is None

    assert context.entities == []
    assert context.signals == []
    assert context.impacts == []
    assert context.score_updates == []

    assert context.recommendation is None


def test_engine_context_lists_are_not_shared():
    first = EngineContext(
        raw_event=build_raw_event(),
    )

    second = EngineContext(
        raw_event=build_raw_event(),
    )

    first.entities.append("test")

    assert first.entities == ["test"]
    assert second.entities == []
