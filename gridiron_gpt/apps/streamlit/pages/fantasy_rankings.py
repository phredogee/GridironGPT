from __future__ import annotations

import streamlit as st

from gridiron_cortex.remember.json_player_scorecard_repository import (
    JsonPlayerScorecardRepository,
)
from gridiron_gpt.data_ingest.player_scores import calculate_player_scores
from gridiron_gpt.draft.bye_week_service import ByeWeekService
from gridiron_gpt.draft.espn_adp_loader import EspnAdpLoader
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
    espn_adp_loader = EspnAdpLoader(season=2026)
    service = FantasyRankingDataService(
        FantasyRankingPopulationService(
            player_repository,
            scorecard_repository,
        ),
        adp_source_loaders={"ESPN": espn_adp_loader.load},
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


def _format_component(value: float | None) -> str:
    return "—" if value is None else f"{value:.1f}"


def _format_market_value(value: float | None, *, signed: bool = False) -> str:
    if value is None:
        return "—"
    return f"{value:+.1f}" if signed else f"{value:.1f}"


def _render_rankings(
    rankings,
    *,
    market_views_by_player_id,
    football_notes_by_player_id: dict[str, str],
    football_summaries_by_player_id: dict[str, str],
    expanded: bool,
):
    for rank, score in enumerate(rankings, start=1):
        market_view = market_views_by_player_id.get(score.player_id)
        position_rank = market_view.position_rank if market_view else None
        tier = market_view.tier if market_view else None
        title_bits = [f"#{rank} {score.player_name}", f"{score.position} · {score.team}"]
        if position_rank is not None:
            title_bits.append(f"{score.position}{position_rank}")
        if tier is not None:
            title_bits.append(f"Tier {tier}")
        title_bits.append(f"{score.overall_score:.2f}")

        with st.expander("  |  ".join(title_bits), expanded=expanded):
            st.markdown(
                " | ".join(
                    [
                        f"**Baseline:** {_format_component(score.baseline_score)}",
                        f"**Market:** {_format_component(score.market_score)}",
                        f"**Role:** {_format_component(score.role_score)}",
                        f"**Cortex:** {_format_component(score.cortex_score)}",
                        f"**Availability:** {_format_component(score.availability_score)}",
                    ]
                )
            )
            if market_view is not None:
                adp_label = (
                    "Consensus ADP"
                    if market_view.adp_source_count >= 2
                    else "ADP"
                )
                st.markdown(
                    " | ".join(
                        [
                            f"**{adp_label}:** {_format_market_value(market_view.consensus_adp)}",
                            f"**ADP Spread:** {_format_market_value(market_view.adp_spread)}",
                            f"**Sources:** {market_view.adp_source_count}",
                            f"**Draft Value:** {_format_market_value(market_view.draft_value, signed=True)}",
                        ]
                    )
                )
                if market_view.source_adps:
                    source_text = ", ".join(
                        f"{source}: {value:.1f}"
                        for source, value in sorted(market_view.source_adps.items())
                    )
                    st.caption(f"ADP sources: {source_text}")
            st.caption(score.explanation)
            st.markdown(
                f"**Football:** {football_summaries_by_player_id.get(score.player_id, football_notes_by_player_id.get(score.player_id, 'No recent football context'))}"
            )


def _render_export_controls(
    population,
    *,
    market_views_by_player_id,
    bye_week_by_team: dict[str, int],
    football_notes_by_player_id: dict[str, str],
):
    st.subheader("Export Rankings")
    preset = st.radio(
        "Export preset",
        ("Draft Day", "Full Analysis", "Custom"),
        horizontal=True,
    )

    if preset == "Draft Day":
        default_fields = list(DRAFT_DAY_FIELDS)
    elif preset == "Full Analysis":
        default_fields = list(FULL_ANALYSIS_FIELDS)
    else:
        default_fields = list(DRAFT_DAY_FIELDS)

    selected_fields = st.multiselect(
        "Columns to include",
        options=list(FIELD_LABELS),
        default=default_fields,
        format_func=lambda field: FIELD_LABELS[field],
    )
    if not selected_fields:
        st.warning("Select at least one export column.")
        return

    xlsx_data = build_rankings_xlsx(
        population,
        selected_fields=selected_fields,
        bye_week_by_team=bye_week_by_team,
        football_notes_by_player_id=football_notes_by_player_id,
        market_views_by_player_id=market_views_by_player_id,
    )
    pdf_data = build_rankings_pdf(
        population,
        selected_fields=selected_fields,
        bye_week_by_team=bye_week_by_team,
        football_notes_by_player_id=football_notes_by_player_id,
        market_views_by_player_id=market_views_by_player_id,
    )

    left, right = st.columns(2)
    left.download_button(
        "Download XLSX",
        data=xlsx_data,
        file_name="gridirongpt_rankings.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    right.download_button(
        "Download PDF",
        data=pdf_data,
        file_name="gridirongpt_rankings.pdf",
        mime="application/pdf",
        use_container_width=True,
    )


def render():
    st.title("Fantasy Rankings")
    st.caption(
        "Integrated GridironGPT rankings from historical production, current market value, "
        "recent role, Cortex intelligence, and canonical availability."
    )

    control_col1, control_col2, control_col3 = st.columns(3)
    scoring = control_col1.selectbox("Scoring", ("ppr", "half_ppr", "standard"))
    teams = control_col2.selectbox("League size", (8, 10, 12, 14, 16), index=2)
    limit = control_col3.selectbox("Overall players", (25, 50, 100, 200), index=1)

    with st.spinner("Building integrated fantasy rankings..."):
        snapshot = build_fantasy_ranking_snapshot(
            scoring=scoring,
            teams=teams,
            limit=limit,
        )

    population = snapshot.population
    bye_week_by_team = ByeWeekService().load()
    football_notes, football_summaries = _football_notes(population)

    metric_cols = st.columns(5)
    metric_cols[0].metric("Historical", snapshot.historical_player_count)
    metric_cols[1].metric("ADP", snapshot.adp_player_count)
    metric_cols[2].metric("ADP Year", snapshot.adp_year or "—")
    metric_cols[3].metric("Role", snapshot.role_player_count)
    metric_cols[4].metric("Role Season", snapshot.role_season or "—")
    if snapshot.adp_sources:
        st.caption(f"ADP sources: {', '.join(snapshot.adp_sources)}")

    _render_export_controls(
        population,
        market_views_by_player_id=snapshot.market_views_by_player_id,
        bye_week_by_team=bye_week_by_team,
        football_notes_by_player_id=football_notes,
    )

    st.divider()
    expand_all = st.toggle("Expand all ranking entries", value=False)

    tabs = st.tabs(("Overall",) + POSITIONS)
    with tabs[0]:
        _render_rankings(
            population.overall,
            market_views_by_player_id=snapshot.market_views_by_player_id,
            football_notes_by_player_id=football_notes,
            football_summaries_by_player_id=football_summaries,
            expanded=expand_all,
        )

    for tab, position in zip(tabs[1:], POSITIONS):
        with tab:
            _render_rankings(
                population.by_position.get(position, ()),
                market_views_by_player_id=snapshot.market_views_by_player_id,
                football_notes_by_player_id=football_notes,
                football_summaries_by_player_id=football_summaries,
                expanded=expand_all,
            )


if __name__ == "__main__":
    render()
