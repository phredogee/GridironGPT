
from gridiron_cortex.engine.signal_processor import SignalProcessor
from gridiron_cortex.models.entity import Entity
from gridiron_cortex.models.raw_event import RawEvent


def test_signal_processor_detects_positive_signal():
    processor = SignalProcessor()

    event = RawEvent(
        headline=(
            "Test Player returns to practice with "
            "the first-team offense."
        ),
        source="test",
        player="Test Player",
        team="TST",
    )

    entities = [
        Entity(
            entity_type="player",
            name="Test Player",
            team="TST",
            confidence=1.0,
            source="event.player",
        )
    ]

    signal = processor.process(event, entities)

    assert signal.sentiment == "positive"
    assert signal.impact_score > 0
    assert signal.entities == entities
    assert "returns" in signal.positive_hits
    assert "first-team" in signal.positive_hits


def test_signal_processor_detects_negative_signal():
    processor = SignalProcessor()

    event = RawEvent(
        headline="Test Player suffers an injury and misses practice.",
        source="test",
        player="Test Player",
        team="TST",
    )

    entities = [
        Entity(
            entity_type="player",
            name="Test Player",
            team="TST",
            confidence=1.0,
            source="event.player",
        )
    ]

    signal = processor.process(event, entities)

    assert signal.sentiment == "negative"
    assert signal.impact_score < 0
    assert signal.negative_hits

def test_signal_processor_understands_aims_to_play():
    processor = SignalProcessor()

    event = RawEvent(
        headline="Patrick Mahomes aims to play Week 1.",
        source="test",
        player="Patrick Mahomes",
        team="KC",
    )

    signal = processor.process(
        event,
        entities=[],
    )

    assert signal.sentiment == "positive"
    assert signal.impact_score == 0.9
    assert signal.confidence == 0.9
    assert "return_to_play" in signal.positive_hits
    assert signal.evidence["classification"] == "return_to_play"


def test_signal_processor_understands_timeshare():
    processor = SignalProcessor()

    event = RawEvent(
        headline="Bhayshul Tuten: Backfield timeshare likely.",
        source="test",
        player="Bhayshul Tuten",
        team="JAX",
    )

    signal = processor.process(
        event,
        entities=[],
    )

    assert signal.sentiment == "negative"
    assert signal.impact_score == -0.6
    assert signal.confidence == 0.85
    assert "timeshare" in signal.negative_hits
    assert signal.evidence["classification"] == "timeshare"


def test_signal_processor_combines_multiple_concepts():
    processor = SignalProcessor()

    event = RawEvent(
        headline=(
            "Test Player returns to practice but "
            "will remain in a backfield timeshare."
        ),
        source="test",
        player="Test Player",
        team="TST",
    )

    signal = processor.process(
        event,
        entities=[],
    )

    assert signal.sentiment == "positive"
    assert signal.impact_score == 0.3
    assert signal.evidence["classification"] == "multi_concept"
    assert signal.evidence["evidence_count"] == 2


def test_structured_intelligence_overrides_concept_matching():
    processor = SignalProcessor()

    event = RawEvent(
        headline="Test Player listed in a timeshare.",
        source="nflverse",
        player="Test Player",
        team="TST",
        sentiment="positive",
        impact_score=0.75,
        confidence=0.92,
        evidence={
            "methods": ["statistical_model"],
        },
    )

    signal = processor.process(
        event,
        entities=[],
    )

    assert signal.sentiment == "positive"
    assert signal.impact_score == 0.75
    assert signal.confidence == 0.92
    assert signal.evidence["methods"] == [
        "statistical_model"
    ]

def test_signal_processor_understands_workhorse_back():
    processor = SignalProcessor()

    event = RawEvent(
        headline="The coaching staff plans to use Test Runner as a workhorse.",
        source="test",
        player="Test Runner",
        team="TST",
    )

    signal = processor.process(
        event,
        entities=[],
    )

    assert signal.sentiment == "positive"
    assert signal.impact_score == 0.9
    assert signal.confidence == 0.92
    assert "workhorse_back" in signal.positive_hits
    assert signal.evidence["classification"] == "workhorse_back"

def test_signal_processor_understands_favorite_receiver():
    processor = SignalProcessor()

    event = RawEvent(
        headline="Test Receiver has become the quarterback's favorite target.",
        source="test",
        player="Test Receiver",
        team="TST",
    )

    signal = processor.process(
        event,
        entities=[],
    )

    assert signal.sentiment == "positive"
    assert signal.impact_score == 0.85
    assert signal.confidence == 0.9
    assert "favorite_receiver" in signal.positive_hits
    assert signal.evidence["classification"] == "favorite_receiver"

