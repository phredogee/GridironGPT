# gridiron_gpt/cli/draft.py

import click
import pandas as pd

from gridiron_cortex.remember.json_player_scorecard_repository import JsonPlayerScorecardRepository
from gridiron_gpt.draft.config import LeagueConfig
from gridiron_gpt.draft.espn_adp_loader import EspnAdpLoader
from gridiron_gpt.draft.fantasy_ranking_cli_adapter import production_rankings_to_cli_frame
from gridiron_gpt.draft.fantasy_ranking_data_service import FantasyRankingDataService
from gridiron_gpt.draft.fantasy_ranking_population_service import FantasyRankingPopulationService
from gridiron_gpt.draft.ranker import get_round_targets
from gridiron_gpt.feedback import banner, error
from gridiron_gpt.football_state.repositories.jsonl_player_state_repository import JsonlPlayerStateRepository


def _build_production_cli_frame(*, scoring: str, teams: int):
    population_service = FantasyRankingPopulationService(
        JsonlPlayerStateRepository(),
        JsonPlayerScorecardRepository("data/cortex/player_scorecards.jsonl"),
    )
    snapshot = FantasyRankingDataService(
        population_service,
        adp_source_loaders={"ESPN": EspnAdpLoader(season=2026).load},
    ).build(scoring=scoring, teams=teams)
    adp_by_name = {
        record.player_name: record.consensus_adp
        for record in snapshot.consensus_adp_by_key.values()
    }
    return production_rankings_to_cli_frame(
        snapshot.population,
        adp_by_name=adp_by_name,
        teams=teams,
    )


@click.group()
def draft():
    """🏆 Pre-season draft tools — rank, strategize, and build your board"""
    pass


@draft.command()
@click.option("--position", "-p", default=None, help="Filter by position (QB, RB, WR, TE)")
@click.option("--top", default=30, show_default=True, type=int, help="Number of players to show")
@click.option("--scoring", default="ppr", show_default=True,
              type=click.Choice(["ppr", "half_ppr", "standard"]))
@click.option("--teams", default=12, show_default=True, type=int, help="League size")
@click.option("--rounds", default=15, show_default=True, type=int, help="Number of draft rounds")
@click.option("--changes", "changes_path", default="data/offseason_changes.yaml",
              show_default=True, help="Retained for CLI compatibility; production rankings ignore this option")
def rank(position, top, scoring, teams, rounds, changes_path):
    """📋 Rank players for the upcoming draft using the production ranking engine."""
    LeagueConfig(teams=teams, rounds=rounds, scoring=scoring)
    try:
        df = _build_production_cli_frame(scoring=scoring, teams=teams)
    except Exception as e:
        error(str(e))
        return

    if position:
        df = df[df["position"].str.upper() == position.upper()]
        if df.empty:
            banner(f"No players found for position: {position}", emoji="❓")
            return

    df = df.head(top)

    click.echo(f"\n🏆  Draft Rankings — {scoring.upper()}, {teams}-team\n")
    click.echo(f"  {'#':<4} {'Name':<26} {'Pos':<5} {'Team':<5} {'Base':>6} {'ADP':>6} {'Score':>7}")
    click.echo("  " + "─" * 69)

    for _, row in df.iterrows():
        adp_str = f"{row['adp']:.1f}" if row["adp"] is not None and not pd.isna(row["adp"]) else "—"
        base_str = f"{row['hist_score']:.1f}" if not pd.isna(row["hist_score"]) else "—"
        click.echo(
            f"  {int(row['rank']):<4} {row['name']:<26} {row['position']:<5} {row['team']:<5}"
            f" {base_str:>6} {adp_str:>6} {row['composite']:>7.2f}"
        )
    click.echo()


@draft.command()
@click.option("--round", "round_num", required=True, type=int, help="Draft round number (1–15)")
@click.option("--teams", default=12, show_default=True, type=int)
@click.option("--rounds", default=15, show_default=True, type=int)
@click.option("--scoring", default="ppr", show_default=True,
              type=click.Choice(["ppr", "half_ppr", "standard"]))
@click.option("--changes", "changes_path", default="data/offseason_changes.yaml",
              show_default=True, help="Retained for CLI compatibility; production rankings ignore this option")
