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
