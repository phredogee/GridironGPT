from gridiron_gpt.draft.fantasy_draft_settings import FantasyDraftSettings
from gridiron_gpt.draft.fantasy_wait_risk_ui import build_wait_risk_display


def test_display_propagates_draft_settings_and_live_drafted_count() -> None:
    settings = FantasyDraftSettings(league_size=12, draft_slot=8)

    display = build_wait_risk_display(
        player_id="wr-1",
        ranking_score=90.0,
        consensus_adp=10.4,
        drafted_count=7,
        settings=settings,
    )

    assert display.current_pick == 8
    assert display.next_pick == 17
    assert display.is_user_turn is True
    assert display.context_label == "Current Pick 8 · You are on the clock · Next Pick 17"
    assert display.risk_label == "HIGH WAIT RISK"
    assert display.recommendation_label == "unlikely to reach Pick 17"


def test_display_keeps_low_risk_separate_from_pick_timing() -> None:
    settings = FantasyDraftSettings(league_size=12, draft_slot=8)

    display = build_wait_risk_display(
        player_id="wr-2",
        ranking_score=87.0,
        consensus_adp=25.2,
        drafted_count=7,
        settings=settings,
    )

    assert display.risk_label == "LOW WAIT RISK"
    assert display.recommendation_label == "likely to reach Pick 17"


def test_display_handles_missing_market_adp_without_guessing() -> None:
    settings = FantasyDraftSettings(league_size=12, draft_slot=8)

    display = build_wait_risk_display(
        player_id="te-1",
        ranking_score=84.0,
        consensus_adp=None,
        drafted_count=7,
        settings=settings,
    )

    assert display.risk_label == "WAIT RISK UNKNOWN"
    assert display.recommendation_label == "next-pick availability unknown"
    assert "ADP" in display.reason


def test_display_preserves_authoritative_board_score() -> None:
    settings = FantasyDraftSettings(league_size=10, draft_slot=4)

    display = build_wait_risk_display(
        player_id="qb-1",
        ranking_score=91.23,
        consensus_adp=5.0,
        drafted_count=3,
        settings=settings,
    )

    assert display.ranking_score == 91.23


def test_before_user_turn_is_presented_as_upcoming_pick_availability() -> None:
    settings = FantasyDraftSettings(league_size=12, draft_slot=8)

    display = build_wait_risk_display(
        player_id="rb-1",
        ranking_score=86.5,
        consensus_adp=1.5,
        drafted_count=0,
        settings=settings,
    )

    assert display.current_pick == 1
    assert display.next_pick == 8
    assert display.is_user_turn is False
    assert display.context_label == "Current Pick 1 · Your Upcoming Pick 8"
    assert display.risk_label == "AVAILABILITY AT PICK 8 · HIGH RISK"
    assert display.recommendation_label == "unlikely to reach your pick"


def test_before_user_turn_low_risk_uses_availability_wording() -> None:
    settings = FantasyDraftSettings(league_size=12, draft_slot=8)

    display = build_wait_risk_display(
        player_id="rb-2",
        ranking_score=80.0,
        consensus_adp=25.3,
        drafted_count=0,
        settings=settings,
    )

    assert display.risk_label == "AVAILABILITY AT PICK 8 · LOW RISK"
    assert display.recommendation_label == "likely to reach your pick"
