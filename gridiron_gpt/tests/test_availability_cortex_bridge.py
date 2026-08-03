from gridiron_cortex.understand.signal_processor import SignalProcessor
from gridiron_gpt.football_state.models.availability_state import (
    AvailabilityDesignation,
    CanonicalAvailabilityState,
    PracticeParticipation,
)
from gridiron_gpt.football_state.services.availability_event_factory import AvailabilityEventFactory
from gridiron_gpt.football_state.services.availability_trajectory_service import AvailabilityTrajectoryService


def state(designation, practice, injury="hamstring"):
    return CanonicalAvailabilityState(
        player_id="bijan",
        player_name="Bijan Robinson",
        team="ATL",
        designation=designation,
        practice_participation=practice,
        injury=injury,
    )


def events(previous, current):
    result = AvailabilityTrajectoryService().classify(previous, current)
    return AvailabilityEventFactory().build_events(result)


def test_questionable_but_improving_preserves_risk_and_direction_separately():
    built = events(
        state(AvailabilityDesignation.QUESTIONABLE, PracticeParticipation.DNP),
        state(AvailabilityDesignation.QUESTIONABLE, PracticeParticipation.LIMITED),
    )

    assert len(built) == 2
    current, trajectory = built
    assert current.sentiment == "negative"
    assert current.impact_score < 0
    assert trajectory.sentiment == "positive"
    assert trajectory.impact_score > 0


def test_out_and_worsening_produce_negative_evidence():
    built = events(
        state(AvailabilityDesignation.QUESTIONABLE, PracticeParticipation.LIMITED),
        state(AvailabilityDesignation.OUT, PracticeParticipation.DNP),
    )

    assert all(event.sentiment == "negative" for event in built)
    assert built[0].impact_score < built[1].impact_score


def test_ir_to_active_emits_positive_current_state_and_recovery():
    built = events(
        state(AvailabilityDesignation.IR, PracticeParticipation.DNP),
        state(AvailabilityDesignation.ACTIVE, PracticeParticipation.FULL, injury=None),
    )

    assert len(built) == 2
    assert built[0].sentiment == "positive"
    assert built[1].sentiment == "positive"
    assert built[1].evidence["availability_trajectory"]["trajectory"] == "recovered"


def test_stable_state_does_not_emit_redundant_trajectory_event():
    built = events(
        state(AvailabilityDesignation.QUESTIONABLE, PracticeParticipation.LIMITED),
        state(AvailabilityDesignation.QUESTIONABLE, PracticeParticipation.LIMITED),
    )

    assert len(built) == 1
    assert built[0].event_type == "availability"


def test_availability_events_pass_through_signal_processor():
    built = events(
        state(AvailabilityDesignation.QUESTIONABLE, PracticeParticipation.DNP),
        state(AvailabilityDesignation.QUESTIONABLE, PracticeParticipation.LIMITED),
    )

    signals = [SignalProcessor().process(event, entities=[]) for event in built]

    assert signals[0].sentiment == "negative"
    assert signals[0].impact_score < 0
    assert signals[1].sentiment == "positive"
    assert signals[1].impact_score > 0
    assert signals[1].signal_type == "availability_trajectory"
