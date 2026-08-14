from gridiron_gpt.draft.fantasy_ranking_explanation_service import (
    FantasyRankingExplanationService,
)
from gridiron_gpt.draft.fantasy_ranking_score import FantasyRankingScore


def ranking_score(**overrides):
    values = {
        "player_id": "p1",
        "player_name": "Example Player",
        "team": "TST",
        "position": "WR",
        "ranking_score": 82.5,
        "components": {
            "baseline": 75.0,
            "market": 95.0,
            "role": 90.0,
            "cortex": 50.0,
            "availability": 100.0,
        },
        "weighted_components": {},
        "provenance": {
            "market": "2026 ADP",
            "role": "2025 recent observed usage percentile",
        },
    }
    values.update(overrides)
    return FantasyRankingScore(**values)


def test_explanation_identifies_strengths_and_concerns():
    explanation = FantasyRankingExplanationService().explain(
        ranking_score(),
        overall_rank=7,
    )

    assert explanation.summary.startswith("#7 Example Player (WR, TST) scores 82.50.")
    assert "elite current market value (95.0)" in explanation.strengths
    assert "elite recent role/usage (90.0)" in explanation.strengths
    assert "below-average Cortex intelligence (50.0)" in explanation.concerns


def test_explanation_preserves_source_provenance():
    explanation = FantasyRankingExplanationService().explain(ranking_score())

    assert "current market value: 95.0 (2026 ADP)" in explanation.evidence
    assert (
        "recent role/usage: 90.0 (2025 recent observed usage percentile)"
        in explanation.evidence
    )


def test_explanation_calls_out_missing_evidence_without_treating_it_as_negative():
    score = ranking_score(
        components={
            "market": 90.0,
            "cortex": 50.0,
            "availability": 100.0,
        },
        provenance={},
    )

    explanation = FantasyRankingExplanationService().explain(score)

    assert "Missing evidence: historical production, recent role/usage." in explanation.summary
    assert all("historical" not in concern for concern in explanation.concerns)
    assert all("role" not in concern for concern in explanation.concerns)


def test_neutral_cortex_is_described_as_tempering_not_missing():
    explanation = FantasyRankingExplanationService().explain(ranking_score())

    assert "below-average Cortex intelligence (50.0)" in explanation.summary
    assert "Missing evidence" not in explanation.summary
