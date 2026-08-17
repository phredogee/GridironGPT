from __future__ import annotations

import argparse

from gridiron_cortex.remember.json_player_scorecard_repository import JsonPlayerScorecardRepository
from gridiron_gpt.draft.espn_adp_loader import EspnAdpLoader
from gridiron_gpt.draft.fantasy_player_projection_service import FantasyPlayerProjectionService
from gridiron_gpt.draft.fantasy_projection_view_service import build_projection_views
from gridiron_gpt.draft.fantasy_ranking_data_service import FantasyRankingDataService
from gridiron_gpt.draft.fantasy_ranking_population_service import FantasyRankingPopulationService
from gridiron_gpt.draft.projection_weight_comparison_service import ProjectionWeightComparisonService
from gridiron_gpt.football_state.repositories.jsonl_player_state_repository import JsonlPlayerStateRepository


def _movement(value: int) -> str:
    if value > 0:
        return f"+{value}"
    if value < 0:
        return str(value)
    return "—"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare live fantasy rankings with hypothetical 5% and 10% projection weights."
    )
    parser.add_argument("--scoring", choices=("ppr", "half_ppr", "standard"), default="ppr")
    parser.add_argument("--teams", type=int, default=12)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--movers", type=int, default=15)
    args = parser.parse_args()

    population_service = FantasyRankingPopulationService(
        JsonlPlayerStateRepository(),
        JsonPlayerScorecardRepository("data/cortex/player_scorecards.jsonl"),
    )
    snapshot = FantasyRankingDataService(
        population_service,
        adp_source_loaders={"ESPN": EspnAdpLoader(season=2026).load},
    ).build(scoring=args.scoring, teams=args.teams, limit=None)

    projections = FantasyPlayerProjectionService().build(scoring=args.scoring)
    projection_views = build_projection_views(projections)
    rows = ProjectionWeightComparisonService().compare(snapshot.population, projection_views)

    print(f"Scoring: {args.scoring} | Teams: {args.teams}")
    print("Production rankings are unchanged; 5% and 10% are experimental only.\n")
    print(f"{'Player':28} {'Pos':>3} {'Now':>5} {'5%':>5} {'Move':>5} {'10%':>5} {'Move':>5} {'Proj':>7}")
    print("-" * 73)
    for row in rows[: max(0, args.limit)]:
        projected = f"{row.projected_points:.0f}" if row.projected_points is not None else "—"
        print(
            f"{row.player_name[:28]:28} {(row.position or '-')[:3]:>3} "
            f"{row.production_rank:>5} {row.rank_5:>5} {_movement(row.movement_5):>5} "
            f"{row.rank_10:>5} {_movement(row.movement_10):>5} {projected:>7}"
        )

    movers = sorted(
        rows,
        key=lambda row: (max(abs(row.movement_5), abs(row.movement_10)), abs(row.movement_10)),
        reverse=True,
    )[: max(0, args.movers)]
    print("\nLargest rank movements")
    print("-" * 73)
    for row in movers:
        print(
            f"{row.player_name[:28]:28} {(row.position or '-')[:3]:>3} "
            f"#{row.production_rank} -> #{row.rank_5} ({_movement(row.movement_5)}) at 5% | "
            f"#{row.rank_10} ({_movement(row.movement_10)}) at 10%"
        )


if __name__ == "__main__":
    main()
