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
    FantasyRankingPopulation,
    FantasyRankingPopulationService,
)
from gridiron_gpt.draft.football_ranking_explanation_service import (
    FootballRankingExplanationService,
)
from gridiron_gpt.football_state.repositories.jsonl_player_state_repository import (
    JsonlPlayerStateRepository,
)


POSITIONS = ("QB", "RB", "WR", "TE")
DRAFTED_IDS_KEY = "fantasy_rankings_drafted_player_ids"
DRAFTED_PLAYER_CSS = """
<style>
/* A drafted expander contains the hidden marker rendered inside its body. */
div[data-testid="stExpander"]:has(.gridiron-drafted-marker) {
    background: rgba(128, 128, 128, 0.18) !important;
    border-color: rgba(128, 128, 128, 0.42) !important;
    opacity: 0.58;
    filter: grayscale(0.75);
}

div[data-testid="stExpander"]:has(.gridiron-drafted-marker) > details > summary {
    background: rgba(128, 128, 128, 0.14) !important;
}

div[data-testid="stExpander"]:has(.gridiron-drafted-marker) > details > summary p {
    text-decoration: line-through;
    text-decoration-thickness: 1px;
}

.gridiron-drafted-marker {
    display: none;
}
</style>
"""


@st.cache_resource(show_spinner=False)
def build_fantasy_ranking_snapshot(
    *,
    scoring: str = "ppr",
    teams: int = 12,
    limit: int | None = None,
):
    """Build and cache the production fantasy-ranking snapshot used by the UI."""
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


def _drafted_ids() -> list[str]:
    """Return ordered drafted player IDs for the current Streamlit session."""
    if DRAFTED_IDS_KEY not in st.session_state:
        st.session_state[DRAFTED_IDS_KEY] = []
    return list(st.session_state[DRAFTED_IDS_KEY])


def _mark_drafted(player_id: str) -> None:
    drafted = _drafted_ids()
    if player_id not in drafted:
        drafted.append(player_id)
    st.session_state[DRAFTED_IDS_KEY] = drafted


def _restore_drafted(player_id: str) -> None:
    st.session_state[DRAFTED_IDS_KEY] = [
        value for value in _drafted_ids() if value != player_id
    ]


def _undo_last_drafted() -> None:
    drafted = _drafted_ids()
    if drafted:
        drafted.pop()
    st.session_state[DRAFTED_IDS_KEY] = drafted


def _clear_drafted() -> None:
    st.session_state[DRAFTED_IDS_KEY] = []


def _remaining_population(
    population: FantasyRankingPopulation,
    drafted_ids: set[str],
) -> FantasyRankingPopulation:
    """Return a view with drafted players removed, primarily for draft exports."""
    if not drafted_ids:
        return population

    overall = [score for score in population.overall if score.player_id not in drafted_ids]
    by_position = {
        position: [score for score in scores if score.player_id not in drafted_ids]
        for position, scores in population.by_position.items()
    }
    explained = [
        item
        for item in population.explained_overall
        if item.score.player_id not in drafted_ids
    ]
    return FantasyRankingPopulation(
        overall=overall,
        by_position=by_position,
        explained_overall=explained,
    )


def _render_drafted_players(population: FantasyRankingPopulation) -> None:
    drafted = _drafted_ids()
    if not drafted:
        st.caption("No players marked drafted yet.")
        return

    by_id = {score.player_id: score for score in population.overall}
    controls = st.columns([1, 1, 5])
    if controls[0].button(
        "Undo Last",
        key="fantasy_rankings_undo_last_drafted",
        use_container_width=True,
    ):
        _undo_last_drafted()
        st.rerun()
    if controls[1].button(
        "Reset Draft",
        key="fantasy_rankings_reset_drafted",
        use_container_width=True,
    ):
        _clear_drafted()
        st.rerun()

    with st.expander(f"Drafted Players ({len(drafted)})", expanded=False):
        for player_id in reversed(drafted):
            score = by_id.get(player_id)
            if score is None:
                continue
            row = st.columns([5, 1])
            row[0].write(
                f"{score.player_name} · {score.position or '-'} · {score.team or '-'}"
            )
            if row[1].button(
                "Restore",
                key=f"fantasy_rankings_restore_{player_id}",
                use_container_width=True,
            ):
                _restore_drafted(player_id)
                st.rerun()


def _expansion_controls(scope: str) -> str:
    state_key = f"fantasy_rankings_expansion_{scope.lower()}"
    if state_key not in st.session_state:
        st.session_state[state_key] = "default"

    controls = st.columns([1, 1, 5])
    if controls[0].button(
        "Expand All",
        key=f"fantasy_rankings_expand_all_{scope.lower()}",
        use_container_width=True,
    ):
        st.session_state[state_key] = "all"
    if controls[1].button(
        "Collapse All",
        key=f"fantasy_rankings_collapse_all_{scope.lower()}",
        use_container_width=True,
    ):
        st.session_state[state_key] = "none"

    return st.session_state[state_key]


