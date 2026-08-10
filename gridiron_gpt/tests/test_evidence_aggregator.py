import pytest

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.understand.evidence_aggregator import (
    EvidenceAggregator,
)


@pytest.fixture
def aggregator() -> EvidenceAggregator:
    return EvidenceAggregator()


def make_event(
    *,
    headline: str,
    source: str,
    player: str = "Tank Dell",
    team: str = "HOU",
    url: str | None = None,
) -> RawEvent:
    return RawEvent(
        headline=headline,
        source=source,
        player=player,
        team=team,
        url=url,
    )


def test_new_event_creates_canonical_event(
    aggregator: EvidenceAggregator,
):
    event = make_event(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        url="https://example.com/espn/tank-dell-practice",
    )

    canonical = aggregator.add(event)

    assert canonical.player == "Tank Dell"
    assert canonical.team == "HOU"
    assert canonical.category == "injury"
    assert canonical.subtype == "returned_to_practice"
    assert canonical.polarity == "positive"
    assert canonical.impact > 0
    assert canonical.confidence > 0
    assert len(canonical.evidence) == 1


def test_duplicate_article_is_not_added_twice(
    aggregator: EvidenceAggregator,
):
    event = make_event(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        url="https://example.com/espn/tank-dell-practice",
    )

    first_result = aggregator.add(event)
    second_result = aggregator.add(event)

    assert first_result is second_result
    assert len(second_result.evidence) == 1
    assert len(second_result.sources) == 1


def test_two_sources_merge_into_one_canonical_event(
    aggregator: EvidenceAggregator,
):
    espn_event = make_event(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        url="https://example.com/espn/tank-dell-practice",
    )

    nbc_event = make_event(
        headline="Tank Dell returned to practice with Houston.",
        source="NBC Sports",
        url="https://example.com/nbc/tank-dell-practice",
    )

    first_result = aggregator.add(espn_event)
    second_result = aggregator.add(nbc_event)

    assert first_result is second_result
    assert len(second_result.evidence) == 2
    assert set(second_result.sources) == {
        "ESPN",
        "NBC Sports",
    }


def test_confidence_increases_with_multiple_sources(
    aggregator: EvidenceAggregator,
):
    first_event = make_event(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        url="https://example.com/espn/tank-dell-practice",
    )

    second_event = make_event(
        headline="Tank Dell returned to practice with Houston.",
        source="NBC Sports",
        url="https://example.com/nbc/tank-dell-practice",
    )

    canonical = aggregator.add(first_event)
    initial_confidence = canonical.confidence

    updated_canonical = aggregator.add(second_event)

    assert updated_canonical.confidence > initial_confidence
    assert updated_canonical.confidence <= 1.0


def test_different_players_do_not_merge(
    aggregator: EvidenceAggregator,
):
    tank_event = make_event(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        player="Tank Dell",
        url="https://example.com/tank-dell-practice",
    )

    nico_event = make_event(
        headline="Nico Collins returns to practice.",
        source="ESPN",
        player="Nico Collins",
        url="https://example.com/nico-collins-practice",
    )

    tank_canonical = aggregator.add(tank_event)
    nico_canonical = aggregator.add(nico_event)

    assert tank_canonical is not nico_canonical
    assert tank_canonical.event_key != nico_canonical.event_key
    assert tank_canonical.player == "Tank Dell"
    assert nico_canonical.player == "Nico Collins"


def test_different_teams_do_not_merge(
    aggregator: EvidenceAggregator,
):
    houston_event = make_event(
        headline="Test Player returns to practice.",
        source="ESPN",
        player="Test Player",
        team="HOU",
        url="https://example.com/houston/test-player",
    )

    dallas_event = make_event(
        headline="Test Player returns to practice.",
        source="NBC Sports",
        player="Test Player",
        team="DAL",
        url="https://example.com/dallas/test-player",
    )

    houston_canonical = aggregator.add(houston_event)
    dallas_canonical = aggregator.add(dallas_event)

    assert houston_canonical is not dallas_canonical
    assert houston_canonical.event_key != dallas_canonical.event_key


def test_different_subtypes_do_not_merge(
    aggregator: EvidenceAggregator,
):
    practice_event = make_event(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        url="https://example.com/tank-dell-practice",
    )

    injured_reserve_event = make_event(
        headline="Tank Dell placed on injured reserve.",
        source="NBC Sports",
        url="https://example.com/tank-dell-injured-reserve",
    )

    practice_canonical = aggregator.add(practice_event)
    reserve_canonical = aggregator.add(injured_reserve_event)

    assert practice_canonical is not reserve_canonical
    assert practice_canonical.event_key != reserve_canonical.event_key
    assert practice_canonical.subtype == "returned_to_practice"
    assert reserve_canonical.subtype == "injured_reserve"


def test_player_and_team_normalization_produce_same_event_key(
    aggregator: EvidenceAggregator,
):
    first_event = make_event(
        headline="Tank Dell returns to practice.",
        source="ESPN",
        player="Tank Dell",
        team="HOU",
        url="https://example.com/espn/tank-dell",
    )

    second_event = make_event(
        headline="Tank Dell returned to practice.",
        source="NBC Sports",
        player="  TANK   DELL  ",
        team=" hou ",
        url="https://example.com/nbc/tank-dell",
    )

    first_canonical = aggregator.add(first_event)
    second_canonical = aggregator.add(second_event)

    assert first_canonical is second_canonical
    assert first_canonical.event_key == second_canonical.event_key
    assert len(second_canonical.evidence) == 2


def test_unknown_events_for_different_players_do_not_merge(
    aggregator: EvidenceAggregator,
):
    first_event = make_event(
        headline="Tank Dell attended a community event.",
        source="Local News",
        player="Tank Dell",
        url="https://example.com/tank-community-event",
    )

    second_event = make_event(
        headline="Nico Collins attended a community event.",
        source="Local News",
        player="Nico Collins",
        url="https://example.com/nico-community-event",
    )

    first_canonical = aggregator.add(first_event)
    second_canonical = aggregator.add(second_event)

    assert first_canonical.category == "unknown"
    assert second_canonical.category == "unknown"
    assert first_canonical.event_key != second_canonical.event_key

def test_conflicting_reports_do_not_merge(
    aggregator: EvidenceAggregator,
):
    practice_event = make_event(
        headline="Tank Dell practiced in full.",
        source="ESPN",
        url="https://example.com/full-practice",
    )

    limited_event = make_event(
        headline="Tank Dell was a limited participant in practice.",
        source="NBC Sports",
        url="https://example.com/limited-practice",
    )

    practice_canonical = aggregator.add(practice_event)
    limited_canonical = aggregator.add(limited_event)

    assert practice_canonical is not limited_canonical

    assert practice_canonical.subtype == "full_practice"
    assert limited_canonical.subtype == "limited_practice"

    assert practice_canonical.event_key != limited_canonical.event_key
