import pytest

from gridiron_gpt.fantasy_decisions.models import ScoringFormat
from gridiron_gpt.product.league_profiles import JsonLeagueProfileRepository, LeagueProfile


def profile(**overrides):
    values = {
        "league_id": "rrfl",
        "name": "Riff Raff Footbrawl League",
        "teams": 10,
        "roster_size": 15,
        "starting_slots": {"QB": 1, "RB": 2, "WR": 3, "FLEX": 1, "DST": 1},
        "bench_slots": 7,
        "ir_slots": 2,
        "faab_budget": 100,
        "scoring_format": ScoringFormat.STANDARD,
    }
    values.update(overrides)
    return LeagueProfile(**values)


def test_profile_converts_to_decision_context():
    context = profile().to_context()
    assert context.teams == 10
    assert context.roster_size == 15
    assert context.starting_slots["WR"] == 3
    assert context.scoring_format == ScoringFormat.STANDARD


def test_repository_saves_loads_and_lists_profiles(tmp_path):
    repo = JsonLeagueProfileRepository(tmp_path)
    repo.save(profile())
    repo.save(profile(league_id="second", name="Second League", teams=12))
    assert repo.load("rrfl") == profile()
    assert [item.league_id for item in repo.list()] == ["rrfl", "second"]


def test_saving_existing_profile_updates_configuration(tmp_path):
    repo = JsonLeagueProfileRepository(tmp_path)
    repo.save(profile())
    repo.save(profile(teams=14, roster_size=20))
    updated = repo.load("rrfl")
    assert updated.teams == 14
    assert updated.roster_size == 20


def test_delete_profile(tmp_path):
    repo = JsonLeagueProfileRepository(tmp_path)
    repo.save(profile())
    assert repo.delete("rrfl") is True
    assert repo.delete("rrfl") is False


def test_unknown_profile_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        JsonLeagueProfileRepository(tmp_path).load("missing")


def test_roster_limits_and_slots_are_validated():
    with pytest.raises(ValueError, match="roster limits"):
        profile(ir_slots=-1)
    with pytest.raises(ValueError, match="slot counts"):
        profile(starting_slots={"QB": -1})
