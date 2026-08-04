from __future__ import annotations

import streamlit as st

from gridiron_cortex.replay.replay_models import ReplayDecision, ReplayStage


_STAGE_ICON = {
    ReplayStage.INGESTED: "📰",
    ReplayStage.RESOLVED: "👤",
    ReplayStage.UNDERSTOOD: "🧠",
    ReplayStage.PROPAGATED: "🔄",
    ReplayStage.SCORED: "🎯",
    ReplayStage.RECOMMENDED: "⭐",
    ReplayStage.CONFIDENCE: "📊",
}


def replay_option_label(decision: ReplayDecision) -> str:
    player = decision.entity_name or "Cortex decision"
    action = f" · {decision.recommendation}" if decision.recommendation else ""
    return f"{player}{action} · {decision.decision_id}"


def render_replay_timeline(decision: ReplayDecision) -> None:
    """Render one replayable Cortex reasoning trail."""
    status = "Complete" if decision.is_complete else "Partial"
    st.caption(
        f"Decision ID `{decision.decision_id}` · {status} · "
        f"{decision.stage_count} lifecycle stages"
    )
    if decision.headline:
        st.markdown(f"**{decision.headline}**")
    meta = []
    if decision.source:
        meta.append(decision.source)
    if decision.recommendation:
        meta.append(f"Recommendation: {decision.recommendation}")
    if decision.confidence is not None:
        confidence = decision.confidence
        confidence_text = f"{confidence:.0%}" if confidence <= 1 else f"{confidence:.0f}%"
        meta.append(f"Confidence: {confidence_text}")
    if meta:
        st.caption(" · ".join(meta))

    for index, step in enumerate(decision.steps, start=1):
        icon = _STAGE_ICON.get(step.stage, "•")
        label = f"{index}. {icon} {step.stage.value.title()} — {step.title}"
        with st.expander(label, expanded=index == len(decision.steps)):
            st.write(step.summary)
            detail_meta = []
            if step.entity_name:
                detail_meta.append(f"Entity: {step.entity_name}")
            if step.source:
                detail_meta.append(f"Source: {step.source}")
            detail_meta.append(step.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"))
            st.caption(" · ".join(detail_meta))
            if step.details:
                st.json(dict(step.details), expanded=False)
