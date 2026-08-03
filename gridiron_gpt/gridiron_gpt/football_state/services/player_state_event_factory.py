from __future__ import annotations

import re
from typing import Any

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_gpt.football_state.models.player_state_change import PlayerStateChange


class PlayerStateEventFactory:
    """Convert canonical player-state transitions into Cortex RawEvents."""

    SOURCE = "canonical player state"

    def build_events(self, change: PlayerStateChange) -> list[RawEvent]:
        if not change.meaningful_change or change.is_new_player:
            return []

        events: list[RawEvent] = []
        for field_name, (previous, current) in change.changed_fields.items():
            event = self._build_event(
                change=change,
                field_name=field_name,
                previous=previous,
                current=current,
            )
            if event is not None:
                events.append(event)
        return events

    def _build_event(
        self,
        *,
        change: PlayerStateChange,
        field_name: str,
        previous: Any,
        current: Any,
    ) -> RawEvent | None:
        current_state = change.current
        common = {
            "source": self.SOURCE,
            "player": change.player_name,
            "player_id": change.player_id,
            "team": current_state.team,
            "position": current_state.position,
            "published_at": current_state.effective_at.isoformat(),
        }

        evidence = {
            "source_id": self._source_id(change, field_name, previous, current),
            "state_change": {
                "field": field_name,
                "previous": previous,
                "current": current,
                "source": current_state.source,
            },
        }

        if field_name == "team":
            return RawEvent(
                headline=(
                    f"{change.player_name} moved from {previous or 'no team'} "
                    f"to {current or 'no team'}"
                ),
                event_type="transaction",
                sentiment="neutral",
                impact_score=0.0,
                confidence=0.99,
                evidence=evidence,
                **common,
            )

        if field_name == "roster_status":
            sentiment, impact = self._status_intelligence(current)
            return RawEvent(
                headline=(
                    f"{change.player_name} roster status changed from "
                    f"{previous or 'unknown'} to {current or 'unknown'}"
                ),
                event_type="availability",
                sentiment=sentiment,
                impact_score=impact,
                confidence=0.98,
                evidence=evidence,
                **common,
            )

        if field_name == "depth_chart_position":
            sentiment, impact, direction = self._depth_chart_intelligence(
                previous,
                current,
            )
            return RawEvent(
                headline=(
                    f"{change.player_name} {direction} from "
                    f"{previous or 'unknown'} to {current or 'unknown'}"
                ),
                event_type="depth_chart",
                sentiment=sentiment,
                impact_score=impact,
                confidence=0.96,
                evidence=evidence,
                **common,
            )

        if field_name == "position":
            return RawEvent(
                headline=(
                    f"{change.player_name} position changed from "
                    f"{previous or 'unknown'} to {current or 'unknown'}"
                ),
                event_type="roster",
                sentiment="neutral",
                impact_score=0.0,
                confidence=0.98,
                evidence=evidence,
                **common,
            )

        return None

    @staticmethod
    def _status_intelligence(status: Any) -> tuple[str, float]:
        normalized = str(status or "").strip().upper()

        positive = {"ACT", "ACTIVE"}
        negative = {
            "IR", "RES", "RESERVE", "PUP", "NFI", "SUS", "SUSPENDED",
            "INACTIVE", "OUT",
        }

        if normalized in positive:
            return "positive", 0.7
        if normalized in negative:
            return "negative", -0.8
        return "neutral", 0.0

    @classmethod
    def _depth_chart_intelligence(
        cls,
        previous: Any,
        current: Any,
    ) -> tuple[str, float, str]:
        previous_rank = cls._depth_rank(previous)
        current_rank = cls._depth_rank(current)

        if previous_rank is not None and current_rank is not None:
            if current_rank < previous_rank:
                return "positive", 0.7, "moved up the depth chart"
            if current_rank > previous_rank:
                return "negative", -0.7, "moved down the depth chart"

        return "neutral", 0.0, "changed depth-chart role"

    @staticmethod
    def _depth_rank(value: Any) -> int | None:
        text = str(value or "").strip().upper()
        match = re.search(r"(\d+)$", text)
        if not match:
            return None
        return int(match.group(1))

    @staticmethod
    def _source_id(
        change: PlayerStateChange,
        field_name: str,
        previous: Any,
        current: Any,
    ) -> str:
        return ":".join(
            [
                "player_state",
                change.player_id,
                field_name,
                str(previous or "").strip(),
                str(current or "").strip(),
                change.current.effective_at.isoformat(),
            ]
        )
