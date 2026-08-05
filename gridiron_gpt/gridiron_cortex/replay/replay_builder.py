from __future__ import annotations

from collections.abc import Iterable
from hashlib import sha256
from typing import Any

from gridiron_cortex.events.event import CortexEvent
from gridiron_cortex.events.event_types import CortexEventType
from gridiron_cortex.replay.replay_models import ReplayDecision, ReplayStage, ReplayStep


_STAGE_BY_EVENT = {
    CortexEventType.ARTICLE_RECEIVED: ReplayStage.INGESTED,
    CortexEventType.PLAYER_RESOLVED: ReplayStage.RESOLVED,
    CortexEventType.SIGNAL_CREATED: ReplayStage.UNDERSTOOD,
    CortexEventType.SIGNAL_UPDATED: ReplayStage.UNDERSTOOD,
    CortexEventType.PROPAGATION_COMPLETED: ReplayStage.PROPAGATED,
    CortexEventType.SCORE_UPDATED: ReplayStage.SCORED,
    CortexEventType.RECOMMENDATION_CHANGED: ReplayStage.RECOMMENDED,
    CortexEventType.CONFIDENCE_UPDATED: ReplayStage.CONFIDENCE,
}

_STAGE_ORDER = {stage: index for index, stage in enumerate(ReplayStage)}


def _number(payload: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def _confidence_from_payload(payload: dict[str, Any]) -> float | None:
    direct = _number(payload, "confidence", "calibrated_confidence", "signal_confidence")
    if direct is not None and direct > 0:
        return direct
    values = payload.get("recommendation_confidences") or ()
    for value in values:
        if isinstance(value, (int, float)) and float(value) > 0:
            return float(value)
    return direct


def _summary(event: CortexEvent) -> str:
    payload = dict(event.payload)
    if event.event_type == CortexEventType.ARTICLE_RECEIVED:
        return str(payload.get("headline") or "Evidence entered Cortex")
    if event.event_type == CortexEventType.PLAYER_RESOLVED:
        confidence = _number(payload, "confidence")
        metadata = [value for value in (payload.get("team"), payload.get("position")) if value]
        suffix = f" · {' · '.join(str(value) for value in metadata)}" if metadata else ""
        if confidence is not None:
            suffix += f" · {confidence:.0%}" if confidence <= 1 else f" · {confidence:.0f}%"
        return f"{event.entity_name or 'Entity resolved'}{suffix}"
    if event.event_type in {CortexEventType.SIGNAL_CREATED, CortexEventType.SIGNAL_UPDATED}:
        impact = _number(payload, "impact_score") or 0.0
        category = str(payload.get("signal_category") or payload.get("signal_type") or "general")
        return f"{category.replace('_', ' ').title()} signal · {impact:+.2f}"
    if event.event_type == CortexEventType.PROPAGATION_COMPLETED:
        impacts = payload.get("impacts") or ()
        names = [
            str(item.get("entity_name"))
            for item in impacts
            if isinstance(item, dict) and item.get("entity_name")
        ]
        detail = f" · {', '.join(names[:3])}" if names else ""
        return f"{int(payload.get('impact_count', 0))} downstream impact(s){detail}"
    if event.event_type == CortexEventType.SCORE_UPDATED:
        delta = _number(payload, "score_delta", "delta")
        return f"{event.entity_name or 'Entity'} score changed {delta:+.2f}" if delta is not None else "Scorecard updated"
    if event.event_type == CortexEventType.RECOMMENDATION_CHANGED:
        action = payload.get("recommendation") or payload.get("action") or payload.get("label")
        confidence = _number(payload, "confidence")
        suffix = ""
        if confidence is not None:
            suffix = f" · {confidence:.0%}" if confidence <= 1 else f" · {confidence:.0f}%"
        return f"{action or 'Recommendation updated'}{suffix}"
    if event.event_type == CortexEventType.CONFIDENCE_UPDATED:
        confidence = _confidence_from_payload(payload)
        if confidence is None:
            return "Confidence recalculated"
        return f"Confidence {confidence:.0%}" if confidence <= 1 else f"Confidence {confidence:.0f}%"
    return event.event_type.value.replace("_", " ").title()


def _title(event: CortexEvent, stage: ReplayStage) -> str:
    if event.event_type == CortexEventType.PLAYER_RESOLVED:
        entity_type = str(dict(event.payload).get("entity_type") or "entity").replace("_", " ").title()
        return f"{entity_type} resolved"
    return {
        ReplayStage.INGESTED: "Article received",
        ReplayStage.RESOLVED: "Entity resolved",
        ReplayStage.UNDERSTOOD: "Signal understood",
        ReplayStage.PROPAGATED: "Impact propagated",
        ReplayStage.SCORED: "Score updated",
        ReplayStage.RECOMMENDED: "Recommendation produced",
        ReplayStage.CONFIDENCE: "Confidence updated",
    }[stage]


def build_replay_decision(events: Iterable[CortexEvent]) -> ReplayDecision | None:
    ordered = sorted(events, key=lambda event: event.timestamp)
    if not ordered:
        return None

    correlation_ids = {event.correlation_id for event in ordered}
    if len(correlation_ids) != 1:
        raise ValueError("replay events must share one correlation_id")

    steps = tuple(
        sorted(
            (
                ReplayStep(
                    event_id=event.event_id,
                    timestamp=event.timestamp,
                    stage=_STAGE_BY_EVENT[event.event_type],
                    event_type=event.event_type,
                    title=_title(event, _STAGE_BY_EVENT[event.event_type]),
                    summary=_summary(event),
                    entity_id=event.entity_id,
                    entity_name=event.entity_name,
                    source=event.source,
                    details=dict(event.payload),
                )
                for event in ordered
                if event.event_type in _STAGE_BY_EVENT
            ),
            key=lambda step: (_STAGE_ORDER[step.stage], step.timestamp),
        )
    )
    if not steps:
        return None

    article = next((event for event in ordered if event.event_type == CortexEventType.ARTICLE_RECEIVED), ordered[0])
    recommendation_event = next((event for event in reversed(ordered) if event.event_type == CortexEventType.RECOMMENDATION_CHANGED), None)
    confidence_event = next((event for event in reversed(ordered) if event.event_type == CortexEventType.CONFIDENCE_UPDATED), None)
    resolved = next((event for event in ordered if event.event_type == CortexEventType.PLAYER_RESOLVED and str(dict(event.payload).get("entity_type", "")).casefold() == "player"), None)
    resolved = resolved or next((event for event in ordered if event.event_type == CortexEventType.PLAYER_RESOLVED), None)
    recommendation_payload = dict(recommendation_event.payload) if recommendation_event else {}
    confidence_payload = dict(confidence_event.payload) if confidence_event else {}
    confidence = _confidence_from_payload(confidence_payload)
    if confidence is None:
        confidence = _number(recommendation_payload, "confidence")
    decision_seed = f"{ordered[0].correlation_id}:{recommendation_event.event_id if recommendation_event else ordered[-1].event_id}"

    return ReplayDecision(
        decision_id=sha256(decision_seed.encode("utf-8")).hexdigest()[:12],
        correlation_id=ordered[0].correlation_id,
        headline=str(dict(article.payload).get("headline") or article.entity_name or "Cortex decision"),
        started_at=min(event.timestamp for event in ordered),
        completed_at=max(event.timestamp for event in ordered),
        steps=steps,
        entity_name=(resolved.entity_name if resolved else article.entity_name),
        source=article.source,
        recommendation=str(recommendation_payload.get("recommendation") or recommendation_payload.get("action") or recommendation_payload.get("label") or "") or None,
        confidence=confidence,
    )
