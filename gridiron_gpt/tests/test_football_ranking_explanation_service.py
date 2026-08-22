from gridiron_gpt.draft.football_ranking_explanation_service import (
    FootballRankingExplanationService,
)


def test_football_explanation_uses_real_signal_headline():
    explanation = FootballRankingExplanationService().explain(
        recent_signals=[
            {
                "headline": "Alpha RB missed practice with an ankle injury",
                "value": -1.0,
            }
        ],
        fallback="Strong market profile",
    )

    assert explanation.takeaway == "Missed practice"
    assert "missed practice" in explanation.summary


def test_football_explanation_can_translate_role_context():
    explanation = FootballRankingExplanationService().explain(
        recent_signals=[
            {
                "headline": "Alpha RB sees increased reps with first-team offense",
                "value": 1.0,
            }
        ],
        fallback="Strong role profile",
    )

    assert explanation.takeaway == "First-team reps"


def test_football_explanation_falls_back_without_signal_evidence():
    explanation = FootballRankingExplanationService().explain(
        recent_signals=[],
        fallback="Elite market + role",
    )

    assert explanation.takeaway == "Elite market + role"
    assert explanation.headlines == ()
