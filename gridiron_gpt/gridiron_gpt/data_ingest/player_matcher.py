import logging
import re
from functools import lru_cache
from typing import Optional, TypedDict

from gridiron_gpt.data_ingest.player_catalog import load_player_catalog

logger = logging.getLogger(__name__)

MANUAL_ALIASES: dict[str, list[str]] = {
    "Christian Watson": ["WR Watson", "C. Watson"],
    "Jonathon Cooper": ["LB Cooper", "J. Cooper"],
}


class PlayerMatch(TypedDict):
    player: str
    team: str
    position: str
    confidence: float
    matched_alias: str


@lru_cache(maxsize=1)
def get_cached_catalog() -> list[dict]:
    """Load and cache the player catalog once per process."""
    return load_player_catalog()


def clear_catalog_cache() -> None:
    """Clear the cached catalog, primarily for tests or catalog refreshes."""
    get_cached_catalog.cache_clear()


def normalize_text(value: str) -> str:
    """
    Normalize text for player-name comparison.

    Examples:
        "D.K. Metcalf" -> "dk metcalf"
        "Ja'Marr Chase" -> "jamarr chase"
        "  Tank   Dell " -> "tank dell"
    """
    normalized = value.casefold()
    normalized = re.sub(r"[.'’`-]", "", normalized)
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def calculate_confidence(alias: str) -> float:
    """Calculate a base confidence score from alias specificity."""
    normalized_alias = normalize_text(alias)
    parts = normalized_alias.split()

    if not normalized_alias:
        return 0.0

    if len(parts) >= 2:
        first_part = parts[0]

        # Initial plus last name, such as "C Watson".
        if len(first_part) == 1:
            return 0.90

        # Position plus last name, such as "WR Watson".
        if first_part.upper() in {
            "QB",
            "RB",
            "WR",
            "TE",
            "K",
            "DST",
            "DL",
            "DE",
            "DT",
            "LB",
            "CB",
            "S",
        }:
            return 0.88

        # Full player name.
        return 1.0

    # Last-name-only aliases are inherently more ambiguous.
    return 0.72


def build_default_aliases(player: dict) -> set[str]:
    """Build common aliases for a catalog player."""
    player_name = get_player_name(player)

    if not player_name:
        return set()

    name_parts = player_name.split()
    aliases = {player_name}

    if len(name_parts) >= 2:
        first_name = name_parts[0]
        last_name = name_parts[-1]
        position = get_player_position(player)

        aliases.add(last_name)
        aliases.add(f"{first_name[0]}. {last_name}")
        aliases.add(f"{first_name[0]} {last_name}")

        if position:
            aliases.add(f"{position} {last_name}")

    aliases.update(MANUAL_ALIASES.get(player_name, []))

    return {alias.strip() for alias in aliases if alias.strip()}


def get_player_name(player: dict) -> str:
    """Return the player's display name across supported catalog schemas."""
    return str(
        player.get("player")
        or player.get("name")
        or player.get("full_name")
        or player.get("player_name")
        or ""
    ).strip()


def get_player_team(player: dict) -> str:
    """Return the player's team abbreviation."""
    return str(
        player.get("team")
        or player.get("team_abbr")
        or player.get("team_abbreviation")
        or ""
    ).strip().upper()


def get_player_position(player: dict) -> str:
    """Return the player's position abbreviation."""
    return str(
        player.get("position")
        or player.get("pos")
        or ""
    ).strip().upper()


def text_contains_alias(text: str, alias: str) -> bool:
    """Return True when a normalized alias appears as a complete phrase."""
    normalized_text = normalize_text(text)
    normalized_alias = normalize_text(alias)

    if not normalized_text or not normalized_alias:
        return False

    pattern = rf"(?<![a-z0-9]){re.escape(normalized_alias)}(?![a-z0-9])"
    return re.search(pattern, normalized_text) is not None


