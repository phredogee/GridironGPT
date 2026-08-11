from gridiron_gpt.football_state.models.player_state import CanonicalPlayerState
from gridiron_gpt.football_state.services.player_availability_classifier import (
    PlayerAvailability,
    PlayerAvailabilityClassifier,
)


def _state(status=None, detail=None):
    return CanonicalPlayerState(
        player_id="00-1234567",
        player_name="Test Player",
        roster_status=status,
        status_description_abbr=detail,
    )


def test_active_player_is_available():
    assert PlayerAvailabilityClassifier.classify(_state("ACT", "A01")) is PlayerAvailability.AVAILABLE


def test_reserve_player_is_reserve():
    assert PlayerAvailabilityClassifier.classify(_state("RES", "R09")) is PlayerAvailability.RESERVE


def test_retired_player_is_retired():
    assert PlayerAvailabilityClassifier.classify(_state("RET", "R02")) is PlayerAvailability.RETIRED


def test_cut_player_is_released():
    assert PlayerAvailabilityClassifier.classify(_state("CUT", "W03")) is PlayerAvailability.RELEASED


def test_exempt_player_is_exempt():
    assert PlayerAvailabilityClassifier.classify(_state("E14", "E14")) is PlayerAvailability.EXEMPT


def test_missing_status_is_unknown():
    assert PlayerAvailabilityClassifier.classify(_state()) is PlayerAvailability.UNKNOWN


def test_unrecognized_provider_status_is_unknown():
    assert PlayerAvailabilityClassifier.classify(_state("NEW_CODE", "X99")) is PlayerAvailability.UNKNOWN


def test_status_matching_is_case_and_whitespace_insensitive():
    assert PlayerAvailabilityClassifier.classify(_state(" act ")) is PlayerAvailability.AVAILABLE
