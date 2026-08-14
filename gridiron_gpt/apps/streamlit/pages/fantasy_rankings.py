from __future__ import annotations

import streamlit as st

from gridiron_cortex.remember.json_player_scorecard_repository import (
    JsonPlayerScorecardRepository,
)
from gridiron_gpt.data_ingest.player_scores import calculate_player_scores
from gridiron_gpt.draft.bye_week_service import ByeWeekService
from gridiron_gpt.draft.fantasy_ranking_data_service import FantasyRankingDataService
from gridiron_gpt.draft.fantasy_ranking_export_service import (
    DRAFT_DAY_FIELDS,
    FIELD_LABELS,
    FULL_ANALYSIS_FIELDS,
    build_rankings_pdf,
    build_rankings_xlsx,
    compact_takeaway,
)
from gridiron_gpt.draft.fantasy_ranking_population_service import (
    FantasyRankingPopulationService,
)
from gridiron_gpt.draft.football_ranking_explanation_service import (
    FootballRankingExplanationService,
)
from gridiron_gpt.football_state.repositories.jsonl_player_state_repository import (
    JsonlPlayerStateRepository,
)


POSITIONS = ("QB", "RB", "WR", "TE")


def build_fantasy_ranking_snapshot(
    *,
    scoring: str = "ppr",
    teams: int = 12,
    limit: int | None = None,
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


def _football_notes(population) -> tuple[dict[str, str], dict[str, str]]:
    """Build compact and full football-speak context from scored news signals."""
    try:
        scored = calculate_player_scores()
    except Exception:
        scored = {}

    by_name_team = {
        (str(player).casefold(), str(team).upper()): data
        for (player, team), data in scored.items()
    }
    service = FootballRankingExplanationService()
    compact: dict[str, str] = {}
    summaries: dict[str, str] = {}

    for score in population.overall:
        data = by_name_team.get(
            (score.player_name.casefold(), (score.team or "").upper()),
            {},
        )
        recent_signals = data.get("signals", [])[-5:]
        fallback = compact_takeaway(score)
        explanation = service.explain(
            recent_signals=recent_signals,
            fallback=fallback,
        )
        compact[score.player_id] = explanation.takeaway
        summaries[score.player_id] = explanation.summary

    return compact, summaries


def _render_score_rows(
    scores,
    *,
    football_summaries: dict[str, str],
    expanded_count: int = 5,
) -> None:
    for rank, score in enumerate(scores, start=1):
        header = (
            f"#{rank}  {score.player_name}  ·  {score.position or '-'}  ·  "
            f"{score.team or '-'}  ·  {score.ranking_score:.2f}"
        )
        with st.expander(header, expanded=rank <= expanded_count):
            football_summary = football_summaries.get(score.player_id)
            if football_summary:
                st.markdown("**Football read**")
                st.write(football_summary)

            component_columns = st.columns(len(score.components))
            for column, (name, value) in zip(
                component_columns,
                score.components.items(),
            ):
                column.metric(name.title(), f"{value:.1f}")

            if score.provenance:
                with st.expander("Evidence & provenance", expanded=False):
                    for name, source in score.provenance.items():
                        st.write(f"• **{name.title()}** — {source}")


def _render_overall_rows(
    explained_overall,
    *,
    football_summaries: dict[str, str],
    limit: int,
) -> None:
    for item in explained_overall[:limit]:
        score = item.score
        explanation = item.explanation
        header = (
            f"#{item.rank}  {score.player_name}  ·  {score.position or '-'}  ·  "
            f"{score.team or '-'}  ·  {score.ranking_score:.2f}"
        )
        with st.expander(header, expanded=item.rank <= 5):
            football_summary = football_summaries.get(score.player_id)
            if football_summary:
                st.markdown("**Football read**")
                st.write(football_summary)

            st.markdown("**Model explanation**")
            st.write(explanation.summary)

            component_columns = st.columns(len(score.components))
            for column, (name, value) in zip(
                component_columns,
                score.components.items(),
            ):
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


def _selected_export_fields() -> tuple[str, ...]:
    preset = st.radio(
        "Export preset",
        ("Draft Day", "Full Analysis", "Custom"),
        horizontal=True,
        key="fantasy_rankings_export_preset",
    )

    if preset == "Draft Day":
        defaults = list(DRAFT_DAY_FIELDS)
    elif preset == "Full Analysis":
        defaults = list(FULL_ANALYSIS_FIELDS)
    else:
        defaults = list(DRAFT_DAY_FIELDS)

    selected = st.multiselect(
        "Export fields",
        options=list(FIELD_LABELS),
        default=defaults,
        format_func=lambda field: FIELD_LABELS[field],
        key=f"fantasy_rankings_export_fields_{preset}",
    )
    return tuple(selected)


def render_fantasy_rankings() -> None:
    st.markdown("### Integrated Fantasy Rankings")
    st.caption(
        "Rankings combine historical production, current market/ADP, recent role, "
        "Cortex intelligence, and canonical availability."
    )

    controls = st.columns([2, 2, 2, 2, 4])
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
        overall_limit = st.selectbox(
            "Overall",
            (25, 50, 100, 200),
            index=1,
            key="fantasy_rankings_limit",
        )
    with controls[3]:
        position_limit = st.selectbox(
            "Per position",
            (10, 20, 30, 50, 100),
            index=2,
            key="fantasy_rankings_position_limit",
        )

    try:
        snapshot = build_fantasy_ranking_snapshot(
            scoring=scoring,
            teams=teams,
            limit=None,
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
        delta=(
            f"{snapshot.role_season}"
            if snapshot.role_season
            else "Unavailable"
        ),
    )
    meta[3].metric("Ranked players", len(snapshot.population.overall))

    if not snapshot.population.explained_overall:
        st.info("No players currently have sufficient anchor evidence to rank.")
        return

    football_notes, football_summaries = _football_notes(snapshot.population)
    bye_weeks = ByeWeekService().load(season=2026)

    st.divider()
    st.markdown("### Export")
    selected_fields = _selected_export_fields()

    if not selected_fields:
        st.warning("Select at least one export field.")
    else:
        export_columns = st.columns([1, 1, 4])
        try:
            xlsx_data = build_rankings_xlsx(
                snapshot.population,
                overall_limit=overall_limit,
                position_limit=position_limit,
                selected_fields=selected_fields,
                bye_week_by_team=bye_weeks,
                football_notes_by_player_id=football_notes,
            )
            export_columns[0].download_button(
                "Download Excel",
                data=xlsx_data,
                file_name=f"gridirongpt_rankings_{scoring}_{teams}team.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        except Exception as exc:
            export_columns[0].warning(f"Excel export unavailable: {exc}")

        try:
            pdf_data = build_rankings_pdf(
                snapshot.population,
                overall_limit=overall_limit,
                position_limit=position_limit,
                selected_fields=selected_fields,
                bye_week_by_team=bye_weeks,
                football_notes_by_player_id=football_notes,
            )
            export_columns[1].download_button(
                "Download PDF",
                data=pdf_data,
                file_name=f"gridirongpt_rankings_{scoring}_{teams}team.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as exc:
            export_columns[1].warning(f"PDF export unavailable: {exc}")

    st.caption(
        "Draft Day defaults to rank, player, position, team, bye, score, and "
        "football notes. Full Analysis adds all model components and provenance."
    )

    st.divider()
    tabs = st.tabs(("Overall",) + POSITIONS)

    with tabs[0]:
        _render_overall_rows(
            snapshot.population.explained_overall,
            football_summaries=football_summaries,
            limit=overall_limit,
        )

    for tab, position in zip(tabs[1:], POSITIONS):
        with tab:
            scores = snapshot.population.by_position.get(position, [])
            st.caption(
                f"Top {min(position_limit, len(scores))} {position} rankings "
                "from the same integrated scoring model."
            )
            _render_score_rows(
                scores[:position_limit],
                football_summaries=football_summaries,
            )