def _is_expanded(rank: int, mode: str, *, default_count: int = 5) -> bool:
    if mode == "all":
        return True
    if mode == "none":
        return False
    return rank <= default_count


def _market_badge(score, market_views: dict) -> str:
    view = market_views.get(score.player_id)
    if view is None:
        return ""
    parts = [f"{score.position or '-'}{view.position_rank}", f"Tier {view.tier}"]
    if view.consensus_adp is not None:
        parts.append(f"ADP {view.consensus_adp:.1f}")
    if view.draft_value is not None:
        sign = "+" if view.draft_value > 0 else ""
        parts.append(f"Value {sign}{view.draft_value:.1f}")
    return " · ".join(parts)


def _render_market_context(score, market_views: dict) -> None:
    view = market_views.get(score.player_id)
    if view is None:
        return

    columns = st.columns(5)
    columns[0].metric("Position Rank", f"{score.position or '-'}{view.position_rank}")
    columns[1].metric("Tier", view.tier)
    adp_label = "Consensus ADP" if view.adp_source_count >= 2 else "ADP"
    columns[2].metric(
        adp_label,
        f"{view.consensus_adp:.1f}" if view.consensus_adp is not None else "—",
    )
    columns[3].metric(
        "ADP Spread",
        f"{view.adp_spread:.1f}" if view.adp_spread is not None else "—",
    )
    columns[4].metric(
        "Draft Value",
        f"{view.draft_value:+.1f}" if view.draft_value is not None else "—",
    )

    if view.source_adps:
        source_text = " · ".join(
            f"{source}: {value:.1f}"
            for source, value in sorted(view.source_adps.items())
        )
        st.caption(f"ADP sources: {source_text}")


def _render_drafted_marker() -> None:
    """Mark the containing Streamlit expander so CSS can mute the full card."""
    st.markdown(
        '<span class="gridiron-drafted-marker" aria-hidden="true"></span>',
        unsafe_allow_html=True,
    )


def _draft_control(score, *, scope: str, drafted_ids: set[str]) -> None:
    drafted = score.player_id in drafted_ids
    if drafted:
        st.button(
            "DRAFTED",
            key=f"fantasy_rankings_drafted_{scope}_{score.player_id}",
            disabled=True,
        )
        return

    if st.button(
        "Mark Drafted",
        key=f"fantasy_rankings_mark_drafted_{scope}_{score.player_id}",
        type="primary",
    ):
        _mark_drafted(score.player_id)
        st.rerun()


def _render_score_rows(
    scores,
    *,
    football_summaries: dict[str, str],
    market_views: dict,
    drafted_ids: set[str] | None = None,
    draft_mode: bool = False,
    scope: str,
    expansion_mode: str = "default",
    expanded_count: int = 5,
) -> None:
    drafted_ids = drafted_ids or set()
    for rank, score in enumerate(scores, start=1):
        drafted = draft_mode and score.player_id in drafted_ids
        market_badge = _market_badge(score, market_views)
        prefix = "DRAFTED · " if drafted else ""
        header = (
            f"{prefix}#{rank}  {score.player_name}  ·  {market_badge or (score.position or '-')}  ·  "
            f"{score.team or '-'}  ·  {score.ranking_score:.2f}"
        )
        with st.expander(
            header,
            expanded=_is_expanded(rank, expansion_mode, default_count=expanded_count),
        ):
            if drafted:
                _render_drafted_marker()
                st.caption("Drafted — no longer available")
            if draft_mode:
                _draft_control(score, scope=scope, drafted_ids=drafted_ids)
            _render_market_context(score, market_views)

            football_summary = football_summaries.get(score.player_id)
            if football_summary:
                st.markdown("**Football read**")
                st.write(football_summary)

            component_columns = st.columns(len(score.components))
            for column, (name, value) in zip(component_columns, score.components.items()):
                column.metric(name.title(), f"{value:.1f}")

            if score.provenance:
                with st.expander("Evidence & provenance", expanded=False):
                    for name, source in score.provenance.items():
                        st.write(f"• **{name.title()}** — {source}")


