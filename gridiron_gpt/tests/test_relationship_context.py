from gridiron_cortex.models.signal import Signal
from gridiron_cortex.reason.relationship_context import RelationshipContextPolicy


def make_signal(classifications=None) -> Signal:
    evidence = {}
    if classifications is not None:
        evidence["event_classifications"] = classifications

    return Signal(
        headline="Test football report",
        sentiment="positive",
        impact_score=0.8,
        entities=[],
        evidence=evidence,
    )


def classification(category: str, subtype: str) -> dict:
    return {
        "category": category,
        "subtype": subtype,
        "polarity": "positive",
        "confidence": 0.9,
        "impact": 0.7,
        "matched_rules": [],
    }


def test_no_classifications_preserves_all_relationships() -> None:
    context = RelationshipContextPolicy().from_signal(make_signal())

    assert context.allowed_relationship_types is None
    assert context.allows("throws_to")
    assert context.allows("competes_with")


def test_unknown_classification_preserves_all_relationships() -> None:
    context = RelationshipContextPolicy().from_signal(
        make_signal([classification("performance", "coach_praise")])
    )

    assert context.allowed_relationship_types is None
    assert context.allows("teammate")
    assert context.allows("throws_to")


def test_first_team_reps_adds_opportunity_relationships() -> None:
    context = RelationshipContextPolicy().from_signal(
        make_signal([classification("depth_chart", "first_team_reps")])
    )

    assert context.allows("backs_up")
    assert context.allows("competes_with")
    assert context.allows("target_competitor")
    assert context.allows("depth_chart_competitor")
    assert context.allows("throws_to")
    assert context.allows("teammate")


def test_return_to_practice_adds_competition_relationships() -> None:
    context = RelationshipContextPolicy().from_signal(
        make_signal([classification("injury", "returned_to_practice")])
    )

    assert context.allows("backs_up")
    assert context.allows("competes_with")
    assert context.allows("depth_chart_competitor")
    assert not context.allows("target_competitor")
    assert context.allows("throws_to")
    assert context.allows("teammate")


def test_compound_classifications_union_relationship_context() -> None:
    context = RelationshipContextPolicy().from_signal(
        make_signal(
            [
                classification("injury", "returned_to_practice"),
                classification("depth_chart", "first_team_reps"),
                classification("performance", "coach_praise"),
            ]
        )
    )

    assert context.allows("backs_up")
    assert context.allows("competes_with")
    assert context.allows("depth_chart_competitor")
    assert context.allows("target_competitor")
    assert context.allows("throws_to")
    assert context.allows("teammate")


def test_relationship_type_normalization() -> None:
    context = RelationshipContextPolicy().from_signal(
        make_signal([classification("depth_chart", "first_team_reps")])
    )

    assert context.allows("Depth Chart Competitor")
    assert context.allows("depth-chart-competitor")
