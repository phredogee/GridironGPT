from __future__ import annotations

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_gpt.football_state.services.opportunity_event_factory import OpportunityEventFactory
from gridiron_gpt.football_state.services.roster_opportunity_service import RosterOpportunityService


class RosterConsequenceOrchestrator:
    """Derive one-hop teammate opportunity events from a source roster event."""

    DERIVED_EVENT_TYPE = "roster_opportunity"

    def __init__(
        self,
        opportunity_service: RosterOpportunityService,
        event_factory: OpportunityEventFactory | None = None,
    ) -> None:
        self.opportunity_service = opportunity_service
        self.event_factory = event_factory or OpportunityEventFactory()

    def derive_events(self, source_event: RawEvent) -> list[RawEvent]:
        # Derived opportunity events are terminal for this orchestration pass.
        # This prevents A -> B -> A consequence loops.
        if source_event.event_type == self.DERIVED_EVENT_TYPE:
            return []

        if not source_event.player_id or not source_event.player:
            return []

        if source_event.impact_score is None or source_event.impact_score == 0:
            return []

        changes = self.opportunity_service.derive(
            source_player_id=source_event.player_id,
            source_player_name=source_event.player,
            source_impact_score=source_event.impact_score,
        )

        events: list[RawEvent] = []
        seen_fingerprints: set[str] = set()
        source_fingerprint = source_event.fingerprint()

        for change in changes:
            # Never derive an event back onto the original source player.
            if change.affected_player_id == source_event.player_id:
                continue

            event = self.event_factory.build_event(change)
            fingerprint = event.fingerprint()
            if fingerprint in seen_fingerprints:
                continue

            event.evidence.setdefault("causality", {})
            event.evidence["causality"].update(
                {
                    "source_event_fingerprint": source_fingerprint,
                    "source_event_type": source_event.event_type,
                    "source_player_id": source_event.player_id,
                    "source_player_name": source_event.player,
                    "derived": True,
                }
            )
            seen_fingerprints.add(fingerprint)
            events.append(event)

        return events
