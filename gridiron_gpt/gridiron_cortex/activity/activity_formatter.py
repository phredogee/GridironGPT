from __future__ import annotations

from typing import Any

from gridiron_cortex.activity.activity_models import ActivityCard, ActivitySeverity
from gridiron_cortex.events.event import CortexEvent
from gridiron_cortex.events.event_types import CortexEventType


_EVENT_PRESENTATION = {
    CortexEventType.ARTICLE_RECEIVED: ("📰", "Article received"),
    CortexEventType.PLAYER_RESOLVED: ("👤", "Player resolved"),
    CortexEventType.SIGNAL_CREATED: ("📈", "Signal created"),
    CortexEventType.SIGNAL_UPDATED: ("📊", "Signal updated"),
    CortexEventType.PROPAGATION_COMPLETED: ("🔄", "Propagation completed"),
    CortexEventType.SCORE_UPDATED: ("🎯", "Score updated"),
    CortexEventType.RECOMMENDATION_CHANGED: ("⭐", "Recommendation changed"),
    CortexEventType.CONFIDENCE_UPDATED: ("🧠", "Confidence updated"),
}


def _number(payload: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def _severity(event: CortexEvent) -> ActivitySeverity:
    payload = dict(event.payload)
    impact = _number(payload, "impact_score", "score_delta", "delta")
    if event.event_type == CortexEventType.PROPAGATION_COMPLETED:
        impacts = payload.get("impacts") or []
        values = [
            item.get("impact_score")
            for item in impacts
            if isinstance(item, dict) and isinstance(item.get("impact_score"), (int, float))
        ]
        if values:
            impact = sum(float(value) for value in values)
    if impact is not None:
        if impact > 0:
            return ActivitySeverity.POSITIVE
        if impact < 0:
            return ActivitySeverity.NEGATIVE
    sentiment = str(payload.get("sentiment", "")).casefold()
    if sentiment == "positive":
        return ActivitySeverity.POSITIVE
    if sentiment == "negative":
        return ActivitySeverity.NEGATIVE
    recommendation = str(payload.get("recommendation", payload.get("action", ""))).upper()
    if recommendation in {"BUY", "START", "ADD"}:
        return ActivitySeverity.POSITIVE
    if recommendation in {"SELL", "SIT", "DROP"}:
        return ActivitySeverity.NEGATIVE
    return ActivitySeverity.INFO


def _subtitle(event: CortexEvent) -> str:
    payload = dict(event.payload)
    if event.event_type == CortexEventType.ARTICLE_RECEIVED:
        return str(payload.get("headline") or event.entity_name or event.source or "New evidence")
    if event.event_type == CortexEventType.PLAYER_RESOLVED:
        team = payload.get("team")
        position = payload.get("position")
        metadata = " · ".join(str(value) for value in (team, position) if value)
        return f"{event.entity_name or 'Entity'}{f' · {metadata}' if metadata else ''}"
    if event.event_type in {CortexEventType.SIGNAL_CREATED, CortexEventType.SIGNAL_UPDATED}:
        impact = _number(payload, "impact_score") or 0.0
        category = payload.get("signal_category") or payload.get("signal_type") or "general"
        return f"{str(category).replace('_', ' ').title()} · impact {impact:+.2f}"
    if event.event_type == CortexEventType.PROPAGATION_COMPLETED:
        return f"{int(payload.get('impact_count', 0))} downstream impact(s)"
    if event.event_type == CortexEventType.SCORE_UPDATED:
        delta = _number(payload, "score_delta", "delta")
        if delta is not None:
            return f"{event.entity_name or 'Entity'} · {delta:+.2f}"
        return event.entity_name or "Scorecard changed"
    if event.event_type == CortexEventType.RECOMMENDATION_CHANGED:
        action = payload.get("recommendation") or payload.get("action") or payload.get("label")
        confidence = _number(payload, "confidence")
        parts = [str(action or "Recommendation updated")]
        if confidence is not None:
            parts.append(f"{confidence:.0%}" if confidence <= 1 else f"{confidence:.0f}%")
        return " · ".join(parts)
    if event.event_type == CortexEventType.CONFIDENCE_UPDATED:
        confidence = _number(payload, "confidence")
        if confidence is None:
            return "Confidence recalculated"
        return f"{confidence:.0%}" if confidence <= 1 else f"{confidence:.0f}%"
    return event.entity_name or event.source or event.event_type.value


def format_activity(event: CortexEvent) -> ActivityCard:
    icon, title = _EVENT_PRESENTATION[event.event_type]
    return ActivityCard(
        event_id=event.event_id,
        timestamp=event.timestamp,
        event_type=event.event_type,
        icon=icon,
        title=title,
        subtitle=_subtitle(event),
        severity=_severity(event),
        correlation_id=event.correlation_id,
        entity_id=event.entity_id,
        entity_name=event.entity_name,
        source=event.source,
        details=dict(event.payload),
    )
