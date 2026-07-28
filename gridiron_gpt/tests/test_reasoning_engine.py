from gridiron_cortex.models.canonical_event import CanonicalEvent
from gridiron_cortex.models.engine_context import EngineContext
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.models.reasoning_result import ReasoningResult
from gridiron_cortex.models.source_evidence import SourceEvidence
from gridiron_cortex.models.contradiction_result import (
    ContradictionResult,
)
from gridiron_cortex.reasoning.reasoning_engine import ReasoningEngine


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


def build_source_evidence(
    source: str,
    url: str,
) -> SourceEvidence:
    return SourceEvidence(
        source=source,
        url=url,
        headline="Tank Dell returns to practice.",
        confidence=0.95,
        metadata={},
    )


def build_canonical_event(
    evidence: list[SourceEvidence],
) -> CanonicalEvent:
    return CanonicalEvent(
        event_key="tank-dell-returned-to-practice",
        player="Tank Dell",
        team="HOU",
        category="injury",
        subtype="returned_to_practice",
        polarity="positive",
        impact=1.0,
        confidence=0.95,
        evidence=evidence,
    )


def test_reasoning_engine_returns_reasoning_result():
    context = EngineContext(
        raw_event=build_raw_event(),
    )

    result = ReasoningEngine().evaluate(context)

    assert isinstance(result, ReasoningResult)


def test_no_canonical_event_returns_unknown():
    context = EngineContext(
        raw_event=build_raw_event(),
    )

    result = ReasoningEngine().evaluate(context)

    assert result.confidence == 0.0
    assert result.certainty == "unknown"
    assert result.summary == "No canonical event available."
    assert result.supporting_evidence == []
    assert result.concerns == [
        "No evidence has been aggregated."
    ]
    assert result.recommendations == []


def test_single_source_returns_low_certainty():
    evidence = [
        build_source_evidence(
            source="ESPN",
            url="https://espn.com/test",
        )
    ]

    context = EngineContext(
        raw_event=build_raw_event(),
        canonical_event=build_canonical_event(evidence),
    )

    result = ReasoningEngine().evaluate(context)

    assert result.confidence == 0.95
    assert result.certainty == "low"
    assert result.summary == "Limited supporting evidence."
    assert result.supporting_evidence == []
    assert result.concerns == [
        "Only one source has reported this event."
    ]
    assert result.recommendations == [
        "Wait for additional corroboration."
    ]

def test_high_quality_sources_return_high_certainty():
    evidence = [
        build_source_evidence(
            source="ESPN",
            url="https://espn.com/test",
        ),
        build_source_evidence(
            source="NFL.com",
            url="https://nfl.com/test",
        ),
        build_source_evidence(
            source="NBC Sports",
            url="https://nbcsports.com/test",
        ),
    ]

    context = EngineContext(
        raw_event=build_raw_event(),
        canonical_event=build_canonical_event(evidence),
    )

    result = ReasoningEngine().evaluate(context)

    assert result.confidence == 0.95
    assert result.certainty == "high"
    assert result.average_reliability >= 0.90
    assert result.summary == "Evidence quality evaluated."
    assert result.supporting_evidence == [
        "3 independent sources",
        f"Average reliability: {result.average_reliability:.2f}",
    ]
    assert result.concerns == []
    assert result.recommendations == []

def test_unknown_sources_return_low_certainty():
    evidence = [
        build_source_evidence(
            source="Fantasy Blog",
            url="https://fantasy-blog.example/test",
        ),
        build_source_evidence(
            source="Unknown RSS",
            url="https://unknown-rss.example/test",
        ),
        build_source_evidence(
            source="My Website",
            url="https://my-website.example/test",
        ),
    ]

    context = EngineContext(
        raw_event=build_raw_event(),
        canonical_event=build_canonical_event(evidence),
    )

    result = ReasoningEngine().evaluate(context)

    assert result.confidence == 0.95
    assert result.certainty == "low"
    assert result.average_reliability < 0.80
    assert result.summary == "Evidence quality evaluated."
    assert result.supporting_evidence == [
        "3 independent sources",
        f"Average reliability: {result.average_reliability:.2f}",
    ]
    assert result.concerns == []
    assert result.recommendations == []

def test_conflict_reduces_certainty():
    evidence = [
        build_source_evidence(
            source="ESPN",
            url="https://espn.com/test",
        ),
        build_source_evidence(
            source="NFL.com",
            url="https://nfl.com/test",
        ),
        build_source_evidence(
            source="NBC Sports",
            url="https://nbcsports.com/test",
        ),
    ]

    context = EngineContext(
        raw_event=build_raw_event(),
        canonical_event=build_canonical_event(evidence),
    )

    context.contradiction = ContradictionResult(
        has_conflict=True,
        severity="moderate",
        confidence_penalty=0.20,
        conflicting_sources=[
            "ESPN",
            "NFL.com",
        ],
        explanation="Trusted sources disagree.",
    )

    result = ReasoningEngine().evaluate(context)

    assert result.certainty == "moderate"
    assert result.confidence == 0.75
    assert "Trusted sources disagree." in result.concerns


def test_no_conflict_preserves_high_certainty():
    evidence = [
        build_source_evidence(
            source="ESPN",
            url="https://espn.com/test",
        ),
        build_source_evidence(
            source="NFL.com",
            url="https://nfl.com/test",
        ),
        build_source_evidence(
            source="NBC Sports",
            url="https://nbcsports.com/test",
        ),
    ]

    context = EngineContext(
        raw_event=build_raw_event(),
        canonical_event=build_canonical_event(evidence),
        contradiction=ContradictionResult(),
    )

    result = ReasoningEngine().evaluate(context)

    assert result.certainty == "high"
    assert result.confidence == 0.95
    assert result.concerns == []



