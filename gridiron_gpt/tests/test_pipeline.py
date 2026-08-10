"""Tests for the active ranking pipeline and Advisor integration."""

import pytest

from gridiron_gpt.core.advisor import Advisor
from pipelines.ranking_pipeline import run_pipeline_logic


def test_advisor_instantiation():
    advisor = Advisor()

    assert advisor is not None
    assert callable(advisor.add_documents)


def test_pipeline_returns_structured_data():
    result = run_pipeline_logic(
        season=2024,
        dry_run=True,
    )

    assert result["season"] == 2024
    assert isinstance(result["rankings"], list)
    assert result["count"] == len(result["rankings"])


def test_pipeline_dry_run_output(capsys):
    run_pipeline_logic(
        season=2024,
        dry_run=True,
    )

    captured = capsys.readouterr()

    assert "Dry-run mode: using stubbed ESPN data" in captured.out


@pytest.mark.parametrize("season", [2024, 2023])
def test_pipeline_dry_run_behavior(season, capsys):
    result = run_pipeline_logic(
        season=season,
        dry_run=True,
    )

    captured = capsys.readouterr()

    assert result["season"] == season
    assert isinstance(result["rankings"], list)
    assert result["count"] == len(result["rankings"])
    assert "Dry-run mode: using stubbed ESPN data" in captured.out


def test_pipeline_live_execution_contract():
    try:
        result = run_pipeline_logic(
            season=2024,
            dry_run=False,
        )
    except NotImplementedError as exc:
        assert "Live ESPN fetch" in str(exc)
    else:
        assert isinstance(result, dict)
        assert result["season"] == 2024


def test_advisor_add_documents_signature():
    advisor = Advisor()

    assert callable(advisor.add_documents)
    assert "texts" in advisor.add_documents.__code__.co_varnames
