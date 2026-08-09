from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import time

import streamlit as st

from gridiron_cortex.replay.replay_models import ReplayDecision, ReplayStage, ReplayStep

_STAGE_ICON = {ReplayStage.INGESTED: "📰", ReplayStage.RESOLVED: "👤", ReplayStage.UNDERSTOOD: "🧠", ReplayStage.PROPAGATED: "🔄", ReplayStage.SCORED: "🎯", ReplayStage.RECOMMENDED: "⭐", ReplayStage.CONFIDENCE: "📊"}

@dataclass(frozen=True, slots=True)
class ReplaySnapshot:
    step_number: int; total_steps: int; current: ReplayStep; visible_steps: tuple[ReplayStep, ...]; reached_stages: tuple[ReplayStage, ...]; recommendation: str | None; confidence: float | None

def replay_option_label(decision: ReplayDecision) -> str:
    player = decision.entity_name or "Cortex decision"; action = f" · {decision.recommendation}" if decision.recommendation else ""
    return f"{player}{action} · {decision.decision_id}"

def build_replay_snapshot(decision: ReplayDecision, step_number: int) -> ReplaySnapshot:
    if not decision.steps: raise ValueError("Replay decision has no steps")
    bounded = min(max(1, int(step_number)), len(decision.steps)); visible = decision.steps[:bounded]; stages = tuple(dict.fromkeys(step.stage for step in visible)); recommendation = None; confidence = None
    for step in visible:
        details = dict(step.details)
        if step.stage == ReplayStage.RECOMMENDED: recommendation = str(details.get("recommendation") or details.get("action") or details.get("label") or step.summary)
        if step.stage == ReplayStage.CONFIDENCE:
            value = details.get("confidence")
            if isinstance(value, (int, float)): confidence = float(value)
    return ReplaySnapshot(bounded, len(decision.steps), visible[-1], visible, stages, recommendation, confidence)

def replay_position(current: int, total: int, action: str) -> int:
    if total < 1: raise ValueError("Replay must contain at least one step")
    current = min(max(1, int(current)), total); actions = {"beginning": 1, "previous": current - 1, "next": current + 1, "end": total}
    if action not in actions: raise ValueError(f"Unknown replay action: {action}")
    return min(max(1, actions[action]), total)

def autoplay_next_position(current: int, total: int) -> tuple[int, bool]:
    """Advance autoplay one frame and report whether playback should continue."""
    if total < 1: raise ValueError("Replay must contain at least one step")
    current = min(max(1, int(current)), total)
    if current >= total: return total, False
    next_position = current + 1
    return next_position, next_position < total

