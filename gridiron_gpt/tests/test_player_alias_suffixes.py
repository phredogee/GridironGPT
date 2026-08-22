import gridiron_gpt.data_ingest.player_matcher as player_matcher
from gridiron_gpt.data_ingest.player_matcher import build_default_aliases, find_player_matches


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


def test_suffixless_names_resolve_from_catalog(monkeypatch):
    catalog = [
        {
            "player": "Chris Rodriguez Jr.",
            "football_name": "Chris",
            "first_name": "Chris",
            "last_name": "Rodriguez",
            "team": "WAS",
            "position": "RB",
            "aliases": [],
        },
        {
            "player": "Deebo Samuel Sr.",
            "football_name": "Deebo",
            "first_name": "Tyshun",
            "last_name": "Samuel",
            "team": "WAS",
            "position": "WR",
            "aliases": [],
        },
    ]

    monkeypatch.setattr(player_matcher, "load_player_catalog", lambda: catalog)
    player_matcher.clear_catalog_cache()

    chris_matches = find_player_matches(
        "Chris Rodriguez: Progressing in recovery"
    )
    deebo_matches = find_player_matches(
        "Buzz: What is Deebo Samuel's potential in 49ers return?"
    )

    assert any(
        match["player"] == "Chris Rodriguez Jr."
        for match in chris_matches
    )
    assert any(
        match["player"] == "Deebo Samuel Sr."
        for match in deebo_matches
    )

    player_matcher.clear_catalog_cache()
