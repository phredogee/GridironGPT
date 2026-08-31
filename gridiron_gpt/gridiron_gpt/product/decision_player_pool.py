from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from gridiron_gpt.fantasy_decisions.models import PlayerDecisionInput


FANTASY_PLAYER_POSITIONS = frozenset({"QB", "RB", "FB", "WR", "TE", "K"})


def build_decision_player_pool(
    catalog: Iterable[Mapping[str, Any]],
    score_data: Mapping[tuple[str, str], Mapping[str, Any]],
    *,
    confidence_from_signals: Callable[[list[Any]], float],
) -> list[PlayerDecisionInput]:
    """Build the Decision Center player universe from the canonical roster catalog.

    The player catalog is authoritative for identity, team, and position. Cortex score
    data enriches catalog players when a current score exists, but players are not
    dropped merely because they have no recent signals.
    """

    scores_by_name: dict[str, tuple[str, Mapping[str, Any]]] = {}
    for (name, team), data in score_data.items():
        scores_by_name.setdefault(name, (team, data))

    players: list[PlayerDecisionInput] = []

    for item in catalog:
        name = str(item.get("player") or "").strip()
        position = str(item.get("position") or "").strip().upper()

        if not name or position not in FANTASY_PLAYER_POSITIONS:
            continue

        catalog_team = str(item.get("team") or "").strip().upper()
        scored_team, data = score_data.get(
            (name, catalog_team),
            scores_by_name.get(name, (catalog_team, {})),
        )

        signals = list(data.get("signals", []))
        score = float(data.get("score", 0.0))
        team = str(scored_team or catalog_team or "FA")

        players.append(
            PlayerDecisionInput(
                player_id=str(
                    item.get("gsis_id")
                    or item.get("player_id")
                    or name.casefold().replace(" ", "-")
                ),
                player_name=name,
                position=position,
                team=team,
                cortex_score=score,
                confidence=(
                    confidence_from_signals(signals) / 100.0 if signals else 0.0
                ),
                projected_points=max(0.0, 10.0 + score),
                replacement_value=max(0.0, score / 2.0),
                evidence={"signals": signals},
            )
        )

    return sorted(players, key=lambda player: player.player_name.casefold())
