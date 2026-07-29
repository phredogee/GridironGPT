from functools import lru_cache
from typing import Optional

from gridiron_cortex.models.raw_event import RawEvent
from gridiron_gpt.data_ingest.player_catalog import load_player_catalog


@lru_cache(maxsize=1)
def _catalog():
    return load_player_catalog()


class PlayerEnrichmentService:
    """
    Enrich RawEvents with canonical player metadata.
    """

    def enrich(self, event: RawEvent) -> RawEvent:
        if not event.player:
            return event

        player = self._find_player(event.player)

        if player is None:
            return event

        event.player = player["player"]

        if not event.team:
            event.team = player["team"]

        event.player_id = player["gsis_id"]
        event.position = player["position"]

        return event

    def _find_player(self, name: str) -> Optional[dict]:
        search = name.casefold()

        for player in _catalog():
            if search in (alias.casefold() for alias in player["aliases"]):
                return player

        return None
