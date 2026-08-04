from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any

from gridiron_cortex.events.event import CortexEvent
from gridiron_cortex.events.event_bus import CortexEventBus
from gridiron_cortex.events.event_types import CortexEventType


def _serialize(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _serialize(item) for key, item in asdict(value).items()}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): _serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_serialize(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


class PipelineEventPublisher:
    """Publish one correlated event trail for a Cortex engine run."""

    def __init__(
        self,
        bus: CortexEventBus,
        *,
        engine_version: str = "cortex-dev",
    ) -> None:
        self.bus = bus
        self.engine_version = engine_version

    def article_received(self, raw_event, correlation_id: str) -> CortexEvent:
        return self._publish(
            CortexEventType.ARTICLE_RECEIVED,
            correlation_id=correlation_id,
            entity_id=getattr(raw_event, "player_id", None),
            entity_name=getattr(raw_event, "player", None),
            source=getattr(raw_event, "source", None),
            payload={
                "headline": getattr(raw_event, "headline", ""),
                "team": getattr(raw_event, "team", None),
                "url": getattr(raw_event, "url", None),
                "published_at": getattr(raw_event, "published_at", None),
                "event_type": getattr(raw_event, "event_type", None),
            },
        )

    def publish_result(self, result, correlation_id: str) -> tuple[CortexEvent, ...]:
        published: list[CortexEvent] = []
        source = getattr(getattr(result, "event", None), "source", None)

        for entity in getattr(result, "entities", ()) or ():
            published.append(
                self._publish(
                    CortexEventType.PLAYER_RESOLVED,
                    correlation_id=correlation_id,
                    entity_id=getattr(entity, "player_id", None),
                    entity_name=getattr(entity, "name", None),
                    source=source,
                    payload={
                        "entity_type": getattr(entity, "entity_type", None),
                        "team": getattr(entity, "team", None),
                        "position": getattr(entity, "position", None),
                        "confidence": getattr(entity, "confidence", None),
                    },
                )
            )

        signal = getattr(result, "signal", None)
        if signal is not None:
            primary = next(iter(getattr(signal, "entities", ()) or ()), None)
            published.append(
                self._publish(
                    CortexEventType.SIGNAL_CREATED,
                    correlation_id=correlation_id,
                    entity_id=getattr(primary, "player_id", None),
                    entity_name=getattr(primary, "name", None),
                    source=source,
                    payload={
                        "headline": getattr(signal, "headline", ""),
                        "impact_score": getattr(signal, "impact_score", 0.0),
                        "sentiment": getattr(signal, "sentiment", "neutral"),
                        "signal_type": getattr(signal, "signal_type", "news"),
                        "signal_category": getattr(signal, "signal_category", "general"),
                        "confidence": getattr(signal, "confidence", None),
                    },
                )
            )

        impacts = getattr(result, "impacts", ()) or ()
        if impacts:
            published.append(
                self._publish(
                    CortexEventType.PROPAGATION_COMPLETED,
                    correlation_id=correlation_id,
                    source=source,
                    payload={
                        "impact_count": len(impacts),
                        "impacts": _serialize(impacts),
                    },
                )
            )

        for update in getattr(result, "score_updates", ()) or ():
            published.append(
                self._publish(
                    CortexEventType.SCORE_UPDATED,
                    correlation_id=correlation_id,
                    entity_id=getattr(update, "entity_id", None),
                    entity_name=getattr(update, "entity_name", None),
                    source=source,
                    payload=_serialize(update),
                )
            )

        for recommendation in getattr(result, "recommendations", ()) or ():
            published.append(
                self._publish(
                    CortexEventType.RECOMMENDATION_CHANGED,
                    correlation_id=correlation_id,
                    entity_id=getattr(recommendation, "entity_id", None),
                    entity_name=getattr(recommendation, "entity_name", None),
                    source=source,
                    payload=_serialize(recommendation),
                )
            )

        confidence_result = getattr(result, "confidence_result", None)
        if confidence_result is not None or signal is not None:
            confidence = (
                getattr(confidence_result, "final_confidence", None)
                if confidence_result is not None
                else getattr(signal, "confidence", None)
            )
            published.append(
                self._publish(
                    CortexEventType.CONFIDENCE_UPDATED,
                    correlation_id=correlation_id,
                    source=source,
                    payload={
                        "confidence": confidence,
                        "calibration": _serialize(confidence_result),
                    },
                )
            )

        return tuple(published)

    def _publish(
        self,
        event_type: CortexEventType,
        *,
        correlation_id: str,
        entity_id: str | None = None,
        entity_name: str | None = None,
        source: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> CortexEvent:
        return self.bus.publish(
            CortexEvent(
                event_type=event_type,
                entity_id=entity_id,
                entity_name=entity_name,
                source=source,
                payload=payload or {},
                correlation_id=correlation_id,
                engine_version=self.engine_version,
            )
        )
