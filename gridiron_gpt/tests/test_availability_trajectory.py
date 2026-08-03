from gridiron_gpt.football_state.models.availability_state import (
    AvailabilityDesignation,
    CanonicalAvailabilityState,
    PracticeParticipation,
)
from gridiron_gpt.football_state.models.availability_trajectory import AvailabilityTrajectory
from gridiron_gpt.football_state.services.availability_trajectory_service import AvailabilityTrajectoryService


def state(designation=AvailabilityDesignation.QUESTIONABLE, practice=PracticeParticipation.NOT_REPORTED, player_id="bijan"):
    return CanonicalAvailabilityState(
        player_id=player_id,
        player_name="Bijan Robinson",
        team="ATL",
        designation=designation,
        practice_participation=practice,
    )


def test_dnp_to_limited_is_improving():
    result = AvailabilityTrajectoryService().classify(
        state(practice=PracticeParticipation.DNP),
        state(practice=PracticeParticipation.LIMITED),
    )
    assert result.trajectory == AvailabilityTrajectory.IMPROVING


def test_limited_to_full_is_improving():
    result = AvailabilityTrajectoryService().classify(
        state(practice=PracticeParticipation.LIMITED),
        state(practice=PracticeParticipation.FULL),
    )
    assert result.trajectory == AvailabilityTrajectory.IMPROVING


def test_full_to_dnp_is_worsening():
    result = AvailabilityTrajectoryService().classify(
        state(practice=PracticeParticipation.FULL),
        state(practice=PracticeParticipation.DNP),
    )
    assert result.trajectory == AvailabilityTrajectory.WORSENING


def test_questionable_to_out_is_worsening():
    result = AvailabilityTrajectoryService().classify(
        state(designation=AvailabilityDesignation.QUESTIONABLE),
        state(designation=AvailabilityDesignation.OUT),
    )
    assert result.trajectory == AvailabilityTrajectory.WORSENING


def test_ir_to_active_is_recovered():
    result = AvailabilityTrajectoryService().classify(
        state(designation=AvailabilityDesignation.IR),
        state(designation=AvailabilityDesignation.ACTIVE),
    )
    assert result.trajectory == AvailabilityTrajectory.RECOVERED


def test_unavailable_player_remaining_out_is_unavailable():
    result = AvailabilityTrajectoryService().classify(
        state(designation=AvailabilityDesignation.IR),
        state(designation=AvailabilityDesignation.OUT),
    )
    assert result.trajectory == AvailabilityTrajectory.UNAVAILABLE


def test_unchanged_state_is_stable():
    result = AvailabilityTrajectoryService().classify(
        state(practice=PracticeParticipation.LIMITED),
        state(practice=PracticeParticipation.LIMITED),
    )
    assert result.trajectory == AvailabilityTrajectory.STABLE


def test_unknown_to_questionable_without_comparable_practice_is_unknown():
    result = AvailabilityTrajectoryService().classify(
        state(designation=AvailabilityDesignation.UNKNOWN),
        state(designation=AvailabilityDesignation.QUESTIONABLE),
    )
    assert result.trajectory == AvailabilityTrajectory.UNKNOWN


def test_different_players_are_rejected():
    try:
        AvailabilityTrajectoryService().classify(state(), state(player_id="allgeier"))
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "same player" in str(exc)
