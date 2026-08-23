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


def test_classify_all_returns_compound_signals() -> None:
    classifier = EventClassifier()

    event = RawEvent(
        headline="Receiver returned to practice and is working with the starters",
        summary="The receiver is standing out in camp and impressed the coaching staff.",
        source="RotoWire",
        player="Example Receiver",
    )

    results = classifier.classify_all(event)
    identities = [(result.category, result.subtype) for result in results]

    assert identities == [
        ("injury", "returned_to_practice"),
        ("depth_chart", "first_team_reps"),
        ("performance", "coach_praise"),
    ]


def test_classify_all_returns_empty_for_unmatched_event() -> None:
    classifier = EventClassifier()

    event = RawEvent(
        headline="Team announces updated stadium parking policy",
        source="Team Site",
    )

    assert classifier.classify_all(event) == []


def test_classify_remains_compatible_with_multi_signal_events() -> None:
    classifier = EventClassifier()

    event = RawEvent(
        headline="Player returned to practice and is working with the starters",
        source="NFL",
        player="Example Player",
    )

    result = classifier.classify(event)

    assert result.category == "injury"
    assert result.subtype == "returned_to_practice"


def test_live_penix_story_classifies_team_drill_return() -> None:
    classifier = EventClassifier()
    event = RawEvent(
        headline=(
            "Tua Tagovailoa: Penix cleared for team drills, "
            "setting stage for QB competition"
        ),
        summary=(
            "Michael Penix is in line to return to 11-on-11 drills "
            "in Monday's practice."
        ),
        source="RotoWire NFL",
        player="Michael Penix Jr.",
        team="ATL",
    )

    identities = {
        (result.category, result.subtype)
        for result in classifier.classify_all(event)
    }

    assert ("injury", "returned_to_team_drills") in identities


def test_live_penix_story_classifies_qb_competition() -> None:
    classifier = EventClassifier()
    event = RawEvent(
        headline=(
            "Tua Tagovailoa: Penix cleared for team drills, "
            "setting stage for QB competition"
        ),
        source="RotoWire NFL",
        player="Michael Penix Jr.",
        team="ATL",
    )

    identities = {
        (result.category, result.subtype)
        for result in classifier.classify_all(event)
    }

    assert ("depth_chart", "qb_competition") in identities


def test_live_walkthrough_story_classifies_participation() -> None:
    classifier = EventClassifier()
    event = RawEvent(
        headline="Parker Washington: Present for Sunday's walkthrough",
        summary=(
            "Washington (undisclosed) was spotted at Sunday's walkthrough."
        ),
        source="RotoWire NFL",
        player="Parker Washington",
        team="JAX",
    )

    result = classifier.classify(event)

    assert result.category == "participation"
    assert result.subtype == "walkthrough"
    assert result.polarity == "positive"


def test_live_season_ending_achilles_story_classifies_injury() -> None:
    classifier = EventClassifier()
    event = RawEvent(
        headline="Sources: Browns starting DE Wright out for year",
        summary=(
            "The Browns are placing starting defensive end Alex Wright "
            "on season-ending injured reserve with a ruptured Achilles."
        ),
        source="ESPN NFL",
        player="Alex Wright",
        team="CLE",
    )

    result = classifier.classify(event)

    assert result.category == "injury"
    assert result.subtype == "season_ending"
    assert result.polarity == "negative"


def test_generic_wont_play_is_availability_not_injury() -> None:
    classifier = EventClassifier()
    event = RawEvent(
        headline="Jadarian Price: Won't play Sunday",
        source="RotoWire NFL",
        player="Jadarian Price",
        team="SEA",
    )

    result = classifier.classify(event)

    assert result.category == "availability"
    assert result.subtype == "ruled_out"
    assert result.polarity == "negative"


def test_explicit_injury_absence_remains_injury_ruled_out() -> None:
    classifier = EventClassifier()
    event = RawEvent(
        headline="Receiver ruled out with a hamstring injury",
        source="ESPN",
        player="Example Receiver",
    )

    result = classifier.classify(event)

    assert result.category == "injury"
    assert result.subtype == "ruled_out"
    assert result.polarity == "negative"
