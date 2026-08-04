from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from gridiron_cortex.replay.replay_models import ReplayDecision, ReplayStage, ReplayStep


_STAGE_ICON = {
    ReplayStage.INGESTED: "📰",
    ReplayStage.RESOLVED: "👤",
    ReplayStage.UNDERSTOOD: "🧠",
    ReplayStage.PROPAGATED: "🔄",
    ReplayStage.SCORED: "🎯",
    ReplayStage.RECOMMENDED: "⭐",
    ReplayStage.CONFIDENCE: "📊",
}


@dataclass(frozen=True, slots=True)
class ReplaySnapshot:
    step_number: int
    total_steps: int
    current: ReplayStep
    visible_steps: tuple[ReplayStep, ...]
    reached_stages: tuple[ReplayStage, ...]
    recommendation: str | None
    confidence: float | None


def replay_option_label(decision: ReplayDecision) -> str:
    player = decision.entity_name or "Cortex decision"
    action = f" · {decision.recommendation}" if decision.recommendation else ""
    return f"{player}{action} · {decision.decision_id}"


def build_replay_snapshot(decision: ReplayDecision, step_number: int) -> ReplaySnapshot:
    """Reconstruct the observable decision state through one replay step."""
    if not decision.steps:
        raise ValueError("Replay decision has no steps")
    bounded = min(max(1, int(step_number)), len(decision.steps))
    visible = decision.steps[:bounded]
    stages = tuple(dict.fromkeys(step.stage for step in visible))
    recommendation = None
    confidence = None
    for step in visible:
        details = dict(step.details)
        if step.stage == ReplayStage.RECOMMENDED:
            recommendation = str(details.get("recommendation") or details.get("action") or details.get("label") or step.summary)
        if step.stage == ReplayStage.CONFIDENCE:
            value = details.get("confidence")
            if isinstance(value, (int, float)):
                confidence = float(value)
    return ReplaySnapshot(bounded, len(decision.steps), visible[-1], visible, stages, recommendation, confidence)


def _confidence_text(value: float) -> str:
    return f"{value:.0%}" if value <= 1 else f"{value:.0f}%"


def render_replay_timeline(decision: ReplayDecision) -> None:
    """Render an interactive, time-travel Cortex reasoning trail."""
    status = "Complete" if decision.is_complete else "Partial"
    st.caption(f"Decision ID `{decision.decision_id}` · {status} · {decision.stage_count} lifecycle stages")
    if decision.headline:
        st.markdown(f"**{decision.headline}**")

    if not decision.steps:
        st.info("This decision does not contain replay steps.")
        return

    step_number = st.slider(
        "Replay position",
        min_value=1,
        max_value=len(decision.steps),
        value=len(decision.steps),
        step=1,
        key=f"replay_position_{decision.decision_id}",
        help="Move backward through Cortex's reasoning state one event at a time.",
    )
    snapshot = build_replay_snapshot(decision, step_number)

    c1, c2, c3 = st.columns(3)
    c1.metric("Playback", f"{snapshot.step_number}/{snapshot.total_steps}")
    c2.metric("Current Stage", snapshot.current.stage.value.title())
    current_recommendation = snapshot.recommendation or (decision.recommendation if snapshot.step_number == snapshot.total_steps else "Pending")
    c3.metric("Recommendation", current_recommendation)

    reached = " → ".join(stage.value.title() for stage in snapshot.reached_stages)
    st.caption(f"State reached: {reached}")
    if snapshot.confidence is not None:
        st.caption(f"Confidence at this point: {_confidence_text(snapshot.confidence)}")

    for index, step in enumerate(snapshot.visible_steps, start=1):
        icon = _STAGE_ICON.get(step.stage, "•")
        marker = " ← current" if index == snapshot.step_number else ""
        label = f"{index}. {icon} {step.stage.value.title()} — {step.title}{marker}"
        with st.expander(label, expanded=index == snapshot.step_number):
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

    hidden = snapshot.total_steps - snapshot.step_number
    if hidden:
        st.caption(f"{hidden} later replay step{'s' if hidden != 1 else ''} hidden at this playback position.")
