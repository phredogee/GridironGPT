from __future__ import annotations

import argparse

from gridiron_gpt.draft.fantasy_player_projection_service import FantasyPlayerProjectionService


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect GridironGPT fantasy projections from regular-season NFL history.")
    parser.add_argument("--scoring", choices=("standard", "half_ppr", "ppr"), default="ppr")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--games", type=float, default=17.0)
    args = parser.parse_args()

    projections = FantasyPlayerProjectionService().ranked(
        scoring=args.scoring,
        expected_games=args.games,
    )

    print(f"Projection records: {len(projections)}")
    print(f"Scoring: {args.scoring} | Expected games: {args.games:g}")
    print("Regular-season history only; preseason statistics are not used.\n")
    print(f"{'#':>3}  {'Player':<28} {'Pts':>8} {'PPG':>7}")
    print("-" * 52)
    for rank, projection in enumerate(projections[: max(args.limit, 0)], start=1):
        ppg = projection.fantasy.projected_ppg
        ppg_text = "-" if ppg is None else f"{ppg:.2f}"
        print(f"{rank:>3}  {projection.player_name:<28.28} {projection.fantasy.projected_points:>8.2f} {ppg_text:>7}")


if __name__ == "__main__":
    main()
