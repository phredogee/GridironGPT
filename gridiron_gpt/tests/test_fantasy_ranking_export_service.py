from io import BytesIO
from types import SimpleNamespace

from openpyxl import load_workbook

from gridiron_gpt.draft.fantasy_ranking_export_service import (
    DRAFT_DAY_FIELDS,
    FULL_ANALYSIS_FIELDS,
    build_rankings_xlsx,
)
from gridiron_gpt.draft.fantasy_ranking_score import FantasyRankingScore


def score(player_id="p1", name="Alpha RB", team="BUF", position="RB"):
    return FantasyRankingScore(
        player_id=player_id,
        player_name=name,
        team=team,
        position=position,
        ranking_score=88.5,
        components={
            "baseline": 80.0,
            "market": 90.0,
            "role": 85.0,
            "cortex": 50.0,
            "availability": 100.0,
        },
        weighted_components={},
        provenance={"market": "2026 ADP"},
    )


def population():
    row = score()
    return SimpleNamespace(
        overall=[row],
        by_position={"QB": [], "RB": [row], "WR": [], "TE": []},
    )


def workbook_headers(data: bytes, sheet="Overall"):
    book = load_workbook(BytesIO(data), read_only=True)
    return [cell.value for cell in next(book[sheet].iter_rows())]


def test_draft_day_export_defaults_to_compact_fields():
    data = build_rankings_xlsx(
        population(),
        bye_week_by_team={"BUF": 7},
        football_notes_by_player_id={"p1": "First-team reps"},
    )

    assert workbook_headers(data) == [
        "Rank",
        "Player",
        "Pos",
        "Team",
        "Bye",
        "Score",
        "Football Notes",
    ]


def test_custom_export_can_remove_market_and_role():
    fields = ("rank", "player", "position", "team", "bye", "score")
    data = build_rankings_xlsx(population(), selected_fields=fields)

    headers = workbook_headers(data)
    assert headers == ["Rank", "Player", "Pos", "Team", "Bye", "Score"]
    assert "Market" not in headers
    assert "Role" not in headers


def test_full_analysis_exposes_all_supported_fields():
    data = build_rankings_xlsx(population(), selected_fields=FULL_ANALYSIS_FIELDS)
    assert workbook_headers(data) == [
        "Rank",
        "Player",
        "Pos",
        "Team",
        "Bye",
        "Score",
        "Baseline",
        "Market",
        "Role",
        "Cortex",
        "Availability",
        "Football Notes",
        "Provenance",
    ]


def test_export_writes_bye_and_football_note_values():
    data = build_rankings_xlsx(
        population(),
        selected_fields=DRAFT_DAY_FIELDS,
        bye_week_by_team={"BUF": 7},
        football_notes_by_player_id={"p1": "Goal-line role"},
    )
    book = load_workbook(BytesIO(data), read_only=True)
    values = [cell.value for cell in next(book["Overall"].iter_rows(min_row=2, max_row=2))]

    assert values[4] == 7
    assert values[6] == "Goal-line role"
