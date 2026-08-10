from datetime import datetime, timezone

from gridiron_gpt.football_state.models.availability_state import (
    AvailabilityDesignation,
    CanonicalAvailabilityState,
    PracticeParticipation,
)


NOW = datetime(2026, 8, 3, 18, 0, tzinfo=timezone.utc)


def state(**overrides):
    values = {
        "player_id": "bijan",
        "player_name": "Bijan Robinson",
        "team": "ATL",
        "designation": AvailabilityDesignation.ACTIVE,
        "practice_participation": PracticeParticipation.FULL,
        "effective_at": NOW,
    }
    values.update(overrides)
    return CanonicalAvailabilityState(**values)


def test_active_player_is_available():
    availability = state()

    assert availability.available is True


def test_unavailable_designations_are_not_available():
    for designation in (
        AvailabilityDesignation.OUT,
        AvailabilityDesignation.IR,
        AvailabilityDesignation.PUP,
        AvailabilityDesignation.NFI,
        AvailabilityDesignation.SUSPENDED,
    ):
        assert state(designation=designation).available is False


def test_uncertain_designations_do_not_claim_availability():
    assert state(designation=AvailabilityDesignation.QUESTIONABLE).available is None
    assert state(designation=AvailabilityDesignation.DOUBTFUL).available is None
    assert state(designation=AvailabilityDesignation.UNKNOWN).available is None


def test_availability_state_round_trips():
    original = state(
        designation=AvailabilityDesignation.QUESTIONABLE,
        practice_participation=PracticeParticipation.LIMITED,
        injury="hamstring",
        evidence={"report": "Wednesday injury report"},
    )

    restored = CanonicalAvailabilityState.from_dict(original.to_dict())

    assert restored == original
    assert restored.designation == AvailabilityDesignation.QUESTIONABLE
    assert restored.practice_participation == PracticeParticipation.LIMITED
