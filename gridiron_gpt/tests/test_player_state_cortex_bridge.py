from datetime import datetime, timezone

from gridiron_cortex.understand.signal_processor import SignalProcessor
from gridiron_gpt.football_state.models.player_state import CanonicalPlayerState
from gridiron_gpt.football_state.models.player_state_change import PlayerStateChange
from gridiron_gpt.football_state.services.player_state_event_factory import PlayerStateEventFactory


NOW = datetime(2026, 8, 3, 18, 0, tzinfo=timezone.utc)


def state(**overrides):
    values = {
        "player_id": "00-0036322",
        "player_name": "Bijan Robinson",
        "team": "ATL",
        "position": "RB",
        "roster_status": "ACT",
        "depth_chart_position": "RB2",
        "effective_at": NOW,
    }
    values.update(overrides)
    return CanonicalPlayerState(**values)


def change(previous, current, changed_fields):
    return PlayerStateChange(
        player_id=current.player_id,
        player_name=current.player_name,
        previous=previous,
        current=current,
        changed_fields=changed_fields,
    )


def test_depth_chart_promotion_becomes_positive_cortex_signal():
    previous = state(depth_chart_position="RB2")
    current = state(depth_chart_position="RB1")
    events = PlayerStateEventFactory().build_events(
        change(previous, current, {"depth_chart_position": ("RB2", "RB1")})
    )

    assert len(events) == 1
    event = events[0]
    assert event.event_type == "depth_chart"
    assert event.sentiment == "positive"
    assert event.impact_score == 0.7
    assert event.player_id == current.player_id

    signal = SignalProcessor().process(event, entities=[])
    assert signal.sentiment == "positive"
    assert signal.impact_score == 0.7
    assert signal.signal_type == "depth_chart"


def test_depth_chart_demotion_becomes_negative_cortex_signal():
    previous = state(depth_chart_position="RB1")
    current = state(depth_chart_position="RB2")
    event = PlayerStateEventFactory().build_events(
        change(previous, current, {"depth_chart_position": ("RB1", "RB2")})
    )[0]

    signal = SignalProcessor().process(event, entities=[])
    assert signal.sentiment == "negative"
    assert signal.impact_score == -0.7


def test_active_roster_status_becomes_positive_availability_signal():
    previous = state(roster_status="IR")
    current = state(roster_status="ACT")
    event = PlayerStateEventFactory().build_events(
        change(previous, current, {"roster_status": ("IR", "ACT")})
    )[0]

    signal = SignalProcessor().process(event, entities=[])
    assert signal.sentiment == "positive"
    assert signal.impact_score == 0.7
    assert signal.signal_type == "availability"


def test_reserve_status_becomes_negative_availability_signal():
    previous = state(roster_status="ACT")
    current = state(roster_status="IR")
    event = PlayerStateEventFactory().build_events(
        change(previous, current, {"roster_status": ("ACT", "IR")})
    )[0]

    signal = SignalProcessor().process(event, entities=[])
    assert signal.sentiment == "negative"
    assert signal.impact_score == -0.8


def test_team_change_is_neutral_transaction_evidence():
    previous = state(team="ATL")
    current = state(team="DAL")
    event = PlayerStateEventFactory().build_events(
        change(previous, current, {"team": ("ATL", "DAL")})
    )[0]

    assert event.team == "DAL"
    assert event.event_type == "transaction"
    assert event.sentiment == "neutral"
    assert event.impact_score == 0.0
    assert event.evidence["state_change"]["previous"] == "ATL"
    assert event.evidence["state_change"]["current"] == "DAL"


def test_multiple_state_changes_emit_separate_traceable_events():
    previous = state(team="ATL", roster_status="IR", depth_chart_position="RB2")
    current = state(team="DAL", roster_status="ACT", depth_chart_position="RB1")
    events = PlayerStateEventFactory().build_events(
        change(
            previous,
            current,
            {
                "team": ("ATL", "DAL"),
                "roster_status": ("IR", "ACT"),
                "depth_chart_position": ("RB2", "RB1"),
            },
        )
    )

    assert len(events) == 3
    assert len({event.evidence["source_id"] for event in events}) == 3
    assert {event.evidence["state_change"]["field"] for event in events} == {
        "team", "roster_status", "depth_chart_position"
    }


def test_new_player_snapshot_does_not_create_transition_event():
    current = state()
    events = PlayerStateEventFactory().build_events(
        PlayerStateChange(
            player_id=current.player_id,
            player_name=current.player_name,
            previous=None,
            current=current,
            changed_fields={},
        )
    )

    assert events == []
