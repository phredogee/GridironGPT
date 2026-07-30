from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.understand.event_classifier import EventClassifier


def test_classifies_returned_to_practice() -> None:
    classifier = EventClassifier()

    event = RawEvent(
        headline="Sam LaPorta cleared for training camp",
        source="RotoWire",
        player="Sam LaPorta",
        team="DET",
    )

    result = classifier.classify(event)

    assert result.category == "injury"
    assert result.subtype == "returned_to_practice"
    assert result.polarity == "positive"
    assert result.confidence == 0.95
    assert "cleared for training camp" in result.matched_rules


def test_classifies_injured_reserve() -> None:
    classifier = EventClassifier()

    event = RawEvent(
        headline="Running back placed on injured reserve",
        source="ESPN",
        player="Example Player",
    )

    result = classifier.classify(event)

    assert result.category == "injury"
    assert result.subtype == "injured_reserve"
    assert result.polarity == "negative"


def test_classifies_first_team_reps() -> None:
    classifier = EventClassifier()

    event = RawEvent(
        headline="Receiver working with the starters during camp",
        source="NBC",
        player="Example Receiver",
    )

    result = classifier.classify(event)

    assert result.category == "depth_chart"
    assert result.subtype == "first_team_reps"
    assert result.polarity == "positive"


def test_classifies_contract_extension() -> None:
    classifier = EventClassifier()

    event = RawEvent(
        headline="Linebacker agreed to a contract extension",
        source="ESPN",
        player="Example Linebacker",
    )

    result = classifier.classify(event)

    assert result.category == "transaction"
    assert result.subtype == "contract_extension"


def test_returns_unknown_for_unmatched_event() -> None:
    classifier = EventClassifier()

    event = RawEvent(
        headline="Team releases its updated stadium parking policy",
        source="Team Site",
    )

    result = classifier.classify(event)

    assert result.category == "unknown"
    assert result.subtype == "unclassified"
    assert result.polarity == "neutral"
    assert result.confidence == 0.0
    assert result.matched_rules == []


def test_more_specific_rule_wins() -> None:
    classifier = EventClassifier()

    event = RawEvent(
        headline="Player activated from injured reserve and returned to practice",
        source="NFL",
        player="Example Player",
    )

    result = classifier.classify(event)

    assert result.category == "injury"
    assert result.subtype == "activated"
    assert result.confidence == 0.97

def test_classifies_full_practice() -> None:
    classifier = EventClassifier()

    event = RawEvent(
        headline="Tank Dell cleared for full practice participation",
        source="NBC Sports",
        player="Tank Dell",
    )

    result = classifier.classify(event)

    assert result.category == "injury"
    assert result.subtype == "full_practice"
    assert result.polarity == "positive"

def test_classifies_limited_practice() -> None:
    classifier = EventClassifier()

    event = RawEvent(
        headline="Tank Dell was a limited participant in practice",
        source="ESPN",
        player="Tank Dell",
    )

    result = classifier.classify(event)

    assert result.category == "injury"
    assert result.subtype == "limited_practice"
    assert result.polarity == "monitor"

def test_classifies_pup() -> None:
    classifier = EventClassifier()

    event = RawEvent(
        headline="Christian McCaffrey placed on the PUP list",
        source="NFL",
        player="Christian McCaffrey",
    )

    result = classifier.classify(event)

    assert result.category == "injury"
    assert result.subtype == "placed_on_pup"
    assert result.polarity == "negative"

def test_classifies_game_time_decision() -> None:
    classifier = EventClassifier()

    event = RawEvent(
        headline="Coach says player will be a game-time decision",
        source="ESPN",
        player="Example Player",
    )

    result = classifier.classify(event)

    assert result.category == "injury"
    assert result.subtype == "game_time_decision"

def test_classifies_from_summary() -> None:
    classifier = EventClassifier()

    event = RawEvent(
        headline="Coach provides injury update",
        summary="Tank Dell was cleared for full practice participation Tuesday.",
        source="NBC Sports",
        player="Tank Dell",
    )

    result = classifier.classify(event)

    assert result.category == "injury"
    assert result.subtype == "full_practice"
    assert result.polarity == "positive"
