import streamlit as st


def render_evidence_graph_panel(result):
    """Render causal EvidenceGraph objects without external dependencies."""

    st.markdown("### Evidence Graph")
    st.caption(
        "Parent-child relationships showing how evidence "
        "contributed to each recommendation."
    )

    if not result.evidence_graphs:
        st.info("No causal evidence graph was generated.")
        return

    for graph_index, graph in enumerate(
        result.evidence_graphs,
        start=1,
    ):
        if len(result.evidence_graphs) > 1:
            st.markdown(
                f"#### Graph {graph_index}: {graph.entity_name}"
            )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Entity", graph.entity_name)

        with col2:
            st.metric("Decision", graph.action)

        with col3:
            st.metric(
                "Confidence",
                f"{graph.confidence:.1f}%",
            )

        nodes_by_id = {
            node.node_id: node
            for node in graph.nodes
        }

        children_by_parent: dict[str, list] = {}

        for node in graph.nodes:
            for parent_id in node.parents:
                children_by_parent.setdefault(
                    parent_id,
                    [],
                ).append(node)

        visited: set[str] = set()

        for root_id in graph.root_node_ids:
            root = nodes_by_id.get(root_id)

            if root is not None:
                _render_node(
                    node=root,
                    children_by_parent=children_by_parent,
                    visited=visited,
                    depth=0,
                )

        unvisited = [
            node
            for node in graph.nodes
            if node.node_id not in visited
        ]

        if unvisited:
            with st.expander("Unlinked graph nodes"):
                for node in unvisited:
                    _render_node_card(node, depth=0)


def _render_node(
    node,
    children_by_parent,
    visited,
    depth,
):
    if node.node_id in visited:
        return

    visited.add(node.node_id)
    _render_node_card(node, depth)

    children = children_by_parent.get(
        node.node_id,
        [],
    )

    for child in children:
        st.markdown(
            (
                f"<div style='margin-left:{depth * 24 + 12}px;"
                "font-size:1.2rem;'>└── ↓</div>"
            ),
            unsafe_allow_html=True,
        )

        _render_node(
            node=child,
            children_by_parent=children_by_parent,
            visited=visited,
            depth=depth + 1,
        )


def _render_node_card(node, depth):
    margin = depth * 24

    st.markdown(
        (
            f"<div style='margin-left:{margin}px;"
            "border:1px solid rgba(128,128,128,.35);"
            "border-radius:10px;"
            "padding:12px;"
            "margin-bottom:8px;'>"
            f"<strong>{node.faculty}</strong>"
            f" · {node.node_type.replace('_', ' ').title()}"
            f"<br>{node.summary}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    if node.reasons or node.metadata:
        with st.expander(
            f"Details — {node.faculty}: {node.node_type}",
        ):
            if node.entity_name:
                st.write(
                    f"**Entity:** {node.entity_name}"
                )

            if node.value is not None:
                st.write(
                    f"**Value:** {node.value}"
                )

            if node.reasons:
                st.markdown("**Reasons**")

                for reason in node.reasons:
                    st.write(f"- {reason}")

            if node.metadata:
                st.markdown("**Metadata**")
                st.json(node.metadata)
