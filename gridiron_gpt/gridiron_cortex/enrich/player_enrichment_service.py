from collections.abc import Callable, Iterable
from typing import Any, Optional

from gridiron_cortex.models.raw_event import RawEvent

PlayerRecord = dict[str, Any]
CatalogLoader = Callable[[], Iterable[PlayerRecord]]


class PlayerEnrichmentService:
    """
    Enrich RawEvents with canonical player metadata supplied
    by the host application.
    """

    def __init__(
        self,
        catalog_loader: CatalogLoader | None = None,
    ) -> None:
        self._catalog_loader = catalog_loader

    def enrich(self, event: RawEvent) -> RawEvent:
        if not event.player or self._catalog_loader is None:
            return event

        player = self._find_player(event.player)

        if player is None:
            return event

        event.player = player["player"]

        if not event.team:
            event.team = player.get("team")

        event.player_id = player.get("gsis_id")
        event.position = player.get("position")

        return event

    def _find_player(
        self,
        name: str,
    ) -> Optional[PlayerRecord]:
        search = name.casefold()

        for player in self._catalog_loader():
            aliases = player.get("aliases", [])

            if search in (
                alias.casefold()
                for alias in aliases
            ):
                return player

        return None
