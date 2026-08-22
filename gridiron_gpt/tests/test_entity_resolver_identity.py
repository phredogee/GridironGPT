from gridiron_cortex.models.raw_event import RawEvent
from gridiron_cortex.understand.entity_resolver import EntityResolver


def test_entity_resolver_preserves_player_id_and_position():
    event = RawEvent(
        headline="C.J. Stroud update",
        source="test",
        player="C.J. Stroud",
        player_id="00-0039163",
        team="HOU",
        position="QB",
    )

    entities = EntityResolver().resolve(event)
    player = next(entity for entity in entities if entity.entity_type == "player")

    assert player.name == "C.J. Stroud"
    assert player.player_id == "00-0039163"
    assert player.team == "HOU"
    assert player.position == "QB"


def test_team_entity_remains_separate_from_player_identity():
    event = RawEvent(
        headline="C.J. Stroud update",
        source="test",
        player="C.J. Stroud",
        player_id="00-0039163",
        team="HOU",
        position="QB",
    )

    entities = EntityResolver().resolve(event)
    team = next(entity for entity in entities if entity.entity_type == "team")

    assert team.name == "HOU"
    assert team.team == "HOU"
    assert team.player_id is None
