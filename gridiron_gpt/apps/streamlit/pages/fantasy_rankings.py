from __future__ import annotations

import streamlit as st

from gridiron_cortex.remember.json_player_scorecard_repository import (
    JsonPlayerScorecardRepository,
)
from gridiron_gpt.draft.fantasy_ranking_data_service import FantasyRankingDataService
from gridiron_gpt.draft.fantasy_ranking_population_service import (
    FantasyRankingPopulationService,
)
from gridiron_gpt.football_state.repositories.jsonl_player_state_repository import (
    JsonlPlayerStateRepository,
)


def build_fantasy_ranking_snapshot(
    *,
    scoring: str = "ppr",
    teams: int = 12,
    limit: int = 50,
):
    """Build the production fantasy-ranking snapshot used by the UI."""
    player_repository = JsonlPlayerStateRepository()
    scorecard_repository = JsonPlayerScorecardRepository(
        "data/cortex/player_scorecards.jsonl"
    )
    service = FantasyRankingDataService(
        FantasyRankingPopulationService(
            player_repository,
            scorecard_repository,
        )
    )
    return service.build(
        scoring=scoring,
        teams=teams,
        limit=limit,
    )


def render_fantasy_rankings() -> None:
    st.markdown("### Integrated Fantasy Rankings")
    st.caption(
        "Rankings combine historical production, current market/ADP, recent role, "
        "Cortex intelligence, and canonical availability."
    )

    controls = st.columns([2, 2, 2, 5])
    with controls[0]:
        scoring = st.selectbox(
            "Scoring",
            ("ppr", "half_ppr", "standard"),
            index=0,
            key="fantasy_rankings_scoring",
        )
    with controls[1]:
        teams = st.selectbox(
            "League size",
            (8, 10, 12, 14, 16),
            index=2,
            key="fantasy_rankings_teams",
        )
    with controls[2]:
        limit = st.selectbox(
            "Show",
            (25, 50, 100, 200),
            index=1,
            key="fantasy_rankings_limit",
        )

    try:
        snapshot = build_fantasy_ranking_snapshot(
            scoring=scoring,
            teams=teams,
            limit=limit,
        )
    except Exception as exc:
        st.error("Fantasy rankings could not be built from the current local data.")
        with st.expander("Technical details", expanded=False):
            st.code(str(exc))
        return

    meta = st.columns(4)
    meta[0].metric("Historical", snapshot.historical_player_count)
    meta[1].metric(
        "Market / ADP",
        snapshot.adp_player_count,
        delta=(f"{snapshot.adp_year}" if snapshot.adp_year else "Unavailable"),
    )
    meta[2].metric(
        "Role evidence",
        snapshot.role_player_count,
        delta=(f"{snapshot.role_season}" if snapshot.role_season else "Unavailable"),
    )
    meta[3].metric("Ranked players", len(snapshot.population.overall))

    if not snapshot.population.explained_overall:
        st.info("No players currently have sufficient anchor evidence to rank.")
        return

    st.divider()

    for item in snapshot.population.explained_overall:
        score = item.score
        explanation = item.explanation
        header = (
            f"#{item.rank}  {score.player_name}  ·  {score.position or '-'}  ·  "
            f"{score.team or '-'}  ·  {score.ranking_score:.2f}"
        )
        with st.expander(header, expanded=item.rank <= 5):
            st.write(explanation.summary)

            component_columns = st.columns(len(score.components))
            for column, (name, value) in zip(component_columns, score.components.items()):
                column.metric(name.title(), f"{value:.1f}")

            if explanation.strengths:
                st.markdown("**Strengths**")
                for strength in explanation.strengths:
                    st.write(f"• {strength}")

            if explanation.concerns:
                st.markdown("**Concerns**")
                for concern in explanation.concerns:
                    st.write(f"• {concern}")

            with st.expander("Evidence & provenance", expanded=False):
                for evidence in explanation.evidence:
                    st.write(f"• {evidence}")
