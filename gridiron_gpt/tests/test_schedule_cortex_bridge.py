from datetime import datetime, timezone

from gridiron_cortex.understand.signal_processor import SignalProcessor
from gridiron_gpt.football_state.models.game_context import CanonicalGameContext, VenueSide
from gridiron_gpt.football_state.models.matchup_context import MatchupContext, MatchupTendency, OpponentMetric
from gridiron_gpt.football_state.models.schedule_context import UpcomingScheduleContext
from gridiron_gpt.football_state.services.schedule_event_factory import ScheduleEventFactory


def game():
    return CanonicalGameContext(
        game_id="2026_04_ATL_CAR",
        season=2026,
        week=4,
        season_type="REG",
        home_team="CAR",
        away_team="ATL",
        kickoff_at=datetime(2026, 9, 27, 17, 0, tzinfo=timezone.utc),
    )


def schedule(**overrides):
    values = {
        "team": "ATL",
        "season": 2026,
        "as_of_week": 4,
        "next_game": game(),
        "opponent": "CAR",
        "venue_side": VenueSide.AWAY,
        "bye_week": False,
        "days_rest": 7.0,
        "previous_game_id": "2026_03_TB_ATL",
    }
    values.update(overrides)
    return UpcomingScheduleContext(**values)


def matchup(tendency=MatchupTendency.FAVORABLE, score=0.25):
    return MatchupContext(
        team="ATL",
        opponent="CAR",
        position="RB",
        season=2026,
        week=4,
        tendency=tendency,
        score=score,
        confidence=0.82,
        metrics=(OpponentMetric("rb_rushing_yards_allowed", 125, 100, sample_games=3),),
        reason="rb_rushing_yards_allowed +25.0% vs league average",
        source="nflverse team defense",
        evidence={"provider": "nflverse"},
    )


def test_normal_schedule_context_is_neutral_evidence():
    event = ScheduleEventFactory().build_schedule_event(
        schedule(), player_id="bijan", player_name="Bijan Robinson"
    )

    assert event.event_type == "schedule_context"
    assert event.sentiment == "neutral"
    assert event.impact_score == 0
    assert event.evidence["schedule_context"]["opponent"] == "CAR"


def test_short_rest_is_small_negative_modifier():
    event = ScheduleEventFactory().build_schedule_event(
        schedule(days_rest=5.0), player_id="bijan", player_name="Bijan Robinson"
    )

    assert event.sentiment == "negative"
    assert event.impact_score == -0.15


def test_extended_rest_is_small_positive_modifier():
    event = ScheduleEventFactory().build_schedule_event(
        schedule(days_rest=10.0), player_id="bijan", player_name="Bijan Robinson"
    )

    assert event.sentiment == "positive"
    assert event.impact_score == 0.10


def test_bye_week_remains_context_not_negative_player_evidence():
    event = ScheduleEventFactory().build_schedule_event(
        schedule(next_game=None, opponent=None, venue_side=None, bye_week=True, days_rest=None),
        player_id="bijan",
        player_name="Bijan Robinson",
    )

    assert event.sentiment == "neutral"
    assert event.impact_score == 0
    assert event.evidence["schedule_context"]["bye_week"] is True


def test_favorable_matchup_becomes_positive_evidence():
    event = ScheduleEventFactory().build_matchup_event(
        matchup(), player_id="bijan", player_name="Bijan Robinson"
    )

    assert event.event_type == "matchup_context"
    assert event.sentiment == "positive"
    assert event.impact_score > 0


def test_unfavorable_matchup_becomes_negative_evidence():
    event = ScheduleEventFactory().build_matchup_event(
        matchup(MatchupTendency.UNFAVORABLE, -0.30),
        player_id="bijan",
        player_name="Bijan Robinson",
    )

    assert event.sentiment == "negative"
    assert event.impact_score < 0


def test_unknown_matchup_does_not_force_direction():
    event = ScheduleEventFactory().build_matchup_event(
        matchup(MatchupTendency.UNKNOWN, 0.0),
        player_id="bijan",
        player_name="Bijan Robinson",
    )

    assert event.sentiment == "neutral"
    assert event.impact_score == 0


def test_matchup_provenance_and_metrics_are_preserved():
    event = ScheduleEventFactory().build_matchup_event(
        matchup(), player_id="bijan", player_name="Bijan Robinson"
    )

    evidence = event.evidence["matchup_context"]
    assert evidence["provenance"]["provider"] == "nflverse"
    assert evidence["metrics"][0]["name"] == "rb_rushing_yards_allowed"


def test_schedule_and_matchup_events_pass_through_signal_processor():
    factory = ScheduleEventFactory()
    events = [
        factory.build_schedule_event(schedule(), player_id="bijan", player_name="Bijan Robinson"),
        factory.build_matchup_event(matchup(), player_id="bijan", player_name="Bijan Robinson"),
    ]

    signals = [SignalProcessor().process(event, entities=[]) for event in events]

    assert signals[0].signal_type == "schedule_context"
    assert signals[0].impact_score == 0
    assert signals[1].signal_type == "matchup_context"
    assert signals[1].impact_score > 0


def test_schedule_event_identity_is_deterministic():
    factory = ScheduleEventFactory()
    first = factory.build_schedule_event(schedule(), player_id="bijan", player_name="Bijan Robinson")
    second = factory.build_schedule_event(schedule(), player_id="bijan", player_name="Bijan Robinson")

    assert first.evidence["source_id"] == second.evidence["source_id"]
    assert first.fingerprint() == second.fingerprint()
