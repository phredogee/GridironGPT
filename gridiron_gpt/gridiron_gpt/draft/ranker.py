# gridiron_gpt/draft/ranker.py

import pandas as pd
from .config import LeagueConfig
from .scorer import get_historical_scores
from .fetcher import fetch_adp, fetch_injuries, INJURY_PENALTIES
from .changes import load_offseason_changes

# Positional scarcity windows: which rounds to prioritize each position
POSITIONAL_SCARCITY = {
    "RB":  list(range(1, 8)),    # rounds 1–7: bell cow backs disappear fast
    "WR":  list(range(1, 9)),    # rounds 1–8: WR depth concentrated early
    "TE":  list(range(4, 11)),   # rounds 4–10: elite TE (then cliff)
    "QB":  list(range(6, 12)),   # rounds 6–11: wait on QB, depth is fine
    "K":   list(range(13, 16)),  # rounds 13–15: stream kickers
    "DEF": list(range(13, 16)),  # rounds 13–15: stream defenses
}

ROUND_ADVICE = {
    range(1, 3):   "Best available RB or WR. Elite skill positions dominate here.",
    range(3, 5):   "Continue RB/WR depth. Grab elite TE (Kelce-tier) if available.",
    range(5, 7):   "Fill TE if open. Consider top-10 QB if falling to you.",
    range(7, 10):  "Draft QB if not done. Lock in WR/RB depth.",
    range(10, 13): "Fill roster holes — backup RB, WR3, second TE.",
    range(13, 17): "K and DEF in final rounds. Handcuff high-value RBs you own.",
}


def _round_advice(round_num: int) -> str:
    for r, advice in ROUND_ADVICE.items():
        if round_num in r:
            return advice
    return "Best player available."


def build_rankings(
    config: LeagueConfig,
    changes_path: str = "data/offseason_changes.yaml",
) -> pd.DataFrame:
    """Build composite draft rankings from historical stats, ADP, injuries, and offseason changes."""
    print("📊 Loading historical scores (2023–2025)...")
    hist = get_historical_scores(scoring=config.scoring)

    print("📡 Fetching ADP data...")
    adp_data = fetch_adp(scoring=config.scoring, teams=config.teams)

    print("🏥 Fetching injury reports...")
    injuries = fetch_injuries()

    changes = load_offseason_changes(changes_path)

    total_picks = config.teams * config.rounds

    rows = []
    for _, row in hist.iterrows():
        name = row["player_display_name"]
        pos = str(row.get("position", "UNK")).upper()
        team = str(row.get("team", "UNK"))
        hist_score = float(row["hist_score"])

        adp_info = adp_data.get(name, {})
        adp = adp_info.get("adp", total_picks + 50)
        # Convert ADP to 0–100 score (lower ADP = higher value)
        adp_score = max(0.0, (total_picks - adp + 1) / total_picks * 100) if adp <= total_picks else 0.0

        inj_status_raw = injuries.get(name, "")
        # Only flag statuses that actually affect availability
        inj_status = inj_status_raw if inj_status_raw in INJURY_PENALTIES else ""
        inj_penalty = INJURY_PENALTIES.get(inj_status, 0.0)

        change = changes.get(name, {})
        multiplier = float(change.get("multiplier", 1.0))
        note = change.get("note", "")

        composite = (hist_score * 0.60 + adp_score * 0.30 + inj_penalty) * multiplier

        suggested_round = max(1, min(round(adp / config.teams), config.rounds)) if adp <= total_picks else config.rounds

        rows.append({
            "name": name,
            "position": pos,
            "team": team,
            "hist_score": round(hist_score, 1),
            "adp": round(adp, 1) if adp <= total_picks else None,
            "adp_score": round(adp_score, 1),
            "injury": inj_status or None,
            "multiplier": multiplier,
            "note": note or None,
            "composite": round(composite, 1),
            "suggested_round": suggested_round,
        })

    df = pd.DataFrame(rows)
    df = df[df["position"].isin(["QB", "RB", "WR", "TE", "K", "DEF"])]
    df = df.sort_values("composite", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df


def get_round_targets(round_num: int, config: LeagueConfig) -> list:
    """Return positions to target and draft advice for a given round."""
    targets = [pos for pos, rounds in POSITIONAL_SCARCITY.items() if round_num in rounds]
    advice = _round_advice(round_num)
    return targets or ["WR", "RB", "FLEX"], advice
