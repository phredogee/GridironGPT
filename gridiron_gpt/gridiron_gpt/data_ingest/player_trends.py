from collections import defaultdict

from gridiron_gpt.data_ingest.news_loader import load_news
from gridiron_gpt.data_ingest.injury_loader import load_injuries
from gridiron_gpt.data_ingest.roster_loader import load_roster_moves
from gridiron_gpt.data_ingest.player_scores import IMPACT_SCORES
from gridiron_gpt.data_ingest.player_scores import (
    calculate_player_scores,
    confidence_from_signals,
)

def _matches_player(item: dict, player_name: str) -> bool:
    return player_name.lower() in item.get("player", "").lower()


def _add_daily_signal(daily_scores, item, source):
    player = item.get("player", "Unknown")

    if player == "Unknown":
        return

    date = item.get("date", "unknown date")
    impact = item.get("fantasy_impact", "unknown").lower()
    value = IMPACT_SCORES.get(impact, 0.0)
    headline = item.get("headline", "No headline")

    existing = {
        signal["headline"]
        for signal in daily_scores[date]["signals"]
    }

    if headline in existing:
        return

    daily_scores[date]["score"] += value
    daily_scores[date]["signals"].append({
        "source": source,
        "headline": headline,
        "impact": impact,
        "value": value,
    })


def build_player_trend(player_name: str) -> str:
    daily_scores = defaultdict(lambda: {"score": 0.0, "signals": []})
    seen_headlines = set()

    for item in load_news():
        if _matches_player(item, player_name):
            headline = item.get("headline", "")

            if headline in seen_headlines:
                continue
            seen_headlines.add(headline)

            _add_daily_signal(daily_scores, item, "News")

    for item in load_injuries():
        if _matches_player(item, player_name):
            headline = item.get("headline", "")

            if headline in seen_headlines:
                continue
            seen_headlines.add(headline)

            _add_daily_signal(daily_scores, item, "Injury")

    for item in load_roster_moves():
        if _matches_player(item, player_name):
            headline = item.get("headline", "")

            if headline in seen_headlines:
                continue
            seen_headlines.add(headline)

            _add_daily_signal(daily_scores, item, "Roster")

    if not daily_scores:
        return f"No trend found for {player_name}."

    sorted_days = sorted(daily_scores.items())

    total_score = sum(day["score"] for _, day in sorted_days)
    first_score = sorted_days[0][1]["score"]
    last_score = sorted_days[-1][1]["score"]

    velocity = calculate_velocity(player_name)
    direction = velocity["direction"]

    lines = []
    lines.append(f"🏈 {player_name} Trend")
    lines.append("")
    lines.append(f"Total Score: {total_score:+.1f}")
    lines.append(f"Direction: {direction}")
    lines.append(f"Velocity: {velocity['velocity']:+.2f}/week")
    lines.append(f"Momentum: {velocity['direction']}")
    lines.append("")
    lines.append("Daily Signals")

    for date, data in sorted_days:
        lines.append("")
        lines.append(f"{date} — Score: {data['score']:+.1f}")

        for signal in sorted(data["signals"], key=lambda s: s["value"], reverse=True):
            value = signal["value"]
            prefix = "+" if value > 0 else ""
            lines.append(
                f"{prefix}{value:.1f} {signal['headline']} "
                f"[{signal['source']}; Impact: {signal['impact']}]"
            )

    return "\n".join(lines)

def get_player_trend_points(player_name: str) -> list[dict]:
    daily_scores = defaultdict(lambda: {"score": 0.0, "signals": []})
    seen_headlines = set()

    for item in load_news():
        if _matches_player(item, player_name):
            headline = item.get("headline", "")

            if headline in seen_headlines:
                continue

            seen_headlines.add(headline)
            _add_daily_signal(daily_scores, item, "News")


    for item in load_injuries():
        if _matches_player(item, player_name):
            headline = item.get("headline", "")

            if headline in seen_headlines:
                continue

            seen_headlines.add(headline)
            _add_daily_signal(daily_scores, item, "Injuries")

    for item in load_roster_moves():
        if _matches_player(item, player_name):
            headline = item.get("headline", "")

            if headline in seen_headlines:
                continue
            seen_headlines.add(headline)
            _add_daily_signal(daily_scores, item, "Roster")

    points = []
    cumulative_score = 0.0

    for event_date, data in sorted(daily_scores.items()):
        cumulative_score += data["score"]

        points.append({
            "date": event_date,
            "daily_score": data["score"],
            "cumulative_score": cumulative_score,
            "signal_count": len(data["signals"]),
        })

    return points

