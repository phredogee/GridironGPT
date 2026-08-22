from dataclasses import dataclass

from gridiron_cortex.explain.explanation_engine import ExplanationEngine
from gridiron_cortex.models.entity import Entity
from gridiron_cortex.models.impact import Impact
from gridiron_cortex.models.prediction import Prediction
from gridiron_cortex.models.recommendation import Recommendation
from gridiron_cortex.models.signal import Signal


@dataclass
class StubPlayer:
    player_name: str


@dataclass
class StubAvailability:
    value: str


@dataclass
class StubGame:
    week: int


@dataclass
class StubFootballContext:
    player: StubPlayer
    availability: StubAvailability
    next_game: StubGame | None
    opponent: str | None
    location: str | None
    bye_week: int | None


def make_signal() -> Signal:
    return Signal(headline="Tank Dell returned to first-team practice.", entities=[Entity(entity_type="player", name="Tank Dell", team="HOU")], sentiment="positive", impact_score=1.0, positive_hits=["returned", "first-team"], confidence=0.90, evidence={"reasons": ["Practice participation confirmed."]})


def make_impact() -> Impact:
    return Impact(entity_type="player", entity_name="Tank Dell", team="HOU", impact_score=1.0, impact_type="direct", reason="Primary player mentioned in signal.")


def make_prediction() -> Prediction:
    return Prediction(entity_id="tank-dell", entity_name="Tank Dell", horizon_days=14, projected_trend="RISING", current_score=55.0, projected_score=59.0, score_delta=4.0, confidence=0.80, reasons=["Positive recent momentum"])


def make_recommendation() -> Recommendation:
    return Recommendation(entity_type="player", entity_name="Tank Dell", team="HOU", action="BUY", confidence=83.0, score_delta=1.0, reasons=["Positive practice return", "14-day forecast: rising"])


def test_explain_preserves_plain_text_output() -> None:
    explanation = ExplanationEngine().explain(signal=make_signal(), impacts=[make_impact()], recommendations=[make_recommendation()], predictions=[make_prediction()])
    assert "Tank Dell is a BUY" in explanation
    assert "Forecast: RISING" in explanation
    assert "Football context:" not in explanation


def test_explain_adds_factual_football_context() -> None:
    context = StubFootballContext(player=StubPlayer("Tank Dell"), availability=StubAvailability("available"), next_game=StubGame(1), opponent="BUF", location="HOME", bye_week=8)
    explanation = ExplanationEngine().explain(signal=make_signal(), impacts=[make_impact()], recommendations=[make_recommendation()], predictions=[make_prediction()], football_context={"00-0039163": context})
    assert "Football context: Tank Dell is available." in explanation
    assert "Next game: Week 1 vs BUF home." in explanation
    assert "Bye week: 8." in explanation
    assert "favorable" not in explanation.casefold()
    assert "boost" not in explanation.casefold()


def test_builds_structured_evidence_chain() -> None:
    chain = ExplanationEngine().build_evidence_chains(signal=make_signal(), impacts=[make_impact()], predictions=[make_prediction()], recommendations=[make_recommendation()])[0]
    assert chain.entity_name == "Tank Dell"
    assert chain.action == "BUY"
    assert chain.confidence == 83.0
    assert [step.faculty for step in chain.steps] == ["Observe", "Understand", "Reason", "Evaluate", "Predict", "Decide"]


def test_chain_contains_propagation_reason() -> None:
    chain = ExplanationEngine().build_evidence_chains(signal=make_signal(), impacts=[make_impact()], predictions=[make_prediction()], recommendations=[make_recommendation()])[0]
    reason_step = next(step for step in chain.steps if step.faculty == "Reason")
    assert "Primary player mentioned" in reason_step.reasons[0]


def test_chain_works_without_prediction() -> None:
    chain = ExplanationEngine().build_evidence_chains(signal=make_signal(), impacts=[make_impact()], predictions=[], recommendations=[make_recommendation()])[0]
    faculties = [step.faculty for step in chain.steps]
    assert "Predict" not in faculties
    assert faculties[-1] == "Decide"


