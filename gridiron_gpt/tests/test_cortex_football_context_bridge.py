from dataclasses import dataclass

from gridiron_cortex.models.entity import Entity


@dataclass
class StubFootballContext:
    player_id: str


class StubFootballContextService:
    def __init__(self):
        self.calls = []

    def for_player(self, player_id):
        self.calls.append(player_id)
        return StubFootballContext(player_id=player_id)


def _attach_context(entities, service):
    """Mirror the Cortex bridge contract without exercising scoring behavior."""
    attached = {}
    if service is None:
        return attached

    for entity in entities:
        if entity.entity_type != "player" or not entity.player_id:
            continue
        football_context = service.for_player(entity.player_id)
        if football_context is not None:
            attached[entity.player_id] = football_context
    return attached


def test_resolved_player_with_id_receives_football_context():
    service = StubFootballContextService()
    entities = [
        Entity(
            entity_type="player",
            name="C.J. Stroud",
            player_id="00-0039163",
            team="HOU",
            position="QB",
        )
    ]

    attached = _attach_context(entities, service)

    assert service.calls == ["00-0039163"]
    assert attached["00-0039163"].player_id == "00-0039163"


def test_non_player_and_player_without_id_do_not_trigger_lookup():
    service = StubFootballContextService()
    entities = [
        Entity(entity_type="team", name="Houston Texans", team="HOU"),
        Entity(entity_type="player", name="Unknown Player", player_id=None),
    ]

    attached = _attach_context(entities, service)

    assert service.calls == []
    assert attached == {}


def test_missing_context_service_preserves_no_context_behavior():
    entities = [
        Entity(
            entity_type="player",
            name="C.J. Stroud",
            player_id="00-0039163",
        )
    ]

    assert _attach_context(entities, None) == {}
