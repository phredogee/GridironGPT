from datetime import datetime, timezone

from gridiron_cortex.events.event import CortexEvent
from gridiron_cortex.events.event_bus import CortexEventBus
from gridiron_cortex.events.event_types import CortexEventType
from gridiron_cortex.events.jsonl_event_store import JsonlCortexEventStore


def _event():
    return CortexEvent(
        event_id="evt-persist-1",
        timestamp=datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc),
        event_type=CortexEventType.ARTICLE_RECEIVED,
        entity_name="Tank Dell",
        source="ESPN",
        correlation_id="corr-persist-1",
        payload={"headline": "Tank Dell returns to practice"},
    )


def test_jsonl_store_survives_reconstruction(tmp_path):
    path = tmp_path / "cortex_events.jsonl"
    first = JsonlCortexEventStore(path)
    first.append(_event())

    second = JsonlCortexEventStore(path)
    assert len(second.all()) == 1
    assert second.all()[0].event_id == "evt-persist-1"
    assert second.all()[0].payload["headline"] == "Tank Dell returns to practice"


def test_jsonl_store_deduplicates_event_id(tmp_path):
    path = tmp_path / "cortex_events.jsonl"
    store = JsonlCortexEventStore(path)
    event = _event()
    store.append(event)
    store.append(event)
    assert len(store.all()) == 1
    assert len(path.read_text(encoding="utf-8").splitlines()) == 1


def test_event_bus_replays_persisted_history(tmp_path):
    path = tmp_path / "cortex_events.jsonl"
    CortexEventBus(store=JsonlCortexEventStore(path)).publish(_event())

    restored = CortexEventBus(store=JsonlCortexEventStore(path))
    history = restored.history(correlation_id="corr-persist-1")
    assert len(history) == 1
    assert history[0].entity_name == "Tank Dell"