def score_match(
    *,
    alias: str,
    player_name: str,
    team: str,
    position: str,
    team_hint: Optional[str],
    position_hint: Optional[str],
) -> float:
    """Score a candidate match using alias specificity and optional hints."""
    confidence = calculate_confidence(alias)

    if normalize_text(alias) == normalize_text(player_name):
        confidence = 1.0

    if team_hint:
        normalized_team_hint = team_hint.strip().upper()

        if team == normalized_team_hint:
            confidence += 0.05
        elif team:
            confidence -= 0.12

    if position_hint:
        normalized_position_hint = position_hint.strip().upper()

        if position == normalized_position_hint:
            confidence += 0.04
        elif position:
            confidence -= 0.08

    return round(max(0.0, min(confidence, 1.0)), 3)


def find_player_matches(
    text: str,
    *,
    team_hint: Optional[str] = None,
    position_hint: Optional[str] = None,
    minimum_confidence: float = 0.70,
) -> list[PlayerMatch]:
    """
    Find all player references contained in a piece of text.

    Args:
        text:
            Headline, article text, injury report, or other source text.
        team_hint:
            Optional team abbreviation used to improve disambiguation.
        position_hint:
            Optional position abbreviation used to improve disambiguation.
        minimum_confidence:
            Lowest confidence score included in the result.

    Returns:
        Matches ordered from highest to lowest confidence.
    """
    if not text or not text.strip():
        return []

    catalog = get_cached_catalog()
    best_matches: dict[str, PlayerMatch] = {}

    for player in catalog:
        player_name = get_player_name(player)

        if not player_name:
            continue

        team = get_player_team(player)
        position = get_player_position(player)

        for alias in build_default_aliases(player):
            if not text_contains_alias(text, alias):
                continue

            confidence = score_match(
                alias=alias,
                player_name=player_name,
                team=team,
                position=position,
                team_hint=team_hint,
                position_hint=position_hint,
            )

            if confidence < minimum_confidence:
                continue

            candidate: PlayerMatch = {
                "player": player_name,
                "team": team,
                "position": position,
                "confidence": confidence,
                "matched_alias": alias,
            }

            current = best_matches.get(player_name)

            if current is None or candidate["confidence"] > current["confidence"]:
                best_matches[player_name] = candidate

    matches = list(best_matches.values())
    matches.sort(
        key=lambda match: (
            match["confidence"],
            len(normalize_text(match["matched_alias"])),
        ),
        reverse=True,
    )

    return matches


def resolve_player(
    text: str,
    *,
    team_hint: Optional[str] = None,
    position_hint: Optional[str] = None,
    minimum_confidence: float = 0.70,
    ambiguity_threshold: float = 0.03,
) -> Optional[PlayerMatch]:
    """
    Resolve the strongest player match from text.

    Returns None when:
        - no candidate exceeds the minimum confidence;
        - the top candidates are too close and cannot be disambiguated.
    """
    matches = find_player_matches(
        text,
        team_hint=team_hint,
        position_hint=position_hint,
        minimum_confidence=minimum_confidence,
    )

    if not matches:
        return None

    top_match = matches[0]

    if len(matches) == 1:
        return top_match

    second_match = matches[1]
    confidence_gap = top_match["confidence"] - second_match["confidence"]

    if confidence_gap < ambiguity_threshold:
        logger.warning(
            "Ambiguous player match for text=%r: %s and %s",
            text,
            top_match["player"],
            second_match["player"],
        )
        return None

    return top_match


def match_player(
    text: str,
    team_hint: Optional[str] = None,
    position_hint: Optional[str] = None,
) -> Optional[PlayerMatch]:
    """
    Backward-compatible entry point for resolving one player.

    New code may call resolve_player() directly.
    """
    return resolve_player(
        text,
        team_hint=team_hint,
        position_hint=position_hint,
    )

def extract_players_from_text(
    text: str,
    team_hint: str | None = None,
    position_hint: str | None = None,
) -> list[PlayerMatch]:
    """Backward-compatible wrapper for existing RSS ingestion code."""
    return find_player_matches(
        text,
        team_hint=team_hint,
        position_hint=position_hint,
    )
