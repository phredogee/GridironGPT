from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

import nflreadpy as nfl
import polars as pl

from gridiron_cortex.models.entity_relationship import (
    EntityRelationship,
)


FANTASY_POSITIONS = {"QB", "RB", "WR", "TE"}
ACTIVE_STATUSES = {"ACT"}

PRIMARY_LIMITS = {
    "QB": 2,
    "RB": 3,
    "WR": 3,
    "TE": 2,
}


def _entity_id(name: str) -> str:
    return (
        name.strip()
        .casefold()
        .replace(" ", "_")
    )


def _is_active_fantasy_player(player: dict) -> bool:
    return (
        player.get("position") in FANTASY_POSITIONS
        and player.get("status") in ACTIVE_STATUSES
        and bool(player.get("player"))
        and bool(player.get("team"))
    )


def _relationship(
    source: dict,
    target: dict,
    relationship_type: str,
    strength: float,
    confidence: float,
    reason: str,
    timestamp: str,
) -> EntityRelationship:
    return EntityRelationship(
        source_entity_id=_entity_id(source["player"]),
        source_entity_name=source["player"],
        source_entity_type="player",
        target_entity_id=_entity_id(target["player"]),
        target_entity_name=target["player"],
        target_entity_type="player",
        relationship_type=relationship_type,
        strength=strength,
        confidence=confidence,
        reason=reason,
        source_team=source.get("team"),
        target_team=target.get("team"),
        first_seen=timestamp,
        last_updated=timestamp,
        active=True,
    )


def load_latest_depth_chart() -> list[dict]:
    """
    Load the most recent nflverse depth-chart snapshot for each NFL team.

    nflverse stores historical depth-chart snapshots, so simply loading the
    table would include stale player roles. This function keeps only rows from
    each team's latest available timestamp.
    """

    season = nfl.get_current_season()
    frame = nfl.load_depth_charts([season])

    if frame.is_empty():
        return []

    latest_by_team = (
        frame
        .group_by("team")
        .agg(
            pl.col("dt").max().alias("latest_dt")
        )
    )

    latest = (
        frame
        .join(
            latest_by_team,
            on="team",
            how="inner",
        )
        .filter(
            pl.col("dt") == pl.col("latest_dt")
        )
        .drop("latest_dt")
    )

    return latest.to_dicts()


def _build_catalog_index(
    catalog: list[dict],
) -> dict[str, dict]:
    """
    Index active fantasy players by GSIS ID and normalized name.
    """

    index: dict[str, dict] = {}

    for player in catalog:
        if not _is_active_fantasy_player(player):
            continue

        gsis_id = player.get("gsis_id")

        if gsis_id:
            index[f"gsis:{gsis_id}"] = player

        name = player.get("player")

        if name:
            index[
                f"name:{name.strip().casefold()}"
            ] = player

    return index


def _match_depth_player(
    row: dict,
    catalog_index: dict[str, dict],
) -> dict | None:
    """
    Match a depth-chart entry back to the active player catalog.
    """

    gsis_id = row.get("gsis_id")

    if gsis_id:
        player = catalog_index.get(
            f"gsis:{gsis_id}"
        )

        if player:
            return player

    player_name = row.get("player_name")

    if player_name:
        return catalog_index.get(
            f"name:{player_name.strip().casefold()}"
        )

    return None


def _build_team_depth(
    catalog: list[dict],
    depth_chart: list[dict],
) -> dict[str, dict[str, list[dict]]]:
    """
    Build a depth-aware offensive roster by team and position.
    """

    catalog_index = _build_catalog_index(catalog)

    teams: dict[
        str,
        dict[str, list[dict]],
    ] = defaultdict(
        lambda: defaultdict(list)
    )

    seen: set[tuple[str, str, str]] = set()

    for row in depth_chart:
        position = row.get("pos_abb")

        if position not in FANTASY_POSITIONS:
            continue

        rank = row.get("pos_rank")

        if rank is None:
            continue

        limit = PRIMARY_LIMITS[position]

        if rank > limit:
            continue

        player = _match_depth_player(
            row,
            catalog_index,
        )

        if player is None:
            continue

        team = player.get("team")

        if not team:
            continue

        key = (
            team,
            position,
            player["player"],
        )

        if key in seen:
            continue

        seen.add(key)

        entry = dict(player)
        entry["depth_rank"] = int(rank)
        entry["depth_slot"] = row.get("pos_slot")

        teams[team][position].append(
            entry
        )

    for positions in teams.values():
        for players in positions.values():
            players.sort(
                key=lambda player: (
                    player["depth_rank"],
                    player["player"].casefold(),
                )
            )

    return teams


def _add_backup_relationships(
    relationships: list[EntityRelationship],
    players: list[dict],
    timestamp: str,
    position_label: str,
) -> None:
    """
    Add backup -> starter relationships for one position group.
    """

    if len(players) < 2:
        return

    starter = players[0]

    for backup in players[1:]:
        relationships.append(
            _relationship(
                source=backup,
                target=starter,
                relationship_type="backs_up",
                strength=0.75,
                confidence=0.90,
                reason=(
                    f"{backup['player']} is ranked behind "
                    f"{starter['player']} on the "
                    f"{backup['team']} {position_label} "
                    "depth chart."
                ),
                timestamp=timestamp,
            )
        )


