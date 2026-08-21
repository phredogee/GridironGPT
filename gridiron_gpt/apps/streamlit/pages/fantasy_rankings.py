from __future__ import annotations

import importlib.util
from pathlib import Path

from gridiron_gpt.draft.fantasy_best_fit_view import build_best_fit_views
from gridiron_gpt.draft.fantasy_roster_advice_service import FantasyRosterAdviceService


_legacy_path = Path(__file__).with_name("fantasy_rankings_legacy.py")
_spec = importlib.util.spec_from_file_location("_gridiron_fantasy_rankings_legacy", _legacy_path)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load fantasy rankings implementation from {_legacy_path}")
_legacy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_legacy)

# Preserve the existing page API while keeping this integration layer small.
for _name in dir(_legacy):
    if not _name.startswith("__"):
        globals().setdefault(_name, getattr(_legacy, _name))

# The legacy page contains one harmless roster-advice lookup in score-row rendering.
# Give it a neutral default so non-draft rendering cannot fail before Draft Assistant runs.
_legacy.roster_advice = FantasyRosterAdviceService().build([])


def _render_draft_assistant(population, market_views, drafted_ids, projection_views):
    best_available = _legacy._best_available_scores(population, drafted_ids, limit=5)
    best_value = _legacy._best_value_scores(population, market_views, drafted_ids, limit=5)
    my_team_ids = set(_legacy._my_team_ids())
    by_id = {score.player_id: score for score in population.overall}
    roster_scores = [by_id[player_id] for player_id in my_team_ids if player_id in by_id]
    roster_advice = FantasyRosterAdviceService().build(roster_scores)
    _legacy.roster_advice = roster_advice

    candidates = [score for score in population.overall if score.player_id not in drafted_ids]
    best_fit = build_best_fit_views(candidates, roster_scores, market_views, limit=5)

    _legacy.st.markdown("### Draft Assistant")
    _legacy.st.caption(
        "Live recommendations use the frozen GridironGPT board and update instantly as players are drafted. "
        "Use Mine when the pick belongs to your roster. Best Fit is advisory and does not change production rankings."
    )
    _legacy.st.caption(roster_advice.summary)

    columns = _legacy.st.columns(3)

    with columns[0]:
        _legacy.st.markdown("**Best Available**")
        if not best_available:
            _legacy.st.caption("No undrafted ranked players remain.")
        for score in best_available:
            view = market_views.get(score.player_id)
            details = [score.position or "-", score.team or "-"]
            if view is not None:
                details.insert(1, f"{score.position or '-'}{view.position_rank}")
                details.append(f"Tier {view.tier}")
            roster_badge = roster_advice.badge_for(score.position)
            projection = _legacy._projection_badge(score, projection_views)
            row = _legacy.st.columns([5, 1.5])
            row[0].write(
                f"**{score.player_name}** · {' · '.join(details)} · {score.ranking_score:.2f}"
                + (f" · {projection}" if projection else "")
                + (f" · **{roster_badge}**" if roster_badge else "")
            )
            with row[1]:
                _legacy._draft_row_control(score, scope="assistant_available", drafted_ids=drafted_ids)

    with columns[1]:
        _legacy.st.markdown("**Best Value**")
        if not best_value:
            _legacy.st.caption("No positive Draft Value opportunities are currently available.")
        for score in best_value:
            view = market_views[score.player_id]
            adp = f"ADP {view.consensus_adp:.1f}" if view.consensus_adp is not None else "ADP —"
            projection = _legacy._projection_badge(score, projection_views)
            roster_badge = roster_advice.badge_for(score.position)
            row = _legacy.st.columns([5, 1.5])
            row[0].write(
                f"**{score.player_name}** · {score.position or '-'}{view.position_rank} · "
                f"Tier {view.tier} · {adp} · **{view.draft_value:+.1f} value**"
                + (f" · {projection}" if projection else "")
                + (f" · **{roster_badge}**" if roster_badge else "")
            )
            with row[1]:
                _legacy._draft_row_control(score, scope="assistant_value", drafted_ids=drafted_ids)

    with columns[2]:
        _legacy.st.markdown("**Best Fit Right Now**")
        _legacy.st.caption("Advisory blend of board strength, active roster need, and draft value.")
        if not best_fit:
            _legacy.st.caption("No undrafted ranked players remain.")
        for fit in best_fit:
            score = fit.score
            projection = _legacy._projection_badge(score, projection_views)
            row = _legacy.st.columns([5, 1.5])
            row[0].write(
                f"**{score.player_name}** · {score.position or '-'} · {score.team or '-'} · "
                f"Board {score.ranking_score:.2f} · **Fit {fit.fit_score:.2f}** · {fit.reason}"
                + (f" · {projection}" if projection else "")
            )
            with row[1]:
                _legacy._draft_row_control(score, scope="assistant_fit", drafted_ids=drafted_ids)


# render_fantasy_rankings resolves helpers from the legacy module globals, so patch the
# tested integration into that namespace and then expose the original page entry point.
_legacy._render_draft_assistant = _render_draft_assistant
render_fantasy_rankings = _legacy.render_fantasy_rankings
