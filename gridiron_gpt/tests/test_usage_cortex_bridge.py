from gridiron_cortex.understand.signal_processor import SignalProcessor
from gridiron_gpt.football_state.models.opportunity_change import (
    OpportunityChange,
    OpportunityDirection,
)
from gridiron_gpt.football_state.models.opportunity_reconciliation import (
    OpportunityConfirmation,
    OpportunityReconciliationResult,
)
from gridiron_gpt.football_state.models.usage_state import CanonicalUsageState
from gridiron_gpt.football_state.models.usage_trend import (
    UsageTrendDirection,
    UsageTrendResult,
)
from gridiron_gpt.football_state.services.usage_event_factory import UsageEventFactory


def trend(direction=UsageTrendDirection.RISING, prior_games=3):
    current = CanonicalUsageState(
        player_id="allgeier",
        player_name="Tyler Allgeier",
        season=2026,
        week=4,
        team="ATL",
        carries=16,
        targets=4,
    )
    return UsageTrendResult(
        player_id="allgeier",
        player_name="Tyler Allgeier",
        direction=direction,
        current=current,
        prior_games=prior_games,
        reason=f"usage trend {direction.value}",
    )


def reconciliation(confirmation, predicted_direction=OpportunityDirection.INCREASED):
    predicted = OpportunityChange(
        source_player_id="bijan",
        source_player_name="Bijan Robinson",
        affected_player_id="allgeier",
        affected_player_name="Tyler Allgeier",
        relationship_type="backs_up",
        direction=predicted_direction,
        magnitude=0.55,
        reason="Bijan Robinson --backs_up(-0.55)--> Tyler Allgeier",
    )
    observed_direction = (
        UsageTrendDirection.RISING
        if confirmation == OpportunityConfirmation.CONFIRMED and predicted_direction == OpportunityDirection.INCREASED
        else UsageTrendDirection.FALLING
    )
    observed = trend(observed_direction)
    return OpportunityReconciliationResult(
        player_id="allgeier",
        player_name="Tyler Allgeier",
        confirmation=confirmation,
        predicted=predicted,
        observed=observed,
        confidence=0.86,
        reason=f"prediction {confirmation.value}",
    )


def test_rising_usage_becomes_positive_cortex_evidence():
    event = UsageEventFactory().build_trend_event(trend())

    assert event.event_type == "usage_trend"
    assert event.sentiment == "positive"
    assert event.impact_score > 0


def test_falling_usage_becomes_negative_cortex_evidence():
    event = UsageEventFactory().build_trend_event(trend(UsageTrendDirection.FALLING))

    assert event.sentiment == "negative"
    assert event.impact_score < 0


def test_mixed_usage_remains_neutral():
    event = UsageEventFactory().build_trend_event(trend(UsageTrendDirection.MIXED))

    assert event.sentiment == "neutral"
    assert event.impact_score == 0


def test_confirmed_increased_opportunity_is_positive():
    event = UsageEventFactory().build_reconciliation_event(
        reconciliation(OpportunityConfirmation.CONFIRMED)
    )

    assert event.sentiment == "positive"
    assert event.impact_score > 0


def test_contradicted_increased_opportunity_is_negative():
    event = UsageEventFactory().build_reconciliation_event(
        reconciliation(OpportunityConfirmation.CONTRADICTED)
    )

    assert event.sentiment == "negative"
    assert event.impact_score < 0


def test_confirmed_decreased_opportunity_is_negative():
    event = UsageEventFactory().build_reconciliation_event(
        reconciliation(
            OpportunityConfirmation.CONFIRMED,
            OpportunityDirection.DECREASED,
        )
    )

    assert event.sentiment == "negative"
    assert event.impact_score < 0


def test_inconclusive_reconciliation_does_not_force_fantasy_direction():
    event = UsageEventFactory().build_reconciliation_event(
        reconciliation(OpportunityConfirmation.INCONCLUSIVE)
    )

    assert event.sentiment == "neutral"
    assert event.impact_score == 0


def test_usage_events_pass_through_normal_signal_processor():
    factory = UsageEventFactory()
    events = [
        factory.build_trend_event(trend()),
        factory.build_reconciliation_event(reconciliation(OpportunityConfirmation.CONFIRMED)),
    ]

    signals = [SignalProcessor().process(event, entities=[]) for event in events]

    assert signals[0].signal_type == "usage_trend"
    assert signals[0].impact_score > 0
    assert signals[1].signal_type == "opportunity_confirmation"
    assert signals[1].impact_score > 0


def test_usage_event_identity_is_deterministic():
    factory = UsageEventFactory()

    first = factory.build_trend_event(trend())
    second = factory.build_trend_event(trend())

    assert first.evidence["source_id"] == second.evidence["source_id"]
    assert first.fingerprint() == second.fingerprint()