def build_nfl_relationships(
    catalog: list[dict],
    depth_chart: list[dict] | None = None,
) -> list[EntityRelationship]:
    """
    Build depth-aware NFL fantasy relationships.

    Relationship generation intentionally focuses on high-value offensive
    relationships rather than connecting every active teammate.
    """

    if depth_chart is None:
        depth_chart = load_latest_depth_chart()

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    teams = _build_team_depth(
        catalog=catalog,
        depth_chart=depth_chart,
    )

    relationships: list[
        EntityRelationship
    ] = []

    for team, positions in teams.items():
        quarterbacks = positions.get(
            "QB",
            [],
        )
        running_backs = positions.get(
            "RB",
            [],
        )
        receivers = positions.get(
            "WR",
            [],
        )
        tight_ends = positions.get(
            "TE",
            [],
        )

        # --------------------------------------------------------------
        # QB depth hierarchy
        # --------------------------------------------------------------

        _add_backup_relationships(
            relationships=relationships,
            players=quarterbacks,
            timestamp=timestamp,
            position_label="quarterback",
        )

        # --------------------------------------------------------------
        # RB depth hierarchy
        # --------------------------------------------------------------

        _add_backup_relationships(
            relationships=relationships,
            players=running_backs,
            timestamp=timestamp,
            position_label="running back",
        )

        # --------------------------------------------------------------
        # Primary QB offensive relationships
        # --------------------------------------------------------------

        if quarterbacks:
            qb1 = quarterbacks[0]

            for receiver in receivers:
                rank = receiver["depth_rank"]

                strength = {
                    1: 0.95,
                    2: 0.90,
                    3: 0.70,
                }.get(rank, 0.60)

                relationships.append(
                    _relationship(
                        source=qb1,
                        target=receiver,
                        relationship_type="throws_to",
                        strength=strength,
                        confidence=0.95,
                        reason=(
                            f"{qb1['player']} is the "
                            f"{team} QB1 and "
                            f"{receiver['player']} is WR"
                            f"{rank} on the current "
                            "depth chart."
                        ),
                        timestamp=timestamp,
                    )
                )

            for tight_end in tight_ends:
                rank = tight_end["depth_rank"]

                strength = {
                    1: 0.85,
                    2: 0.60,
                }.get(rank, 0.50)

                relationships.append(
                    _relationship(
                        source=qb1,
                        target=tight_end,
                        relationship_type="throws_to",
                        strength=strength,
                        confidence=0.90,
                        reason=(
                            f"{qb1['player']} is the "
                            f"{team} QB1 and "
                            f"{tight_end['player']} is TE"
                            f"{rank} on the current "
                            "depth chart."
                        ),
                        timestamp=timestamp,
                    )
                )

            for running_back in running_backs:
                rank = running_back[
                    "depth_rank"
                ]

                strength = {
                    1: 0.85,
                    2: 0.55,
                    3: 0.35,
                }.get(rank, 0.30)

                relationships.append(
                    _relationship(
                        source=qb1,
                        target=running_back,
                        relationship_type=(
                            "hands_off_to"
                        ),
                        strength=strength,
                        confidence=0.90,
                        reason=(
                            f"{qb1['player']} shares "
                            f"the {team} backfield with "
                            f"{running_back['player']} "
                            f"(RB{rank})."
                        ),
                        timestamp=timestamp,
                    )
                )

        # --------------------------------------------------------------
        # Primary receiving-option competition
        # --------------------------------------------------------------

        receiving_options = (
            receivers
            + tight_ends[:1]
        )

        for index, source in enumerate(
            receiving_options
        ):
            for target in receiving_options[
                index + 1:
            ]:
                source_rank = source[
                    "depth_rank"
                ]
                target_rank = target[
                    "depth_rank"
                ]

                rank_distance = abs(
                    source_rank - target_rank
                )

                strength = max(
                    0.35,
                    0.65
                    - (rank_distance * 0.08),
                )

                for left, right in (
                    (source, target),
                    (target, source),
                ):
                    relationships.append(
                        _relationship(
                            source=left,
                            target=right,
                            relationship_type=(
                                "target_competitor"
                            ),
                            strength=strength,
                            confidence=0.85,
                            reason=(
                                f"{left['player']} and "
                                f"{right['player']} compete "
                                f"for {team} receiving "
                                "opportunities."
                            ),
                            timestamp=timestamp,
                        )
                    )

        # --------------------------------------------------------------
        # RB competition
        # --------------------------------------------------------------

        if len(running_backs) >= 2:
            rb1 = running_backs[0]

            for backup in running_backs[1:]:
                relationships.append(
                    _relationship(
                        source=rb1,
                        target=backup,
                        relationship_type=(
                            "depth_chart_competitor"
                        ),
                        strength=0.60,
                        confidence=0.85,
                        reason=(
                            f"{rb1['player']} and "
                            f"{backup['player']} compete "
                            f"for {team} backfield usage."
                        ),
                        timestamp=timestamp,
                    )
                )

                relationships.append(
                    _relationship(
                        source=backup,
                        target=rb1,
                        relationship_type=(
                            "depth_chart_competitor"
                        ),
                        strength=0.60,
                        confidence=0.85,
                        reason=(
                            f"{backup['player']} and "
                            f"{rb1['player']} compete "
                            f"for {team} backfield usage."
                        ),
                        timestamp=timestamp,
                    )
                )

    return relationships


def populate_cortex_relationships(
    cortex,
    catalog: list[dict],
    depth_chart: list[dict] | None = None,
) -> int:
    """
    Build and persist current NFL relationships through Cortex.
    """

    relationships = build_nfl_relationships(
        catalog=catalog,
        depth_chart=depth_chart,
    )

    for relationship in relationships:
        cortex.knowledge.save_relationship(
            relationship
        )

    return len(relationships)
