from gridiron_cortex.models.canonical_event import CanonicalEvent
from gridiron_cortex.models.source_evidence import SourceEvidence
from gridiron_cortex.evidence.evidence_analyzer import (
    EvidenceAnalyzer,
)

def make_evidence(
    source: str,
    category: str = "injury",
    subtype: str = "returned_to_practice",
    confidence: float = 0.95,
) -> SourceEvidence:
    return SourceEvidence(
        headline="Tank Dell returns to practice.",
        source=source,
        category=category,
        subtype=subtype,
        confidence=confidence,
        metadata={},
    )


def make_event(
    evidence: list[SourceEvidence],
) -> CanonicalEvent:
    return CanonicalEvent(
        event_key="tank_dell_practice",
        player="Tank Dell",
        team="HOU",
        category="injury",
        subtype="returned_to_practice",
        polarity="positive",
        impact=1.0,
        confidence=0.95,
        evidence=evidence,
    )


def test_single_source_is_developing():
    analyzer = EvidenceAnalyzer()

    assessment = analyzer.analyze(
        make_event([
            make_evidence("ESPN"),
        ])
    )

    assert assessment.source_count == 1
    assert assessment.independent_source_count == 1
    assert assessment.consensus_level == "single_source"
    assert assessment.developing_story is True


def test_multiple_agreeing_sources_have_strong_consensus():
    analyzer = EvidenceAnalyzer()

    assessment = analyzer.analyze(
        make_event([
            make_evidence("ESPN"),
            make_evidence("NFL.com"),
            make_evidence("NBC Sports"),
        ])
    )

    assert assessment.agreement_score == 1.0
    assert assessment.conflict_score == 0.0
    assert assessment.consensus_level == "strong"
    assert assessment.developing_story is False
    assert assessment.trust_score > 0.90


def test_conflicting_evidence_reduces_trust():
    analyzer = EvidenceAnalyzer()

    assessment = analyzer.analyze(
        make_event([
            make_evidence("ESPN"),
            make_evidence("NFL.com"),
            make_evidence(
                "NBC Sports",
                subtype="limited_practice",
            ),
        ])
    )

    assert assessment.agreement_score < 1.0
    assert assessment.conflict_score > 0.0
    assert assessment.consensus_level == "moderate"
    assert assessment.developing_story is False