def test_workhorse_back_has_rushing_opportunity_category():
    processor = SignalProcessor()

    event = RawEvent(
        headline="The team plans to use Test Runner as a workhorse.",
        source="test",
        player="Test Runner",
        team="TST",
    )

    signal = processor.process(
        event,
        entities=[],
    )

    assert signal.evidence["categories"] == [
        "rushing_opportunity"
    ]

    assert signal.evidence["concepts"][0]["category"] == (
        "rushing_opportunity"
    )


def test_favorite_receiver_has_receiving_opportunity_category():
    processor = SignalProcessor()

    event = RawEvent(
        headline=(
            "Test Receiver has become the quarterback's "
            "favorite target."
        ),
        source="test",
        player="Test Receiver",
        team="TST",
    )

    signal = processor.process(
        event,
        entities=[],
    )

    assert signal.evidence["categories"] == [
        "receiving_opportunity"
    ]

    assert signal.evidence["concepts"][0]["category"] == (
        "receiving_opportunity"
    )


def test_multiple_concepts_preserve_unique_categories():
    processor = SignalProcessor()

    event = RawEvent(
        headline=(
            "Test Runner returned to practice and is expected "
            "to handle a heavy workload."
        ),
        source="test",
        player="Test Runner",
        team="TST",
    )

    signal = processor.process(
        event,
        entities=[],
    )

    assert signal.evidence["classification"] == "multi_concept"

    assert signal.evidence["categories"] == [
        "health",
        "rushing_opportunity",
    ]

def test_signal_processor_understands_camp_standout():
    event = RawEvent(
        headline="The rookie is turning heads and has been a camp standout.",
        source="test",
    )

    signal = SignalProcessor().process(event, entities=[])

    assert signal.sentiment == "positive"
    assert signal.evidence["classification"] == "camp_standout"
    assert "training_camp" in signal.evidence["categories"]


def test_signal_processor_understands_camp_role_loss():
    event = RawEvent(
        headline="The receiver is losing reps during training camp.",
        source="test",
    )

    signal = SignalProcessor().process(event, entities=[])

    assert signal.sentiment == "negative"
    assert signal.evidence["classification"] == "camp_role_loss"

def test_out_keyword_does_not_match_inside_standout():
    event = RawEvent(
        headline="The rookie has been a camp standout.",
        source="test",
    )

    signal = SignalProcessor().process(
        event,
        entities=[],
    )

    concept_names = [
        concept["name"]
        for concept in signal.evidence["concepts"]
    ]

    assert signal.sentiment == "positive"
    assert "camp_standout" in concept_names
    assert "injury" not in concept_names

def test_signal_processor_understands_named_starter():
    event = RawEvent(
        headline="Test Player was named the starter.",
        source="test",
    )

    signal = SignalProcessor().process(
        event,
        entities=[],
    )

    assert signal.sentiment == "positive"
    assert signal.evidence["classification"] == "named_starter"
    assert signal.evidence["categories"] == ["depth_chart"]


def test_signal_processor_understands_first_team_role():
    event = RawEvent(
        headline="Test Player is practicing with the first team.",
        source="test",
    )

    signal = SignalProcessor().process(
        event,
        entities=[],
    )

    assert signal.sentiment == "positive"
    assert signal.evidence["classification"] == "first_team_role"
    assert signal.impact_score == 0.8


def test_signal_processor_understands_depth_chart_demotion():
    event = RawEvent(
        headline="Test Player has been moved down the depth chart.",
        source="test",
    )

    signal = SignalProcessor().process(
        event,
        entities=[],
    )

    assert signal.sentiment == "negative"
    assert signal.evidence["classification"] == (
        "depth_chart_demotion"
    )


def test_signal_processor_understands_second_team_role():
    event = RawEvent(
        headline="Test Player is running with the second team.",
        source="test",
    )

    signal = SignalProcessor().process(
        event,
        entities=[],
    )

    assert signal.sentiment == "negative"
    assert signal.evidence["classification"] == "second_team_role"


def test_depth_chart_phrase_is_not_double_counted():
    event = RawEvent(
        headline="Test Player is taking first-team reps.",
        source="test",
    )

    signal = SignalProcessor().process(
        event,
        entities=[],
    )

    concept_names = [
        concept["name"]
        for concept in signal.evidence["concepts"]
    ]

    assert concept_names == ["first_team_role"]