def _render_overall_rows(
    explained_overall,
    *,
    football_summaries: dict[str, str],
    market_views: dict,
    limit: int,
    drafted_ids: set[str] | None = None,
    draft_mode: bool = False,
    expansion_mode: str = "default",
) -> None:
    drafted_ids = drafted_ids or set()
    for item in explained_overall[:limit]:
        score = item.score
        explanation = item.explanation
        drafted = draft_mode and score.player_id in drafted_ids
        market_badge = _market_badge(score, market_views)
        prefix = "DRAFTED · " if drafted else ""
        header = (
            f"{prefix}#{item.rank}  {score.player_name}  ·  {market_badge or (score.position or '-')}  ·  "
            f"{score.team or '-'}  ·  {score.ranking_score:.2f}"
        )
        with st.expander(header, expanded=_is_expanded(item.rank, expansion_mode)):
            if drafted:
                _render_drafted_marker()
                st.caption("Drafted — no longer available")
            if draft_mode:
                _draft_control(score, scope="overall", drafted_ids=drafted_ids)
            _render_market_context(score, market_views)

            football_summary = football_summaries.get(score.player_id)
            if football_summary:
                st.markdown("**Football read**")
                st.write(football_summary)

            st.markdown("**Model explanation**")
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
    st.markdown(DRAFTED_PLAYER_CSS, unsafe_allow_html=True)
    st.markdown("### Integrated Fantasy Rankings")
    st.caption(
        "GridironGPT combines historical production, consensus market ADP, recent role, "
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
    with controls[4]:
        draft_mode = st.toggle(
            "Draft Mode",
            value=False,
            key="fantasy_rankings_draft_mode",
            help="Mark drafted players in place while preserving the original draft board order.",
        )

    refresh = st.columns([1, 5])
    if refresh[0].button(
        "Refresh Rankings",
        key="fantasy_rankings_refresh_snapshot",
        use_container_width=True,
        help="Rebuild rankings and refresh external ADP data. Draft selections are preserved.",
    ):
        build_fantasy_ranking_snapshot.clear()
        st.rerun()

    try:
        snapshot = build_fantasy_ranking_snapshot(scoring=scoring, teams=teams, limit=None)
    except Exception as exc:
        st.error("Fantasy rankings could not be built from the current local data.")
        with st.expander("Technical details", expanded=False):
            st.code(str(exc))
        return

    drafted_ids = set(_drafted_ids()) if draft_mode else set()
    export_population = _remaining_population(snapshot.population, drafted_ids)

    meta = st.columns(4)
    meta[0].metric("Historical", snapshot.historical_player_count)
    source_label = ", ".join(snapshot.adp_sources) if snapshot.adp_sources else "Unavailable"
    meta[1].metric(
        "Consensus ADP",
        snapshot.adp_player_count,
        delta=source_label,
    )
    meta[2].metric(
        "Role evidence",
        snapshot.role_player_count,
        delta=(f"{snapshot.role_season}" if snapshot.role_season else "Unavailable"),
    )
    if draft_mode:
        meta[3].metric(
            "Available",
            len(export_population.overall),
            delta=f"{len(drafted_ids)} drafted",
        )
    else:
        meta[3].metric("Ranked players", len(snapshot.population.overall))

    if not snapshot.population.explained_overall:
        st.info("No players currently have sufficient anchor evidence to rank.")
        return

    if draft_mode:
        _render_drafted_players(snapshot.population)

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
                export_population,
                overall_limit=overall_limit,
                position_limit=position_limit,
                selected_fields=selected_fields,
                bye_week_by_team=bye_weeks,
                football_notes_by_player_id=football_notes,
                market_views_by_player_id=snapshot.market_views_by_player_id,
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
                export_population,
                overall_limit=overall_limit,
                position_limit=position_limit,
                selected_fields=selected_fields,
                bye_week_by_team=bye_weeks,
                football_notes_by_player_id=football_notes,
                market_views_by_player_id=snapshot.market_views_by_player_id,
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
        "Draft Day includes position rank, tier, consensus ADP, Draft Value, bye, "
        "GridironGPT score, and football notes. Drafted players remain visible on the "
        "live board but are excluded from Draft Mode exports."
    )

    st.divider()
    tabs = st.tabs(("Overall",) + POSITIONS)

    with tabs[0]:
        overall_expansion = _expansion_controls("overall")
        _render_overall_rows(
            snapshot.population.explained_overall,
            football_summaries=football_summaries,
            market_views=snapshot.market_views_by_player_id,
            limit=overall_limit,
            drafted_ids=drafted_ids,
            draft_mode=draft_mode,
            expansion_mode=overall_expansion,
        )

    for tab, position in zip(tabs[1:], POSITIONS):
        with tab:
            scores = snapshot.population.by_position.get(position, [])
            st.caption(
                f"Top {min(position_limit, len(scores))} {position} rankings "
                "from the same integrated scoring model."
            )
            expansion_mode = _expansion_controls(position)
            _render_score_rows(
                scores[:position_limit],
                football_summaries=football_summaries,
                market_views=snapshot.market_views_by_player_id,
                drafted_ids=drafted_ids,
                draft_mode=draft_mode,
                scope=position.lower(),
                expansion_mode=expansion_mode,
            )
