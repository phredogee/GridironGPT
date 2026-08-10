def test_streamlit_components_import():
    from apps.streamlit.components.confidence_panel import (
        render_confidence_panel,
    )
    from apps.streamlit.components.evidence_graph_panel import (
        render_evidence_graph_panel,
    )
    from apps.streamlit.components.player_snapshot import (
        render_player_snapshot,
    )
    from apps.streamlit.components.recommendation_card import (
        render_recommendation_card,
    )

    assert callable(render_confidence_panel)
    assert callable(render_evidence_graph_panel)
    assert callable(render_player_snapshot)
    assert callable(render_recommendation_card)