def calculate_velocity(player_name: str) -> dict:
    from datetime import datetime

    points = get_player_trend_points(player_name)

    if not points:
        return {
            "velocity": 0.0,
            "direction": "No data",
            "days": 0,
        }

    unique_dates = {point["date"] for point in points}

    if len(unique_dates) == 1:
        return {
            "velocity": 0.0,
            "direction": "Single-day signal",
            "days": 1,
        }

    first = points[0]
    last = points[-1]

    first_date = datetime.fromisoformat(first["date"]).date()
    last_date = datetime.fromisoformat(last["date"]).date()

    days = max(1, (last_date - first_date).days)

    score_change = last["cumulative_score"] - first["cumulative_score"]
    velocity = (score_change / days) * 7

    if velocity > 0.25:
        direction = "Heating up 📈"
    elif velocity < -0.25:
        direction = "Cooling off 📉"
    else:
        direction = "Stable ➖"

    return {
        "velocity": velocity,
        "direction": direction,
        "days": days,
    }

    days = max(1, (last["date"] - first["date"]).days if hasattr(last["date"], "days") else 1)

    # Dates are strings, so calculate days safely.
    from datetime import datetime

    first_date = datetime.fromisoformat(first["date"]).date()
    last_date = datetime.fromisoformat(last["date"]).date()
    days = max(1, (last_date - first_date).days)

    score_change = last["cumulative_score"] - first["cumulative_score"]
    velocity = (score_change / days) * 7

    if velocity > 0.25:
        direction = "Heating up 📈"
    elif velocity < -0.25:
        direction = "Cooling off 📉"
    else:
        direction = "Stable ➖"

    return {
        "velocity": velocity,
        "direction": direction,
        "days": days,
    }

    from gridiron_gpt.data_ingest.player_scores import (
        calculate_player_scores,
        confidence_from_signals,
    )

def build_hot_players_report(limit: int = 10) -> str:
    scores = calculate_player_scores()

    players = []

    for (player, team), data in scores.items():
        velocity = calculate_velocity(player)

        if velocity["velocity"] <= 0:
            continue

        confidence = confidence_from_signals(data["signals"])

        players.append({
            "player": player,
            "team": team,
            "velocity": velocity["velocity"],
            "confidence": confidence,
        })

    players.sort(key=lambda p: p["velocity"], reverse=True)

    lines = ["🔥 HOT PLAYERS", ""]

    if not players:
        lines.append("- No hot players found.")
        return "\n".join(lines)

    for idx, player in enumerate(players[:limit], start=1):
        lines.append(
            f"{idx}. {player['player']} ({player['team']}) "
            f"— Velocity: {player['velocity']:+.2f}/week "
            f"[{player['confidence']}%]"
        )

    return "\n".join(lines)

def build_cold_players_report(limit: int = 10) -> str:
    scores = calculate_player_scores()

    players = []

    for (player, team), data in scores.items():
        velocity = calculate_velocity(player)

        if velocity["velocity"] >= 0:
            continue

        confidence = confidence_from_signals(data["signals"])

        players.append({
            "player": player,
            "team": team,
            "velocity": velocity["velocity"],
            "confidence": confidence,
        })

    players.sort(key=lambda p: p["velocity"])

    lines = ["🧊 COLD PLAYERS", ""]

    if not players:
        lines.append("- No cooling players found.")
        return "\n".join(lines)

    for idx, player in enumerate(players[:limit], start=1):
        lines.append(
            f"{idx}. {player['player']} ({player['team']}) "
            f"— Velocity: {player['velocity']:+.2f}/week "
            f"[{player['confidence']}%]"
        )

    return "\n".join(lines)
