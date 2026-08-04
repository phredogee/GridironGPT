from __future__ import annotations

from collections import defaultdict

from gridiron_cortex.events.event_bus import CortexEventBus
from gridiron_cortex.replay.replay_builder import build_replay_decision
from gridiron_cortex.replay.replay_models import ReplayDecision


class ReplayEngine:
    """Reconstruct Cortex decision timelines from correlated events."""

    def __init__(self, event_bus: CortexEventBus) -> None:
        self.event_bus = event_bus

    def by_correlation(self, correlation_id: str) -> ReplayDecision | None:
        return build_replay_decision(
            self.event_bus.history(correlation_id=correlation_id)
        )

    def by_decision_id(self, decision_id: str) -> ReplayDecision | None:
        for decision in self.latest(limit=None):
            if decision.decision_id == decision_id:
                return decision
        return None

    def latest(self, limit: int | None = 25) -> tuple[ReplayDecision, ...]:
        grouped = defaultdict(list)
        for event in self.event_bus.history():
            grouped[event.correlation_id].append(event)

        decisions = [
            decision
            for events in grouped.values()
            if (decision := build_replay_decision(events)) is not None
        ]
        decisions.sort(key=lambda decision: decision.completed_at, reverse=True)
        if limit is None:
            return tuple(decisions)
        if limit < 1:
            return ()
        return tuple(decisions[:limit])

    def by_player(
        self,
        player_name: str,
        limit: int = 25,
    ) -> tuple[ReplayDecision, ...]:
        normalized = player_name.strip().casefold()
        matches = tuple(
            decision
            for decision in self.latest(limit=None)
            if (decision.entity_name or "").strip().casefold() == normalized
            or any(
                (step.entity_name or "").strip().casefold() == normalized
                for step in decision.steps
            )
        )
        return matches[: max(0, limit)]
