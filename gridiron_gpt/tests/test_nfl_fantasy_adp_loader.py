import pandas as pd

from gridiron_gpt.draft.nfl_fantasy_adp_loader import NflFantasyAdpLoader


def test_parses_public_draft_breakdown_table():
    frame = pd.DataFrame(
        {
            "Player": [
                "Ja'Marr Chase WR - CIN",
                "Bijan Robinson RB - ATL",
                "Josh Allen QB - BUF",
            ],
            "Avg. Pick (ADP)": [1.42, 3.32, 22.18],
        }
    )
    loader = NflFantasyAdpLoader(table_loader=lambda _: [frame])

    snapshot = loader.load()

    assert snapshot.source == "NFL Fantasy"
    assert snapshot.records["Ja'Marr Chase"] == 1.42
    assert snapshot.records["Bijan Robinson"] == 3.32
    assert snapshot.records["Josh Allen"] == 22.18


def test_ignores_zero_and_invalid_adp_rows():
    frame = pd.DataFrame(
        {
            "Player": ["Useful Player WR - TST", "Bench Player RB - TST"],
            "Avg. Pick (ADP)": [25.0, 0.0],
        }
    )
    loader = NflFantasyAdpLoader(table_loader=lambda _: [frame])

    assert loader.load().records == {"Useful Player": 25.0}


def test_supports_multiindex_table_headers():
    columns = pd.MultiIndex.from_tuples(
        [
            ("Standard Draft", "Player"),
            ("Standard Draft", "Avg. Pick (ADP)"),
        ]
    )
    frame = pd.DataFrame(
        [["Puka Nacua WR - LAR", 9.55]],
        columns=columns,
    )
    loader = NflFantasyAdpLoader(table_loader=lambda _: [frame])

    assert loader.load().records["Puka Nacua"] == 9.55


def test_returns_empty_snapshot_when_no_matching_table_exists():
    frame = pd.DataFrame({"Name": ["Player"], "Value": [1]})
    loader = NflFantasyAdpLoader(table_loader=lambda _: [frame])

    assert loader.load().records == {}
