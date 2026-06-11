import logging
import re
from functools import lru_cache
from typing import Optional, TypedDict

from gridiron_gpt.data_ingest.player_catalog import load_player_catalog

logger = logging.getLogger(__name__)

MANUAL_ALIASES = {
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


def calculate_confidence(alias: str) -> float:
    """Calculate confidence based on alias specificity."""
    alias = alias.strip()

    if not alias:
        return 0.0

    score = min(1.0, len(alias) / 15)

    if " " in alias:
        score += 0.2

    if len(alias) <= 3:
        score -= 0.3

    return max(0.0, min(1.0, score))


def extract_players_from_text(text: Optional[str]) -> list[PlayerMatch]:
    """
    Extract all player mentions from text.

    Returns matches with player, team, position, confidence, and matched alias.
    """
    if not text or not isinstance(text, str):
        logger.warning("Invalid input to extract_players_from_text: %r", text)
        return []

    lowered = text.lower()
    catalog = get_cached_catalog()
    matches: list[PlayerMatch] = []
    seen_players = set()

    for item in catalog:
        player = item.get("player")

        if not player or player in seen_players:
            continue

        team = item.get("team", "UNK")
        position = item.get("position", "Unknown")

        aliases = [player]
        aliases.extend(item.get("aliases", []))
        aliases.extend(MANUAL_ALIASES.get(player, []))

        unique_aliases = []
        seen_aliases = set()

        for alias in aliases:
            if not alias or not isinstance(alias, str):
                continue

            alias_lower = alias.lower().strip()

            if alias_lower not in seen_aliases:
                seen_aliases.add(alias_lower)
                unique_aliases.append(alias_lower)

        best_match = None
        best_confidence = 0.0

        for alias in unique_aliases:
            pattern = r"\b" + re.escape(alias) + r"\b"

            if re.search(pattern, lowered):
                confidence = calculate_confidence(alias)

                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = alias

        if best_match and best_confidence >= 0.5:
            matches.append(
                {
                    "player": player,
                    "team": team,
                    "position": position,
                    "confidence": best_confidence,
                    "matched_alias": best_match,
                }
            )
            seen_players.add(player)

    matches.sort(key=lambda match: match["confidence"], reverse=True)

    if not matches:
        logger.debug("No player matches found in text: %s", text[:100])

    return matches


def extract_player_and_team(text: str) -> tuple[str, str]:
    """
    Legacy single-player extraction.

    Prefer extract_players_from_text() for new code.
    """
    matches = extract_players_from_text(text)

    if matches:
        return matches[0]["player"], matches[0]["team"]

    return "Unknown", "UNK"
