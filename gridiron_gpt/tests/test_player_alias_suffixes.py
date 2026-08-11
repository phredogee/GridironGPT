from gridiron_gpt.data_ingest.player_matcher import (
    build_default_aliases,
    find_player_matches,
    get_alias_index,
    get_cached_catalog,
)


def test_suffixless_alias_is_generated():
    player = {
        "player": "Chris Rodriguez Jr.",
        "football_name": "Chris",
        "first_name": "Chris",
        "last_name": "Rodriguez",
        "team": "WAS",
        "position": "RB",
        "aliases": [],
    }

    aliases = build_default_aliases(player)

    assert "Chris Rodriguez" in aliases
    assert "RB Rodriguez" in aliases


def test_football_name_alias_is_generated():
    player = {
        "player": "Deebo Samuel Sr.",
        "football_name": "Deebo",
        "first_name": "Tyshun",
        "last_name": "Samuel",
        "team": "WAS",
        "position": "WR",
        "aliases": [],
    }

    aliases = build_default_aliases(player)

    assert "Deebo Samuel" in aliases


def test_live_catalog_suffixless_names_resolve():
    # Force the current catalog through alias-index construction.
    # The upstream roster may change whether suffixes are included in the
    # canonical display name, so this test verifies identity resolution rather
    # than pinning the exact display formatting of the live dataset.
    get_cached_catalog.cache_clear()
    get_alias_index.cache_clear()

    chris_matches = find_player_matches(
        "Chris Rodriguez: Progressing in recovery"
    )
    deebo_matches = find_player_matches(
        "Buzz: What is Deebo Samuel's potential in 49ers return?"
    )

    assert any(
        match["player"].startswith("Chris Rodriguez")
        for match in chris_matches
    )
    assert any(
        match["player"].startswith("Deebo Samuel")
        for match in deebo_matches
    )
