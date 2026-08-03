from dataclasses import dataclass

from gridiron_gpt.football_state.models.opportunity_change import OpportunityDirection
from gridiron_gpt.football_state.services.roster_opportunity_service import RosterOpportunityService


@dataclass
class Candidate:
    entity_id: str
    entity_name: str
    propagation_weight: float
    reason: str


class Planner:
    def __init__(self, candidates):
        self.candidates = candidates
        self.calls = []

    def plan(self, **kwargs):
        self.calls.append(kwargs)
        return self.candidates


def candidate(relationship, weight, name="Tyler Allgeier"):
    return Candidate(
        entity_id="allgeier",
        entity_name=name,
        propagation_weight=weight,
        reason=f"Bijan Robinson --{relationship}(-0.65)--> {name}",
    )


def test_negative_starter_signal_increases_backup_opportunity():
    service = RosterOpportunityService(Planner([candidate("backs_up", -0.55)]))

    changes = service.derive(
        source_player_id="bijan",
        source_player_name="Bijan Robinson",
        source_impact_score=-0.8,
    )

    assert len(changes) == 1
    assert changes[0].direction == OpportunityDirection.INCREASED
    assert changes[0].affected_player_name == "Tyler Allgeier"
    assert changes[0].magnitude > 0


def test_positive_starter_signal_reduces_backup_opportunity():
    service = RosterOpportunityService(Planner([candidate("backs_up", -0.2)]))

    changes = service.derive(
        source_player_id="bijan",
        source_player_name="Bijan Robinson",
        source_impact_score=0.7,
    )

    assert changes[0].direction == OpportunityDirection.DECREASED


def test_competitor_relationship_is_interpreted_as_opportunity():
    service = RosterOpportunityService(Planner([candidate("competes_with", -0.4)]))

    changes = service.derive(
        source_player_id="bijan",
        source_player_name="Bijan Robinson",
        source_impact_score=-0.6,
    )

    assert changes[0].relationship_type == "competes_with"
    assert changes[0].direction == OpportunityDirection.INCREASED


def test_non_opportunity_relationship_is_ignored():
    service = RosterOpportunityService(Planner([candidate("teammate", 0.3)]))

    assert service.derive(
        source_player_id="bijan",
        source_player_name="Bijan Robinson",
        source_impact_score=-0.8,
    ) == []


def test_zero_source_impact_does_not_plan_propagation():
    planner = Planner([candidate("backs_up", -0.5)])
    service = RosterOpportunityService(planner)

    assert service.derive(
        source_player_id="bijan",
        source_player_name="Bijan Robinson",
        source_impact_score=0.0,
    ) == []
    assert planner.calls == []


def test_opportunity_derivation_uses_one_hop_relationships():
    planner = Planner([])
    service = RosterOpportunityService(planner)

    service.derive(
        source_player_id="bijan",
        source_player_name="Bijan Robinson",
        source_impact_score=-0.8,
    )

    assert planner.calls[0]["max_depth"] == 1
    assert planner.calls[0]["source_entity_id"] == "bijan"
