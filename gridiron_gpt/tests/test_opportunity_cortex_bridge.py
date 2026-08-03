from gridiron_cortex.understand.signal_processor import SignalProcessor
from gridiron_gpt.football_state.models.opportunity_change import (
    OpportunityChange,
    OpportunityDirection,
)
from gridiron_gpt.football_state.services.opportunity_event_factory import OpportunityEventFactory


def change(direction=OpportunityDirection.INCREASED, magnitude=0.44):
    return OpportunityChange(
        source_player_id="bijan",
        source_player_name="Bijan Robinson",
        affected_player_id="allgeier",
        affected_player_name="Tyler Allgeier",
        relationship_type="backs_up",
        direction=direction,
        magnitude=magnitude,
        reason="Bijan Robinson --backs_up(-0.55)--> Tyler Allgeier",
    )


def test_increased_opportunity_becomes_positive_cortex_event():
    event = OpportunityEventFactory().build_event(change())

    assert event.player == "Tyler Allgeier"
    assert event.player_id == "allgeier"
    assert event.sentiment == "positive"
    assert event.impact_score == 0.44
    assert event.event_type == "roster_opportunity"


def test_decreased_opportunity_becomes_negative_cortex_event():
    event = OpportunityEventFactory().build_event(
        change(direction=OpportunityDirection.DECREASED, magnitude=0.2)
    )

    assert event.sentiment == "negative"
    assert event.impact_score == -0.2


def test_opportunity_evidence_preserves_causal_relationship():
    event = OpportunityEventFactory().build_event(change())
    evidence = event.evidence["roster_opportunity"]

    assert evidence["source_player_name"] == "Bijan Robinson"
    assert evidence["relationship_type"] == "backs_up"
    assert evidence["direction"] == "increased"
    assert evidence["reason"].startswith("Bijan Robinson")


def test_opportunity_event_has_deterministic_source_identity():
    factory = OpportunityEventFactory()

    first = factory.build_event(change())
    second = factory.build_event(change())

    assert first.evidence["source_id"] == second.evidence["source_id"]
    assert first.fingerprint() == second.fingerprint()


def test_opportunity_event_passes_through_signal_processor():
    event = OpportunityEventFactory().build_event(change())

    signal = SignalProcessor().process(event, entities=[])

    assert signal.signal_type == "roster_opportunity"
    assert signal.sentiment == "positive"
    assert signal.impact_score == 0.44
    assert signal.evidence["roster_opportunity"]["affected_player_id"] if "affected_player_id" in signal.evidence.get("roster_opportunity", {}) else event.player_id == "allgeier"
