from gridiron_cortex.understand.contradiction_detector import (
    ContradictionDetector,
)
from tests.builders import (
    build_canonical_event,
    build_source_evidence,
)


def test_empty_event_has_no_conflict():
    detector = ContradictionDetector()

    event = build_canonical_event(
        evidence=[],
    )

    result = detector.evaluate(event)

    assert result.has_conflict is False
    assert result.severity == 0.0
    assert result.confidence_penalty == 0.0
    assert result.conflicting_sources == []
    assert result.explanation == "No contradictory evidence found."


def test_single_source_has_no_conflict():
    detector = ContradictionDetector()

    event = build_canonical_event(
        evidence=[
            build_source_evidence(
                source="ESPN",
                headline="Tank Dell returns to practice.",
            )
        ],
    )

    result = detector.evaluate(event)

    assert result.has_conflict is False
    assert result.severity == 0.0

def test_mixed_sources_detect_conflict():
    detector = ContradictionDetector()

    event = build_canonical_event(
        evidence=[
            build_source_evidence(
                source="ESPN",
                headline="Tank Dell returns to practice.",
            ),
            build_source_evidence(
                source="NFL.com",
                headline="Tank Dell ruled out with injury.",
            ),
            build_source_evidence(
                source="NBC Sports",
                headline="Tank Dell returns to practice.",
            ),
        ]
    )

    result = detector.evaluate(event)

    assert result.has_conflict is True

def test_conflicting_sources_are_detected():
    detector = ContradictionDetector()

    event = build_canonical_event(
        evidence=[
            build_source_evidence(
                source="ESPN",
                headline="Tank Dell returns to practice.",
            ),
            build_source_evidence(
                source="NFL.com",
                headline="Tank Dell ruled out with injury.",
            ),
            build_source_evidence(
                source="NBC Sports",
                headline="Tank Dell returns to practice.",
            ),
        ]
    )

    result = detector.evaluate(event)

    assert result.has_conflict is True
    assert result.confidence_penalty == 0.20
    assert set(result.conflicting_sources) == {
        "ESPN",
        "NFL.com",
        "NBC Sports",
    }

def test_multiple_conflicts_increase_penalty():
    detector = ContradictionDetector()

    event = build_canonical_event(
        evidence=[
            build_source_evidence(
                source="ESPN",
                headline="Tank Dell returns to practice.",
            ),
            build_source_evidence(
                source="NFL.com",
                headline="Tank Dell ruled out with injury.",
            ),
            build_source_evidence(
                source="NBC Sports",
                headline="Tank Dell returns to practice.",
            ),
            build_source_evidence(
                source="CBS",
                headline="Tank Dell returns to practice.",
            ),
        ]
    )

    result = detector.evaluate(event)

    assert result.has_conflict is True
    assert result.confidence_penalty == 0.20

def test_confidence_penalty_is_capped():
    detector = ContradictionDetector()

    event = build_canonical_event(
        evidence=[
            build_source_evidence(
                source="A",
                headline="activated healthy returns",
            ),
            build_source_evidence(
                source="B",
                headline="cleared full practice starting",
            ),
            build_source_evidence(
                source="C",
                headline="injury inactive",
            ),
            build_source_evidence(
                source="D",
                headline="questionable benched limited",
            ),
        ]
    )

    result = detector.evaluate(event)

    # More than enough conflicting keywords to exceed the cap.
    assert result.confidence_penalty == 0.50
