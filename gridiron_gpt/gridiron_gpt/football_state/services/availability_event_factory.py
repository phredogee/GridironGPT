from __future__ import annotations

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_gpt.football_state.models.availability_state import AvailabilityDesignation
from gridiron_gpt.football_state.models.availability_trajectory import (
    AvailabilityTrajectory,
    AvailabilityTrajectoryResult,
)


class AvailabilityEventFactory:
    """Convert canonical availability state + trajectory into Cortex evidence."""

    SOURCE = "canonical availability state"

    def build_events(self, result: AvailabilityTrajectoryResult) -> list[RawEvent]:
        current = result.current
        events = [self._current_state_event(result)]

        if result.trajectory not in {AvailabilityTrajectory.STABLE, AvailabilityTrajectory.UNKNOWN}:
            events.append(self._trajectory_event(result))

        return events

    def _current_state_event(self, result: AvailabilityTrajectoryResult) -> RawEvent:
        current = result.current
        sentiment, impact = self._designation_intelligence(current.designation)
        designation = current.designation.value
        injury = f" ({current.injury})" if current.injury else ""

        return RawEvent(
            source=self.SOURCE,
            headline=f"{current.player_name} availability is {designation}{injury}",
            player=current.player_name,
            player_id=current.player_id,
            team=current.team,
            published_at=current.effective_at.isoformat(),
            event_type="availability",
            sentiment=sentiment,
            impact_score=impact,
            confidence=0.98,
            evidence={
                "source_id": self._source_id(result, "state"),
                "availability": {
                    "designation": designation,
                    "practice_participation": current.practice_participation.value,
                    "injury": current.injury,
                    "available": current.available,
                    "source": current.source,
                },
            },
        )

    def _trajectory_event(self, result: AvailabilityTrajectoryResult) -> RawEvent:
        current = result.current
        sentiment, impact = self._trajectory_intelligence(result.trajectory)

        return RawEvent(
            source=self.SOURCE,
            headline=(
                f"{current.player_name} availability trajectory is "
                f"{result.trajectory.value}: {result.reason}"
            ),
            player=current.player_name,
            player_id=current.player_id,
            team=current.team,
            published_at=current.effective_at.isoformat(),
            event_type="availability_trajectory",
            sentiment=sentiment,
            impact_score=impact,
            confidence=0.94,
            evidence={
                "source_id": self._source_id(result, "trajectory"),
                "availability_trajectory": {
                    "trajectory": result.trajectory.value,
                    "reason": result.reason,
                    "previous_designation": result.previous.designation.value,
                    "current_designation": current.designation.value,
                    "previous_practice": result.previous.practice_participation.value,
                    "current_practice": current.practice_participation.value,
                },
            },
        )

    @staticmethod
    def _designation_intelligence(designation: AvailabilityDesignation) -> tuple[str, float]:
        if designation == AvailabilityDesignation.ACTIVE:
            return "positive", 0.45
        if designation == AvailabilityDesignation.QUESTIONABLE:
            return "negative", -0.25
        if designation == AvailabilityDesignation.DOUBTFUL:
            return "negative", -0.55
        if designation == AvailabilityDesignation.OUT:
            return "negative", -0.85
        if designation in {
            AvailabilityDesignation.IR,
            AvailabilityDesignation.PUP,
            AvailabilityDesignation.NFI,
            AvailabilityDesignation.SUSPENDED,
        }:
            return "negative", -1.0
        return "neutral", 0.0

    @staticmethod
    def _trajectory_intelligence(trajectory: AvailabilityTrajectory) -> tuple[str, float]:
        if trajectory == AvailabilityTrajectory.RECOVERED:
            return "positive", 0.75
        if trajectory == AvailabilityTrajectory.IMPROVING:
            return "positive", 0.35
        if trajectory == AvailabilityTrajectory.WORSENING:
            return "negative", -0.45
        if trajectory == AvailabilityTrajectory.UNAVAILABLE:
            return "negative", -0.35
        return "neutral", 0.0

    @staticmethod
    def _source_id(result: AvailabilityTrajectoryResult, kind: str) -> str:
        current = result.current
        return ":".join(
            [
                "availability",
                current.player_id,
                kind,
                current.designation.value,
                current.practice_participation.value,
                result.trajectory.value,
                current.effective_at.isoformat(),
            ]
        )
