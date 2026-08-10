from gridiron_cortex.models.entity_relationship import EntityRelationship
from apps.streamlit.pages.mission_control import (
    build_player_contexts,
    select_default_context,
)


def relationship(source_name: str, target_name: str):
    return EntityRelationship(
        source_entity_id=source_name.lower().replace(" ", "-"),
        source_entity_name=source_name,
        source_entity_type="player",
        target_entity_id=target_name.lower().replace(" ", "-"),
        target_entity_name=target_name,
        target_entity_type="player",
        relationship_type="throws_to",
        strength=0.9,
        confidence=0.9,
        source_team="HOU",
        target_team="HOU",
        active=True,
    )


def test_player_contexts_sort_by_adjusted_score():
    scores = {
        ("Tank Dell", "HOU"): {
            "score": 0.5,
            "adjusted_score": 0.8,
            "signals": [{"value": 0.5}],
        },
        ("C.J. Stroud", "HOU"): {
            "score": 1.2,
            "signals": [{"value": 1.0}, {"value": 0.2}],
        },
    }

    contexts = build_player_contexts(
        scores,
        [relationship("C.J. Stroud", "Tank Dell")],
    )

    assert [context.player for context in contexts] == [
        "C.J. Stroud",
        "Tank Dell",
    ]
    assert contexts[0].signal_count == 2


def test_player_contexts_exclude_zero_score_players():
    contexts = build_player_contexts(
        {
            ("Inactive Player", "UNK"): {
                "score": 0.0,
                "signals": [],
            }
        },
        [],
    )

    assert contexts == ()


def test_default_context_prefers_graph_connected_player():
    contexts = build_player_contexts(
        {
            ("Unconnected Star", "AAA"): {
                "score": 3.0,
                "signals": [{"value": 3.0}],
            },
            ("Tank Dell", "HOU"): {
                "score": 1.0,
                "signals": [{"value": 1.0}],
            },
        },
        [relationship("C.J. Stroud", "Tank Dell")],
    )

    selected = select_default_context(contexts)

    assert selected is not None
    assert selected.player == "Tank Dell"
    assert selected.entity_id == "tank-dell"
