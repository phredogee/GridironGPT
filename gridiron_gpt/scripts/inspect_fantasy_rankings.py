from __future__ import annotations

import argparse

from gridiron_cortex.remember.json_player_scorecard_repository import JsonPlayerScorecardRepository
from gridiron_gpt.draft.espn_adp_loader import EspnAdpLoader
from gridiron_gpt.draft.fantasy_ranking_data_service import FantasyRankingDataService
from gridiron_gpt.draft.fantasy_ranking_population_service import FantasyRankingPopulationService
from gridiron_gpt.football_state.repositories.jsonl_player_state_repository import JsonlPlayerStateRepository


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect live production fantasy rankings.")
    parser.add_argument("--scoring", choices=("ppr", "half_ppr", "standard"), default="ppr")
    parser.add_argument("--teams", type=int, default=12)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument(
        "--components",
        action="store_true",
        help="Show active/missing ranking evidence for each player.",
    )
    args = parser.parse_args()

    population_service = FantasyRankingPopulationService(
        JsonlPlayerStateRepository(),
        JsonPlayerScorecardRepository("data/cortex/player_scorecards.jsonl"),
    )
    snapshot = FantasyRankingDataService(
        population_service,
        adp_source_loaders={"ESPN": EspnAdpLoader(season=2026).load},
    ).build(scoring=args.scoring, teams=args.teams, limit=args.limit)

    print(f"Scoring: {args.scoring} | Teams: {args.teams}")
    print(
        f"Historical: {snapshot.historical_player_count} | "
        f"ADP: {snapshot.adp_player_count} | "
        f"Role: {snapshot.role_player_count} | "
        f"Projections: {snapshot.projection_player_count}"
    )
    print("Production ranking model; projection is active at its configured production weight.\n")
    print(f"{'#':>3}  {'Player':28} {'Pos':>3} {'Team':>4} {'Score':>7} {'Proj':>7} {'ProjWt':>7}")
    print("-" * 72)

    component_order = ("baseline", "market", "role", "cortex", "availability", "projection")
    for rank, row in enumerate(snapshot.population.overall, start=1):
        projection = row.components.get("projection")
        projection_weighted = row.weighted_components.get("projection")
        projection_text = f"{projection:.1f}" if projection is not None else "—"
        weighted_text = f"{projection_weighted:.2f}" if projection_weighted is not None else "—"
        print(
            f"{rank:>3}  {row.player_name[:28]:28} {(row.position or '-')[:3]:>3} "
            f"{(row.team or '-')[:4]:>4} {row.ranking_score:>7.2f} "
            f"{projection_text:>7} {weighted_text:>7}"
        )
        if args.components:
            active = [name for name in component_order if name in row.components]
            missing = [name for name in component_order if name not in row.components]
            effective_projection_weight = None
            if projection is not None and projection > 0 and projection_weighted is not None:
                effective_projection_weight = (projection_weighted / projection) * 100.0
            effective_text = (
                f"{effective_projection_weight:.2f}%"
                if effective_projection_weight is not None
                else "—"
            )
            print(
                f"     active: {', '.join(active) or 'none'} | "
                f"missing: {', '.join(missing) or 'none'} | "
                f"effective projection weight: {effective_text}"
            )


if __name__ == "__main__":
    main()