def strategy(round_num, teams, rounds, scoring, changes_path):
    """🧠 Draft strategy and top production-ranked targets for a specific round."""
    config = LeagueConfig(teams=teams, rounds=rounds, scoring=scoring)
    targets, advice = get_round_targets(round_num, config)

    pick_start = (round_num - 1) * teams + 1
    pick_end = round_num * teams

    click.echo(f"\n🧠  Round {round_num} Strategy — {scoring.upper()}, {teams}-team\n")
    click.echo(f"  Picks:    #{pick_start}–#{pick_end}")
    click.echo(f"  Targets:  {', '.join(targets)}")
    click.echo(f"  Advice:   {advice}")

    try:
        df = _build_production_cli_frame(scoring=scoring, teams=teams)
        available = df[
            (df["suggested_round"] == round_num) & (df["position"].isin(targets))
        ].head(5)

        if not available.empty:
            click.echo(f"\n  Top production-ranked targets in round {round_num}:")
            for _, row in available.iterrows():
                adp_str = f"ADP {row['adp']:.1f}" if row["adp"] is not None and not pd.isna(row["adp"]) else "ADP —"
                click.echo(
                    f"    #{int(row['rank']):<4} {row['name']:<25} {row['position']:<5} "
                    f"{adp_str}  Score {row['composite']:.2f}"
                )
    except Exception:
        pass

    click.echo()


@draft.command()
@click.option("--scoring", default="ppr", show_default=True,
              type=click.Choice(["ppr", "half_ppr", "standard"]))
@click.option("--teams", default=12, show_default=True, type=int)
@click.option("--rounds", default=15, show_default=True, type=int)
@click.option("--top", default=200, show_default=True, type=int, help="Max players to show")
@click.option("--changes", "changes_path", default="data/offseason_changes.yaml",
              show_default=True, help="Retained for CLI compatibility; production rankings ignore this option")
def board(scoring, teams, rounds, top, changes_path):
    """📌 Full production draft board grouped by rank-derived round."""
    config = LeagueConfig(teams=teams, rounds=rounds, scoring=scoring)

    try:
        df = _build_production_cli_frame(scoring=scoring, teams=teams)
    except Exception as e:
        error(str(e))
        return

    df = df.head(top)

    banner(f"📌 Draft Board — {scoring.upper()}, {teams}-team, {rounds} rounds")
    click.echo(f"  Roster: {config.roster}")
    click.echo(f"  Lineup: {config.lineup}\n")

    current_round = 0
    for _, row in df.iterrows():
        r = int(row["suggested_round"])
        if r != current_round:
            current_round = r
            targets, advice = get_round_targets(current_round, config)
            click.echo(f"\n  ── Round {current_round}  (Target: {', '.join(targets)}) ──")
            click.echo(f"     {advice}\n")

        adp_val = row["adp"]
        adp_str = f"ADP {adp_val:.1f}" if adp_val is not None and not pd.isna(adp_val) else "ADP —"
        click.echo(
            f"  #{int(row['rank']):<4} {row['name']:<26} {row['position']:<5} {row['team']:<5}"
            f" Score {row['composite']:>6.2f}  {adp_str}"
        )

    click.echo()


@draft.command()
@click.option("--scoring", default="ppr", show_default=True,
              type=click.Choice(["ppr", "half_ppr", "standard"]))
@click.option("--season", default=2025, show_default=True, type=int,
              help="Season year to index")
def index(scoring, season):
    """🗂️ Build the ask-query index from historical player stats (offseason use)"""
    import nflreadpy as nfl
    from gridiron_gpt.core.advisor import Advisor

    score_col = "fantasy_points_ppr" if scoring != "standard" else "fantasy_points"

    print(f"📊 Loading {season} player stats...")
    df = nfl.load_player_stats(seasons=[season])
    if hasattr(df, "to_pandas"):
        df = df.to_pandas()

    if score_col not in df.columns:
        score_col = "fantasy_points_ppr" if "fantasy_points_ppr" in df.columns else "fantasy_points"

    agg = (
        df.groupby(["player_display_name", "position", "team"])
        .agg(total_pts=(score_col, "sum"), games=(score_col, "count"))
        .reset_index()
    )
    agg = agg[agg["total_pts"] > 0].sort_values("total_pts", ascending=False)

    players = []
    for _, row in agg.iterrows():
        name = row["player_display_name"]
        pos_code = str(row["position"]).upper()
        team = str(row["team"])
        pts = float(row["total_pts"])
        games = int(row["games"])
        ppg = pts / games if games > 0 else 0
        players.append({
            "player_name": name,
            "position": pos_code,
            "team": team,
            "week": f"{season} season ({games} games)",
            "fantasy_points": pts,
            "surface": f"{ppg:.1f} pts/game average",
            "environment": f"{season} full season",
        })

    advisor = Advisor()
    advisor.build_from_players(players)
    advisor.save()
    click.echo(f"✅ Indexed {len(players)} players from {season} season — ask is ready.")
