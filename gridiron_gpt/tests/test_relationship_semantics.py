import pytest

from gridiron_cortex.reason.relationship_semantics import (
    RelationshipSemantic,
    RelationshipSemantics,
)


def test_unknown_relationship_preserves_existing_behavior() -> None:
    semantics = RelationshipSemantics()

    assert semantics.calculate_multiplier(
        "unknown_relationship",
        1.0,
    ) == 1.0

    assert semantics.calculate_multiplier(
        "unknown_relationship",
        -1.0,
    ) == 1.0


def test_passes_to_moves_in_same_direction() -> None:
    semantics = RelationshipSemantics()

    assert semantics.calculate_multiplier(
        "passes_to",
        1.0,
    ) == 1.0

    assert semantics.calculate_multiplier(
        "passes_to",
        -1.0,
    ) == 0.85


def test_competes_with_reverses_positive_signal() -> None:
    semantics = RelationshipSemantics()

    assert semantics.calculate_multiplier(
        "competes_with",
        1.0,
    ) == -0.45


def test_competes_with_reverses_negative_signal() -> None:
    semantics = RelationshipSemantics()

    multiplier = semantics.calculate_multiplier(
        "competes_with",
        -1.0,
    )

    assert multiplier == -0.45
    assert -1.0 * multiplier > 0


def test_backs_up_rewards_starter_decline() -> None:
    semantics = RelationshipSemantics()

    multiplier = semantics.calculate_multiplier(
        "backs_up",
        -1.0,
    )

    assert multiplier == -0.65
    assert -1.0 * multiplier > 0


def test_zero_signal_has_zero_multiplier() -> None:
    semantics = RelationshipSemantics()

    assert semantics.calculate_multiplier(
        "passes_to",
        0.0,
    ) == 0.0


def test_relationship_type_is_normalized() -> None:
    semantics = RelationshipSemantics()

    assert semantics.get("Target Competitor") == semantics.get(
        "target_competitor"
    )

    assert semantics.get("depth-chart-competitor") == semantics.get(
        "depth_chart_competitor"
    )


def test_custom_semantic_can_be_registered() -> None:
    semantics = RelationshipSemantics()

    custom = RelationshipSemantic(
        relationship_type="custom",
        positive_multiplier=0.25,
        negative_multiplier=-0.50,
        description="Custom test relationship.",
    )

    semantics.register("custom relationship", custom)

    assert semantics.get("custom_relationship") is custom


def test_empty_relationship_type_cannot_be_registered() -> None:
    semantics = RelationshipSemantics()

    with pytest.raises(ValueError):
        semantics.register(
            "",
            RelationshipSemantic(
                relationship_type="invalid",
            ),
        )
