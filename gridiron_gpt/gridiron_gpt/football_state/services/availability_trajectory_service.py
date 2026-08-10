from __future__ import annotations

from gridiron_gpt.football_state.models.availability_state import (
    AvailabilityDesignation,
    CanonicalAvailabilityState,
    PracticeParticipation,
)
from gridiron_gpt.football_state.models.availability_trajectory import (
    AvailabilityTrajectory,
    AvailabilityTrajectoryResult,
)


_DESIGNATION_SCORE = {
    AvailabilityDesignation.ACTIVE: 4,
    AvailabilityDesignation.QUESTIONABLE: 3,
    AvailabilityDesignation.DOUBTFUL: 2,
    AvailabilityDesignation.OUT: 1,
    AvailabilityDesignation.IR: 0,
    AvailabilityDesignation.PUP: 0,
    AvailabilityDesignation.NFI: 0,
    AvailabilityDesignation.SUSPENDED: 0,
}

_PRACTICE_SCORE = {
    PracticeParticipation.FULL: 3,
    PracticeParticipation.LIMITED: 2,
    PracticeParticipation.DNP: 1,
}


class AvailabilityTrajectoryService:
    """Classify direction between successive canonical availability states."""

    def classify(
        self,
        previous: CanonicalAvailabilityState,
        current: CanonicalAvailabilityState,
    ) -> AvailabilityTrajectoryResult:
        if previous.player_id != current.player_id:
            raise ValueError("availability states must describe the same player")

        if previous.available is False and current.available is True:
            return self._result(previous, current, AvailabilityTrajectory.RECOVERED, "player returned to available status")

        if current.available is False:
            if previous.available is False:
                return self._result(previous, current, AvailabilityTrajectory.UNAVAILABLE, "player remains unavailable")
            return self._result(previous, current, AvailabilityTrajectory.WORSENING, "player became unavailable")

        designation_delta = self._delta(
            _DESIGNATION_SCORE.get(previous.designation),
            _DESIGNATION_SCORE.get(current.designation),
        )
        practice_delta = self._delta(
            _PRACTICE_SCORE.get(previous.practice_participation),
            _PRACTICE_SCORE.get(current.practice_participation),
        )
        deltas = [delta for delta in (designation_delta, practice_delta) if delta is not None]

        if not deltas:
            if (
                previous.designation == current.designation
                and previous.practice_participation == current.practice_participation
            ):
                return self._result(previous, current, AvailabilityTrajectory.STABLE, "availability state is unchanged")
            return self._result(previous, current, AvailabilityTrajectory.UNKNOWN, "insufficient comparable availability evidence")

        total = sum(deltas)
        if total > 0:
            return self._result(previous, current, AvailabilityTrajectory.IMPROVING, "availability indicators improved")
        if total < 0:
            return self._result(previous, current, AvailabilityTrajectory.WORSENING, "availability indicators worsened")
        return self._result(previous, current, AvailabilityTrajectory.STABLE, "availability indicators are stable")

    @staticmethod
    def _delta(previous: int | None, current: int | None) -> int | None:
        if previous is None or current is None:
            return None
        return current - previous

    @staticmethod
    def _result(previous, current, trajectory, reason):
        return AvailabilityTrajectoryResult(
            player_id=current.player_id,
            player_name=current.player_name,
            trajectory=trajectory,
            previous=previous,
            current=current,
            reason=reason,
        )
