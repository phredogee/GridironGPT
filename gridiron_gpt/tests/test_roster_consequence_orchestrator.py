from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.understand.signal_processor import SignalProcessor
from gridiron_gpt.football_state.models.opportunity_change import (
    OpportunityChange,
    OpportunityDirection,
)
from gridiron_gpt.football_state.services.roster_consequence_orchestrator import RosterConsequenceOrchestrator


class OpportunityService:
    def __init__(self, changes):
        self.changes = changes
        self.calls = []

    def derive(self, **kwargs):
        self.calls.append(kwargs)
        return self.changes


def source_event(**overrides):
    values = {
        "source": "canonical availability state",
        "headline": "Bijan Robinson placed on IR",
        "player": "Bijan Robinson",
        "player_id": "bijan",
        "team": "ATL",
        "event_type": "availability",
        "sentiment": "negative",
        "impact_score": -0.8,
        "confidence": 0.98,
        "evidence": {"source_id": "availability:bijan:ir"},
    }
    values.update(overrides)
    return RawEvent(**values)


def opportunity(player_id="allgeier", player_name="Tyler Allgeier", magnitude=0.44):
    return OpportunityChange(
        source_player_id="bijan",
        source_player_name="Bijan Robinson",
        affected_player_id=player_id,
        affected_player_name=player_name,
        relationship_type="backs_up",
        direction=OpportunityDirection.INCREASED,
        magnitude=magnitude,
        reason=f"Bijan Robinson --backs_up(-0.55)--> {player_name}",
    )


def test_source_event_derives_affected_player_opportunity_event():
    service = OpportunityService([opportunity()])
    orchestrator = RosterConsequenceOrchestrator(service)

    derived = orchestrator.derive_events(source_event())

    assert len(derived) == 1
    assert derived[0].player == "Tyler Allgeier"
    assert derived[0].impact_score == 0.44
    assert service.calls[0]["source_impact_score"] == -0.8


def test_multiple_affected_players_are_preserved():
    service = OpportunityService([
        opportunity(),
        opportunity("huntley", "Another ATL RB", 0.2),
    ])

    derived = RosterConsequenceOrchestrator(service).derive_events(source_event())

    assert [event.player for event in derived] == ["Tyler Allgeier", "Another ATL RB"]


def test_causal_chain_points_back_to_original_event():
    source = source_event()
    derived = RosterConsequenceOrchestrator(OpportunityService([opportunity()])).derive_events(source)

    causality = derived[0].evidence["causality"]
    assert causality["source_event_fingerprint"] == source.fingerprint()
    assert causality["source_player_id"] == "bijan"
    assert causality["derived"] is True


def test_duplicate_consequences_are_collapsed_within_one_pass():
    duplicate = opportunity()
    service = OpportunityService([duplicate, duplicate])

    derived = RosterConsequenceOrchestrator(service).derive_events(source_event())

    assert len(derived) == 1


def test_consequence_does_not_loop_back_to_source_player():
    self_change = opportunity("bijan", "Bijan Robinson")

    derived = RosterConsequenceOrchestrator(OpportunityService([self_change])).derive_events(source_event())

    assert derived == []


def test_derived_opportunity_event_is_terminal_for_orchestrator():
    derived_source = source_event(event_type="roster_opportunity", player="Tyler Allgeier", player_id="allgeier")
    service = OpportunityService([opportunity("bijan", "Bijan Robinson")])

    assert RosterConsequenceOrchestrator(service).derive_events(derived_source) == []
    assert service.calls == []


def test_unresolved_or_zero_impact_source_does_not_propagate():
    service = OpportunityService([opportunity()])
    orchestrator = RosterConsequenceOrchestrator(service)

    assert orchestrator.derive_events(source_event(player_id=None)) == []
    assert orchestrator.derive_events(source_event(impact_score=0.0)) == []
    assert service.calls == []


def test_derived_event_passes_through_normal_cortex_signal_processing():
    derived = RosterConsequenceOrchestrator(OpportunityService([opportunity()])).derive_events(source_event())

    signal = SignalProcessor().process(derived[0], entities=[])

    assert signal.signal_type == "roster_opportunity"
    assert signal.sentiment == "positive"
    assert signal.impact_score == 0.44
