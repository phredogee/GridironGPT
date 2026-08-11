from gridiron_cortex.models.entity import Entity


class EntityResolver:
    """
    Resolves fantasy-relevant entities from an event.
    """

    def resolve(self, event):
        entities = []

        player = getattr(event, "player", None)
        player_id = getattr(event, "player_id", None)
        team = getattr(event, "team", None)
        position = getattr(event, "position", None)

        if player:
            entities.append(
                Entity(
                    entity_type="player",
                    name=player,
                    player_id=player_id,
                    team=team,
                    position=position,
                    confidence=1.0,
                    source="event.player",
                )
            )

        if team:
            entities.append(
                Entity(
                    entity_type="team",
                    name=team,
                    team=team,
                    confidence=1.0,
                    source="event.team",
                )
            )

        return entities
