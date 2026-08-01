from gridiron_cortex.explain.explanation_engine import ExplanationEngine
from gridiron_cortex.models.entity import Entity
from gridiron_cortex.models.impact import Impact
from gridiron_cortex.models.prediction import Prediction
from gridiron_cortex.models.recommendation import Recommendation
from gridiron_cortex.models.signal import Signal


def make_signal() -> Signal:
    return Signal(
        headline="Tank Dell returned to first-team practice.",
        entities=[
            Entity(
                entity_type="player",
                name="Tank Dell",
                team="HOU",
            )
        ],
        sentiment="positive",
        impact_score=1.0,
        positive_hits=["returned", "first-team"],
        confidence=0.90,
        evidence={
            "reasons": ["Practice participation confirmed."],
        },
    )


def make_impact() -> Impact:
    return Impact(
        entity_type="player",
        entity_name="Tank Dell",
        team="HOU",
        impact_score=1.0,
        impact_type="direct",
        reason="Primary player mentioned in signal.",
    )


def make_prediction() -> Prediction:
    return Prediction(
        entity_id="tank-dell",
        entity_name="Tank Dell",
        horizon_days=14,
        projected_trend="RISING",
        current_score=55.0,
        projected_score=59.0,
        score_delta=4.0,
        confidence=0.80,
        reasons=["Positive recent momentum"],
    )


def make_recommendation() -> Recommendation:
    return Recommendation(
        entity_type="player",
        entity_name="Tank Dell",
        team="HOU",
        action="BUY",
        confidence=83.0,
        score_delta=1.0,
        reasons=[
            "Positive practice return",
            "14-day forecast: rising",
        ],
    )


def test_explain_preserves_plain_text_output() -> None:
    engine = ExplanationEngine()

    explanation = engine.explain(
        signal=make_signal(),
        impacts=[make_impact()],
        recommendations=[make_recommendation()],
        predictions=[make_prediction()],
    )

    assert "Tank Dell is a BUY" in explanation
    assert "Forecast: RISING" in explanation


def test_builds_structured_evidence_chain() -> None:
    engine = ExplanationEngine()

    chains = engine.build_evidence_chains(
        signal=make_signal(),
        impacts=[make_impact()],
        predictions=[make_prediction()],
        recommendations=[make_recommendation()],
    )

    assert len(chains) == 1

    chain = chains[0]

    assert chain.entity_name == "Tank Dell"
    assert chain.action == "BUY"
    assert chain.confidence == 83.0

    faculties = [
        step.faculty
        for step in chain.steps
    ]

    assert faculties == [
        "Observe",
        "Understand",
        "Reason",
        "Evaluate",
        "Predict",
        "Decide",
    ]


def test_chain_contains_propagation_reason() -> None:
    engine = ExplanationEngine()

    chain = engine.build_evidence_chains(
        signal=make_signal(),
        impacts=[make_impact()],
        predictions=[make_prediction()],
        recommendations=[make_recommendation()],
    )[0]

    reason_step = next(
        step
        for step in chain.steps
        if step.faculty == "Reason"
    )

    assert "Primary player mentioned" in reason_step.reasons[0]


def test_chain_works_without_prediction() -> None:
    engine = ExplanationEngine()

    chain = engine.build_evidence_chains(
        signal=make_signal(),
        impacts=[make_impact()],
        predictions=[],
        recommendations=[make_recommendation()],
    )[0]

    faculties = [
        step.faculty
        for step in chain.steps
    ]

    assert "Predict" not in faculties
    assert faculties[-1] == "Decide"


def test_no_recommendation_returns_no_chains() -> None:
    engine = ExplanationEngine()

    chains = engine.build_evidence_chains(
        signal=make_signal(),
        impacts=[make_impact()],
        predictions=[make_prediction()],
        recommendations=[],
    )

    assert chains == []

def test_builds_causal_evidence_graph() -> None:
    engine = ExplanationEngine()

    graphs = engine.build_evidence_graphs(
        signal=make_signal(),
        impacts=[make_impact()],
        predictions=[make_prediction()],
        recommendations=[make_recommendation()],
    )

    assert len(graphs) == 1

    graph = graphs[0]

    assert graph.entity_name == "Tank Dell"
    assert graph.action == "BUY"
    assert len(graph.get_roots()) == 1
    assert len(graph.get_terminals()) == 1

    root = graph.get_roots()[0]
    terminal = graph.get_terminals()[0]

    assert root.faculty == "Observe"
    assert terminal.faculty == "Decide"


def test_evidence_graph_contains_parent_links() -> None:
    engine = ExplanationEngine()

    graph = engine.build_evidence_graphs(
        signal=make_signal(),
        impacts=[make_impact()],
        predictions=[make_prediction()],
        recommendations=[make_recommendation()],
    )[0]

    decide_node = graph.get_terminals()[0]

    assert decide_node.parents

    parent_faculties = {
        graph.get_node(parent_id).faculty
        for parent_id in decide_node.parents
    }

    assert "Evaluate" in parent_faculties
    assert "Predict" in parent_faculties


def test_evidence_graph_works_without_prediction() -> None:
    engine = ExplanationEngine()

    graph = engine.build_evidence_graphs(
        signal=make_signal(),
        impacts=[make_impact()],
        predictions=[],
        recommendations=[make_recommendation()],
    )[0]

    faculties = {
        node.faculty
        for node in graph.nodes
    }

    assert "Predict" not in faculties
    assert "Decide" in faculties


def test_no_recommendation_returns_no_graphs() -> None:
    engine = ExplanationEngine()

    graphs = engine.build_evidence_graphs(
        signal=make_signal(),
        impacts=[make_impact()],
        predictions=[make_prediction()],
        recommendations=[],
    )

    assert graphs == []

def test_propagated_impact_explanation_includes_relationship_context():
    impact = Impact(
        entity_type="player",
        entity_name="A.J. Brown",
        team="PHI",
        impact_score=0.767,
        impact_type="propagated",
        reason=(
            "Jalen Hurts --throws_to(+1.00)--> "
            "A.J. Brown"
        ),
        hop_count=1,
        relationship_strength=0.95,
        relationship_confidence=0.95,
        propagation_weight=0.767,
    )

    summary = ExplanationEngine._impact_summary(impact)

    assert "propagated impact" in summary
    assert "1-hop propagation" in summary
    assert "weight +0.767" in summary
