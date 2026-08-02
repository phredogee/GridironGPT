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

NAME_SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}


class PlayerMatch(TypedDict):
    player: str
    team: str
    position: str
    confidence: float
    matched_alias: str


@lru_cache(maxsize=1)
def get_cached_catalog() -> list[dict]:
    return load_player_catalog()


@lru_cache(maxsize=1)
def get_alias_index() -> dict[str, list[dict]]:
    alias_index: dict[str, list[dict]] = {}

    for player in get_cached_catalog():
        for alias in build_default_aliases(player):
            normalized = normalize_text(alias)

            alias_index.setdefault(normalized, []).append(
                {
                    "player": player,
                    "alias": alias,
                }
            )

    return alias_index


def clear_catalog_cache() -> None:
    """Clear cached catalog and alias index."""
    get_cached_catalog.cache_clear()
    get_alias_index.cache_clear()


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

        if len(first_part) == 1:
            return 0.90

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

        return 1.0

    return 0.72


def strip_name_suffix(player_name: str) -> str:
    """Return a display name without a trailing generational suffix."""
    parts = player_name.strip().split()

    if not parts:
        return ""

    normalized_suffix = normalize_text(parts[-1])
    if normalized_suffix in NAME_SUFFIXES:
        parts = parts[:-1]

    return " ".join(parts)


def build_default_aliases(player: dict) -> set[str]:
    """
    Return stored catalog aliases plus safe generated fallbacks.

    In addition to the official full name, include football-name and
    suffixless variants. News providers commonly omit Jr./Sr./roman-numeral
    suffixes, so "Chris Rodriguez" must still resolve to
    "Chris Rodriguez Jr." without requiring a manual alias.
    """
    player_name = get_player_name(player)

    if not player_name:
        return set()

    aliases = {
        str(alias).strip()
        for alias in player.get("aliases", [])
        if alias and str(alias).strip()
    }

    aliases.add(player_name)

    football_name = str(player.get("football_name") or "").strip()
    first_name = str(player.get("first_name") or "").strip()
    last_name = str(player.get("last_name") or "").strip()

    suffixless_name = strip_name_suffix(player_name)
    if suffixless_name and suffixless_name != player_name:
        aliases.add(suffixless_name)

    if football_name and last_name:
        aliases.add(f"{football_name} {last_name}")

    base_name = suffixless_name or player_name
    name_parts = base_name.split()

    if len(name_parts) >= 2:
        generated_first = first_name or name_parts[0]
        generated_last = last_name or name_parts[-1]
        position = get_player_position(player)
        team = get_player_team(player)

        aliases.add(f"{generated_first[0]}. {generated_last}")
        aliases.add(f"{generated_first[0]} {generated_last}")

        if position:
            aliases.add(f"{position} {generated_last}")
            aliases.add(f"{position} {base_name}")

        if team:
            aliases.add(f"{team} {base_name}")

            if position:
                aliases.add(f"{team} {position} {generated_last}")
                aliases.add(f"{team} {position} {base_name}")

    aliases.update(MANUAL_ALIASES.get(player_name, []))

    return {
        alias.strip()
        for alias in aliases
        if alias and alias.strip()
    }


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


def find_alias_span(
    normalized_text: str,
    normalized_alias: str,
) -> tuple[int, int] | None:
    """Return the first complete-phrase span for an alias."""
    if not normalized_text or not normalized_alias:
        return None

    pattern = rf"(?<![a-z0-9]){re.escape(normalized_alias)}(?![a-z0-9])"
    match = re.search(pattern, normalized_text)

    if match is None:
        return None

    return match.span()


def find_player_matches(
    text: str,
    *,
    team_hint: Optional[str] = None,
    position_hint: Optional[str] = None,
    minimum_confidence: float = 0.85,
) -> list[PlayerMatch]:
    """Find all high-confidence player references contained in text."""
    if not text or not text.strip():
        return []

    normalized_text = normalize_text(text)
    best_matches: dict[str, PlayerMatch] = {}
    accepted_spans: list[tuple[int, int]] = []

    alias_items = sorted(
        get_alias_index().items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for normalized_alias, alias_entries in alias_items:
        if not normalized_alias:
            continue

        span = find_alias_span(normalized_text, normalized_alias)

        if span is None:
            continue

        span_start, span_end = span

        is_contained_by_stronger_match = any(
            accepted_start <= span_start
            and span_end <= accepted_end
            and (accepted_start, accepted_end) != span
            for accepted_start, accepted_end in accepted_spans
        )

        if is_contained_by_stronger_match:
            continue

        alias_accepted = False

        for entry in alias_entries:
            player = entry["player"]
            alias = entry["alias"]

            player_name = get_player_name(player)

            if not player_name:
                continue

            team = get_player_team(player)
            position = get_player_position(player)

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
                alias_accepted = True

        if alias_accepted:
            accepted_spans.append(span)

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
    minimum_confidence: float = 0.85,
    ambiguity_threshold: float = 0.03,
) -> Optional[PlayerMatch]:
    """Resolve the strongest player match from text."""
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
    """Backward-compatible entry point for resolving one player."""
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
    """Extract high-confidence player references from article text."""
    return find_player_matches(
        text,
        team_hint=team_hint,
        position_hint=position_hint,
        minimum_confidence=0.85,
    )
