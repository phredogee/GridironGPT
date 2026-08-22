import pytest

from gridiron_cortex.models.canonical_event import CanonicalEvent
from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.models.source_evidence import SourceEvidence
from gridiron_cortex.understand.signal_processor import SignalProcessor


def make_event(
    headline: str = "Tank Dell returns to practice.",
    source: str = "ESPN",
):
    return RawEvent(
        headline=headline,
        source=source,
    )


@pytest.fixture
def processor():
    return SignalProcessor()


def test_signal_without_canonical_event_defaults_to_one_source(
    processor,
):
    event = make_event()

    signal = processor.process(
        event,
        entities=[],
    )

    assert signal.source_count == 1
    assert signal.sources == ["ESPN"]
    assert signal.corroboration_confidence == signal.confidence


def test_signal_uses_canonical_event_sources(
    processor,
):
    event = make_event()

    canonical_event = CanonicalEvent(
        event_key="tank_practice",
        player="Tank Dell",
        team="HOU",
        category="injury",
        subtype="returned_to_practice",
        polarity="positive",
        impact=1.0,
        confidence=0.98,
        evidence=[
            SourceEvidence(
                source="ESPN",
                url="https://espn.com/1",
                headline="Tank Dell returns to practice.",
                category="injury",
                subtype="returned_to_practice",
                confidence=0.95,
                metadata={},
            ),
            SourceEvidence(
                source="NFL.com",
                url="https://nfl.com/1",
                headline="Tank Dell returns to practice.",
                category="injury",
                subtype="returned_to_practice",
                confidence=0.95,
                metadata={},
            ),
            SourceEvidence(
                source="NBC Sports",
                url="https://nbcsports.com/1",
                headline="Tank Dell returns to practice.",
                category="injury",
                subtype="returned_to_practice",
                confidence=0.95,
                metadata={},
            ),
        ],
    )

    signal = processor.process(
        event,
        entities=[],
        canonical_event=canonical_event,
    )

    assert signal.source_count == 3
    assert signal.sources == [
        "ESPN",
        "NFL.com",
        "NBC Sports",
    ]


def test_signal_uses_canonical_confidence(
    processor,
):
    event = make_event()

    canonical_event = CanonicalEvent(
        event_key="tank_practice",
        player="Tank Dell",
        team="HOU",
        category="injury",
        subtype="returned_to_practice",
        polarity="positive",
        impact=1.0,
        confidence=0.99,
        evidence=[
            SourceEvidence(
                source="ESPN",
                url="https://espn.com/1",
                headline="Tank Dell returns to practice.",
                category="injury",
                subtype="returned_to_practice",
                confidence=0.95,
                metadata={},
            ),
        ],
    )

    signal = processor.process(
        event,
        entities=[],
        canonical_event=canonical_event,
    )

    assert signal.confidence != signal.corroboration_confidence
    assert signal.corroboration_confidence == 0.99


def test_canonical_event_does_not_change_signal_interpretation(
    processor,
):
    event = make_event()

    without_canonical = processor.process(
        event,
        entities=[],
    )

    canonical_event = CanonicalEvent(
        event_key="tank_practice",
        player="Tank Dell",
        team="HOU",
        category="injury",
        subtype="returned_to_practice",
        polarity="positive",
        impact=1.0,
        confidence=0.99,
        evidence=[
            SourceEvidence(
                source="ESPN",
                category="injury",
                subtype="returned_to_practice",
                url="https://espn.com/1",
                headline="Tank Dell returns to practice.",
                confidence=0.95,
                metadata={},
            ),
        ],
    )

    with_canonical = processor.process(
        event,
        entities=[],
        canonical_event=canonical_event,
    )

    assert with_canonical.sentiment == without_canonical.sentiment
    assert with_canonical.impact_score == without_canonical.impact_score
    assert with_canonical.positive_hits == without_canonical.positive_hits
    assert with_canonical.negative_hits == without_canonical.negative_hits


def test_compound_event_preserves_all_classifications_in_one_signal(
    processor,
):
    event = RawEvent(
        headline="Receiver returned to practice and is working with the starters",
        summary="The receiver impressed the coaching staff.",
        source="RotoWire",
        player="Example Receiver",
    )

    signal = processor.process(event, entities=[])

    assert signal.evidence["event_classification"]["subtype"] == (
        "returned_to_practice"
    )
    assert [
        (item["category"], item["subtype"])
        for item in signal.evidence["event_classifications"]
    ] == [
        ("injury", "returned_to_practice"),
        ("depth_chart", "first_team_reps"),
        ("performance", "coach_praise"),
    ]
    assert signal.headline == event.headline


def test_single_classification_keeps_primary_and_collection_evidence(
    processor,
):
    event = RawEvent(
        headline="Player placed on injured reserve",
        source="ESPN",
        player="Example Player",
    )

    signal = processor.process(event, entities=[])

    assert signal.evidence["event_classification"]["subtype"] == "injured_reserve"
    assert len(signal.evidence["event_classifications"]) == 1
    assert signal.evidence["event_classifications"][0] == (
        signal.evidence["event_classification"]
    )