def _confidence_text(value: float) -> str: return f"{value:.0%}" if value <= 1 else f"{value:.0f}%"
def _first(details: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = details.get(key)
        if value is not None and value != "": return value
    return None

def stage_card_fields(step: ReplayStep) -> tuple[tuple[str, str], ...]:
    d = dict(step.details); fields: list[tuple[str, str]] = []
    def add(label: str, value: Any, *, number: bool = False, confidence: bool = False) -> None:
        if value is None: return
        if confidence and isinstance(value, (int, float)): text = _confidence_text(float(value))
        elif number and isinstance(value, (int, float)): text = f"{float(value):+.3f}"
        else: text = str(value).replace("_", " ").title() if isinstance(value, str) and label in {"Type", "Polarity", "Relationship"} else str(value)
        fields.append((label, text))
    if step.stage == ReplayStage.RESOLVED:
        add("Entity", step.entity_name or _first(d, "entity_name", "name")); add("Team", d.get("team")); add("Position", d.get("position")); add("Resolution Confidence", d.get("confidence"), confidence=True)
    elif step.stage == ReplayStage.UNDERSTOOD:
        add("Type", _first(d, "signal_category", "signal_type", "type")); add("Polarity", _first(d, "polarity", "sentiment", "direction")); add("Impact", _first(d, "impact_score", "magnitude", "impact"), number=True); add("Signal Confidence", _first(d, "signal_confidence", "confidence"), confidence=True)
    elif step.stage == ReplayStage.PROPAGATED:
        impacts = d.get("impacts") or (); first_impact = next((item for item in impacts if isinstance(item, dict)), {})
        add("Impacts", d.get("impact_count") if d.get("impact_count") is not None else len(impacts)); add("Target", _first(first_impact, "entity_name", "target_name", "target")); add("Relationship", _first(first_impact, "relationship_type", "relationship")); add("Weight", _first(first_impact, "propagation_weight", "weight"), number=True); add("Projected Impact", _first(first_impact, "projected_impact", "impact", "impact_score"), number=True)
    elif step.stage == ReplayStage.SCORED:
        add("Entity", step.entity_name); add("Previous Score", _first(d, "previous_score", "old_score", "score_before")); add("New Score", _first(d, "new_score", "score", "score_after")); add("Delta", _first(d, "score_delta", "delta"), number=True)
    elif step.stage == ReplayStage.RECOMMENDED:
        add("Previous", _first(d, "previous_recommendation", "previous_action", "old_recommendation")); add("Recommendation", _first(d, "recommendation", "action", "label")); add("Confidence", d.get("confidence"), confidence=True); add("Reason", _first(d, "reason", "explanation", "rationale"))
    elif step.stage == ReplayStage.CONFIDENCE:
        add("Calibrated", _first(d, "calibrated_confidence", "confidence"), confidence=True); add("Recommendation", d.get("recommendation_confidence"), confidence=True); add("Signal", d.get("signal_confidence"), confidence=True)
    elif step.stage == ReplayStage.INGESTED:
        add("Source", step.source or d.get("source")); add("Headline", d.get("headline"))
    return tuple(fields)

def _render_stage_card(step: ReplayStep) -> None:
    fields = stage_card_fields(step)
    if not fields: return
    columns = st.columns(min(4, len(fields)))
    for index, (label, value) in enumerate(fields): columns[index % len(columns)].metric(label, value)

def render_replay_timeline(decision: ReplayDecision) -> None:
    status = "Complete" if decision.is_complete else "Partial"; st.caption(f"Decision ID `{decision.decision_id}` · {status} · {decision.stage_count} lifecycle stages")
    if decision.headline: st.markdown(f"**{decision.headline}**")
    if not decision.steps: st.info("This decision does not contain replay steps."); return
    position_key = f"replay_position_{decision.decision_id}"; playing_key = f"replay_playing_{decision.decision_id}"; speed_key = f"replay_speed_{decision.decision_id}"
    if position_key not in st.session_state: st.session_state[position_key] = len(decision.steps)
    if playing_key not in st.session_state: st.session_state[playing_key] = False
    controls = st.columns([1, 1, 1, 1, 1, 1.15])
    actions = (("⏮ Beginning", "beginning"), ("◀ Previous", "previous"))
    for column, (label, action) in zip(controls[:2], actions):
        if column.button(label, key=f"replay_{action}_{decision.decision_id}", use_container_width=True): st.session_state[playing_key] = False; st.session_state[position_key] = replay_position(st.session_state[position_key], len(decision.steps), action)
    play_label = "⏸ Pause" if st.session_state[playing_key] else "▶ Play"
    if controls[2].button(play_label, key=f"replay_play_{decision.decision_id}", use_container_width=True):
        if st.session_state[playing_key]: st.session_state[playing_key] = False
        else:
            if st.session_state[position_key] >= len(decision.steps): st.session_state[position_key] = 1
            st.session_state[playing_key] = True
    for column, (label, action) in zip(controls[3:5], (("Next ▶", "next"), ("End ⏭", "end"))):
        if column.button(label, key=f"replay_{action}_{decision.decision_id}", use_container_width=True): st.session_state[playing_key] = False; st.session_state[position_key] = replay_position(st.session_state[position_key], len(decision.steps), action)
    speed = controls[5].selectbox("Speed", (0.5, 1.0, 1.5, 2.0), index=1, format_func=lambda value: f"{value:g}×", key=speed_key, label_visibility="collapsed")
    step_number = st.slider("Replay position", min_value=1, max_value=len(decision.steps), step=1, key=position_key, help="Scrub directly through Cortex's reasoning state, or use the playback controls above.")
    snapshot = build_replay_snapshot(decision, step_number)
    c1, c2, c3 = st.columns(3); c1.metric("Playback", f"{snapshot.step_number}/{snapshot.total_steps}"); c2.metric("Current Stage", snapshot.current.stage.value.title()); current_recommendation = snapshot.recommendation or (decision.recommendation if snapshot.step_number == snapshot.total_steps else "Pending"); c3.metric("Recommendation", current_recommendation)
    reached = " → ".join(stage.value.title() for stage in snapshot.reached_stages); st.caption(f"State reached: {reached}")
    if snapshot.confidence is not None: st.caption(f"Confidence at this point: {_confidence_text(snapshot.confidence)}")
    for index, step in enumerate(snapshot.visible_steps, start=1):
        icon = _STAGE_ICON.get(step.stage, "•"); marker = " ← current" if index == snapshot.step_number else ""; label = f"{index}. {icon} {step.stage.value.title()} — {step.title}{marker}"
        with st.expander(label, expanded=index == snapshot.step_number):
            st.write(step.summary); _render_stage_card(step); detail_meta = []
            if step.entity_name: detail_meta.append(f"Entity: {step.entity_name}")
            if step.source: detail_meta.append(f"Source: {step.source}")
            detail_meta.append(step.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")); st.caption(" · ".join(detail_meta))
            if step.details:
                with st.expander("Raw event payload", expanded=False): st.json(dict(step.details), expanded=True)
    hidden = snapshot.total_steps - snapshot.step_number
    if hidden: st.caption(f"{hidden} later replay step{'s' if hidden != 1 else ''} hidden at this playback position.")
    if st.session_state[playing_key]:
        next_position, keep_playing = autoplay_next_position(snapshot.step_number, snapshot.total_steps); time.sleep(0.8 / float(speed)); st.session_state[position_key] = next_position; st.session_state[playing_key] = keep_playing; st.rerun()
