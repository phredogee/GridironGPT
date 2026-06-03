# gridiron_gpt/draft/scorer.py

import pandas as pd

SEASONS = [2023, 2024, 2025]
SEASON_WEIGHTS = {2023: 0.15, 2024: 0.30, 2025: 0.55}


def get_historical_scores(scoring: str = "ppr", seasons: list = None) -> pd.DataFrame:
    """Fetch and weight 3-season player fantasy totals from nflreadpy."""
    import nflreadpy as nfl

    seasons = seasons or SEASONS
    frames = []

    for season in seasons:
        try:
            df = nfl.load_player_stats(seasons=[season])
            if hasattr(df, "to_pandas"):
                df = df.to_pandas()

            if scoring == "standard":
                score_col = "fantasy_points"
            else:
                score_col = "fantasy_points_ppr"

            if score_col not in df.columns:
                score_col = next(
                    (c for c in ["fantasy_points_ppr", "fantasy_points"] if c in df.columns),
                    None,
                )
            if score_col is None:
                print(f"⚠️ No fantasy point column found for {season}, skipping.")
                continue

            agg = (
                df.groupby(["player_display_name", "position", "team"])
                .agg(total_points=(score_col, "sum"), games=(score_col, "count"))
                .reset_index()
            )

            if scoring == "half_ppr":
                # ppr_total = standard + receptions; half_ppr ≈ standard + 0.5*rec
                # Approximate from ppr: subtract ~0.5 reception value (rough: ~15% of ppr total for skill positions)
                agg["total_points"] = agg["total_points"] * 0.88

            agg["season"] = season
            agg["weight"] = SEASON_WEIGHTS[season]
            frames.append(agg)

        except Exception as e:
            print(f"⚠️ Could not load {season} data: {e}")

    if not frames:
        return pd.DataFrame(
            columns=["player_display_name", "position", "team", "hist_score", "games_played"]
        )

    combined = pd.concat(frames, ignore_index=True)
    combined["weighted_pts"] = combined["total_points"] * combined["weight"]

    summary = (
        combined.groupby(["player_display_name", "position"])
        .agg(hist_score=("weighted_pts", "sum"), games_played=("games", "sum"), team=("team", "last"))
        .reset_index()
    )

    return summary.sort_values("hist_score", ascending=False).reset_index(drop=True)