def test_no_recommendation_returns_no_chains() -> None:
    assert ExplanationEngine().build_evidence_chains(signal=make_signal(), impacts=[make_impact()], predictions=[make_prediction()], recommendations=[]) == []


def test_builds_causal_evidence_graph() -> None:
    graph = ExplanationEngine().build_evidence_graphs(signal=make_signal(), impacts=[make_impact()], predictions=[make_prediction()], recommendations=[make_recommendation()])[0]
    assert graph.entity_name == "Tank Dell"
    assert graph.action == "BUY"
    assert len(graph.get_roots()) == 1
    assert len(graph.get_terminals()) == 1
    assert graph.get_roots()[0].faculty == "Observe"
    assert graph.get_terminals()[0].faculty == "Decide"


def test_evidence_graph_contains_parent_links() -> None:
    graph = ExplanationEngine().build_evidence_graphs(signal=make_signal(), impacts=[make_impact()], predictions=[make_prediction()], recommendations=[make_recommendation()])[0]
    decide_node = graph.get_terminals()[0]
    assert decide_node.parents
    parent_faculties = {graph.get_node(parent_id).faculty for parent_id in decide_node.parents}
    assert "Evaluate" in parent_faculties
    assert "Predict" in parent_faculties


def test_evidence_graph_works_without_prediction() -> None:
    graph = ExplanationEngine().build_evidence_graphs(signal=make_signal(), impacts=[make_impact()], predictions=[], recommendations=[make_recommendation()])[0]
    faculties = {node.faculty for node in graph.nodes}
    assert "Predict" not in faculties
    assert "Decide" in faculties


def test_no_recommendation_returns_no_graphs() -> None:
    assert ExplanationEngine().build_evidence_graphs(signal=make_signal(), impacts=[make_impact()], predictions=[make_prediction()], recommendations=[]) == []


def test_propagated_impact_explanation_includes_relationship_context():
    impact = Impact(entity_type="player", entity_name="A.J. Brown", team="PHI", impact_score=0.767, impact_type="propagated", reason="Jalen Hurts --throws_to(+1.00)--> A.J. Brown", hop_count=1, relationship_strength=0.95, relationship_confidence=0.95, propagation_weight=0.767)
    summary = ExplanationEngine._impact_summary(impact)
    assert "propagated impact" in summary
    assert "1-hop propagation" in summary
    assert "weight +0.767" in summary


def test_explain_surfaces_compound_event_developments_without_rescoring() -> None:
    signal = make_signal()
    signal.evidence["event_classifications"] = [
        {
            "category": "injury",
            "subtype": "returned_to_practice",
            "polarity": "positive",
            "confidence": 0.95,
            "impact": 0.8,
            "matched_rules": ["returned to practice"],
        },
        {
            "category": "depth_chart",
            "subtype": "first_team_reps",
            "polarity": "positive",
            "confidence": 0.93,
            "impact": 0.7,
            "matched_rules": ["first-team reps"],
        },
    ]

    original_impact = signal.impact_score
    explanation = ExplanationEngine().explain(
        signal=signal,
        impacts=[make_impact()],
        recommendations=[make_recommendation()],
        predictions=[make_prediction()],
    )

    assert (
        "Football developments detected: injury.returned_to_practice, "
        "depth_chart.first_team_reps."
    ) in explanation
    assert signal.impact_score == original_impact


def test_compound_developments_flow_into_structured_evidence_reasons() -> None:
    signal = make_signal()
    signal.evidence["event_classifications"] = [
        {
            "category": "performance",
            "subtype": "coach_praise",
        },
        {
            "category": "depth_chart",
            "subtype": "first_team_reps",
        },
    ]

    chain = ExplanationEngine().build_evidence_chains(
        signal=signal,
        impacts=[make_impact()],
        predictions=[],
        recommendations=[make_recommendation()],
    )[0]

    understand_step = next(
        step for step in chain.steps if step.faculty == "Understand"
    )
    assert "Detected football development: performance.coach_praise." in (
        understand_step.reasons
    )
    assert "Detected football development: depth_chart.first_team_reps." in (
        understand_step.reasons
    )
