"""
Relationships loader with validation and caching.
"""

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# Constants
REQUIRED_FIELDS: Set[str] = {"target", "relationship_type", "multiplier"}
OPTIONAL_FIELDS: Set[str] = {"note", "team"}
VALID_RELATIONSHIP_TYPES: Set[str] = {
    "qb_to_wr1", "qb_to_wr2", "qb_to_te1", "qb_to_rb",
    "wr1_to_qb", "wr2_to_qb", "te1_to_qb", "rb_to_qb",
    "coach_to_qb", "coach_to_wr", "coach_to_rb", "coach_to_te",
    "ol_to_qb", "qb_to_ol",
}

DEFAULT_RELATIONSHIPS_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "relationships.json"
)


def get_relationships_path() -> Path:
    """Get relationships file path from environment or default."""
    env_path = os.getenv("GRIDIRON_RELATIONSHIPS_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_RELATIONSHIPS_PATH


def validate_relationships(data: Any) -> None:
    """
    Validate relationships JSON structure.
    
    Expected format:
    {
        "Player Name": [
            {
                "target": "Target Player",
                "relationship_type": "qb_to_wr1",
                "multiplier": 0.35,
                "note": "Optional description",
                "team": "Optional team code"
            }
        ]
    }
    
    Args:
        data: Parsed JSON data
        
    Raises:
        ValueError: If validation fails
    """
    if not isinstance(data, dict):
        raise ValueError(
            f"Relationships data must be a dict, got {type(data).__name__}: {data!r}"
        )
    
    if not data:
        raise ValueError("Relationships data is empty")
    
    seen_targets: Dict[str, Set[str]] = {}  # source -> set of targets
    
    for source_idx, (source_player, relationships) in enumerate(data.items()):
        if not isinstance(source_player, str) or not source_player.strip():
            raise ValueError(
                f"Invalid source player key at index {source_idx}: {source_player!r}"
            )
        
        if not isinstance(relationships, list):
            raise ValueError(
                f"{source_player}: relationships must be a list, "
                f"got {type(relationships).__name__}"
            )
        
        if not relationships:
            logger.warning(f"{source_player}: has no relationships defined")
            continue
        
        seen_targets[source_player] = set()
        
        for rel_idx, relationship in enumerate(relationships):
            if not isinstance(relationship, dict):
                raise ValueError(
                    f"{source_player}[{rel_idx}]: must be a dict, "
                    f"got {type(relationship).__name__}"
                )
            
            # Check required fields
            missing = REQUIRED_FIELDS - relationship.keys()
            if missing:
                raise ValueError(
                    f"{source_player}[{rel_idx}]: missing required fields {missing}"
                )
            
            # Check for unknown fields (helps catch typos)
            unknown = set(relationship.keys()) - REQUIRED_FIELDS - OPTIONAL_FIELDS
            if unknown:
                logger.warning(
                    f"{source_player}[{rel_idx}]: unknown fields {unknown} "
                    f"(possible typos?)"
                )
            
            target = relationship["target"]
            if not isinstance(target, str) or not target.strip():
                raise ValueError(
                    f"{source_player}[{rel_idx}]: target must be non-empty string"
                )
            
            # Duplicate target check
            if target in seen_targets[source_player]:
                raise ValueError(
                    f"{source_player}: duplicate relationship to {target}"
                )
            seen_targets[source_player].add(target)
            
            # Validate relationship_type
            rel_type = relationship["relationship_type"]
            if rel_type not in VALID_RELATIONSHIP_TYPES:
                raise ValueError(
                    f"{source_player} -> {target}: "
                    f"invalid relationship_type '{rel_type}'. "
                    f"Valid types: {VALID_RELATIONSHIP_TYPES}"
                )
            
            # Validate multiplier
            multiplier = relationship["multiplier"]
            if not isinstance(multiplier, (int, float)):
                raise ValueError(
                    f"{source_player} -> {target}: "
                    f"multiplier must be numeric, got {type(multiplier).__name__}"
                )
            if not 0.0 <= multiplier <= 1.0:
                raise ValueError(
                    f"{source_player} -> {target}: "
                    f"multiplier must be in [0.0, 1.0], got {multiplier}"
                )
            if multiplier == 0.0:
                logger.warning(
                    f"{source_player} -> {target}: multiplier is 0.0 (no effect)"
                )
            
            # Validate optional fields
            if "note" in relationship and not isinstance(relationship["note"], str):
                raise ValueError(
                    f"{source_player} -> {target}: note must be string"
                )
            if "team" in relationship and not isinstance(relationship["team"], str):
                raise ValueError(
                    f"{source_player} -> {target}: team must be string"
                )


@lru_cache(maxsize=1)
def load_relationships(path: Optional[Path] = None) -> Dict[str, List[Dict]]:
    """
    Load and validate relationships from JSON file.
    
    Cached to avoid repeated disk reads. Call clear_relationships_cache()
    after file modifications.
    
    Args:
        path: Optional custom path to relationships.json
        
    Returns:
        Dict mapping source player names to lists of relationship dicts
        
    Raises:
        FileNotFoundError: If relationships file doesn't exist
        ValueError: If JSON is invalid or fails validation
    """
    data_file = path or get_relationships_path()
    
    logger.info(f"Loading relationships from {data_file}")
    
    if not data_file.exists():
        raise FileNotFoundError(
            f"Relationships file not found: {data_file}\n"
            f"Default location: {DEFAULT_RELATIONSHIPS_PATH}\n"
            f"Set GRIDIRON_RELATIONSHIPS_PATH environment variable to override."
        )
    
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {data_file}: {e}")
    except UnicodeDecodeError as e:
        raise ValueError(f"File encoding error in {data_file}: {e}")
    
    validate_relationships(data)
    
    logger.info(f"Loaded {len(data)} source players with relationships")
    return data


def clear_relationships_cache() -> None:
    """Clear the relationships cache. Call after modifying relationships.json."""
    load_relationships.cache_clear()
    logger.info("Relationships cache cleared")


def reload_relationships(path: Optional[Path] = None) -> Dict[str, List[Dict]]:
    """Force reload relationships (clears cache first)."""
    clear_relationships_cache()
    return load_relationships(path)


# Export control
__all__ = [
    "load_relationships",
    "clear_relationships_cache",
    "reload_relationships",
    "validate_relationships",
    "get_relationships_path",
    "VALID_RELATIONSHIP_TYPES",
]
