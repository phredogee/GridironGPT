from collections import defaultdict
from datetime import date, datetime
from gridiron_gpt.data_ingest.news_loader import load_news
from gridiron_gpt.data_ingest.injury_loader import load_injuries
from gridiron_gpt.data_ingest.roster_loader import load_roster_moves
from gridiron_gpt.data_ingest.player_catalog import load_player_catalog
from gridiron_gpt.intelligence.signal_impact_api import generate_signal_impacts
from gridiron_gpt.intelligence.signal_decay import (
    apply_signal_decay,
    decay_weight,
)

IMPACT_SCORES = {
    "positive": 1.0,
    "neutral": 0.0,
    "unknown": 0.0,
    "monitor": -0.5,
    "negative": -1.0,
}

def recency_weight(signal_date: str) -> float:
    try:
        event_date = datetime.fromisoformat(signal_date).date()
    except Exception:
        return 1.0

    days_old = (date.today() - event_date).days

    if days_old <= 1:
        return 1.0

    if days_old <= 7:
        return 0.85

    if days_old <= 14:
        return 0.65

    if days_old <= 30:
        return 0.40

    return 0.20

def recommendation_from_score(score: float) -> str:
    if score >= 2:
        return "BUY"

    if score > 0:
        return "WATCH"

    if score == 0:
        return "HOLD"

    if score > -1:
        return "MONITOR"

    return "SELL"

def confidence_from_signals(signals: list[dict]) -> int:
    if not signals:
        return 0

    positive = sum(
        1 for signal in signals
        if signal["value"] > 0
    )

    negative = sum(
        1 for signal in signals
        if signal["value"] < 0
    )

    total = len(signals)

    agreement = max(positive, negative) / total

    confidence = 50 + int(agreement * 50)

    return min(confidence, 99)

def _position_lookup() -> dict[str, str]:
    catalog = load_player_catalog()

    positions = {
        item["player"]: item.get("position", "UNK")
        for item in catalog
    }

    positions.update({
        "Tank Dell": "WR",
        "Joe Mixon": "RB",
        "Christian Watson": "WR",
    })

    return positions

def _add_signal(scores, item, source):
    player = item.get("player", "Unknown")
    team = item.get("team", "UNK")

    if player == "Unknown":
        return

    impact = item.get("fantasy_impact", "unknown").lower()
    base_value = IMPACT_SCORES.get(impact, 0.0)
    signal_date = item.get("date", date.today().isoformat())
    weight = decay_weight(signal_date)
    value = apply_signal_decay(base_value, signal_date)

    key = (player, team)
    headline = item.get("headline", "No headline")

    existing_headlines = {
        signal["headline"]
        for signal in scores[key]["signals"]
    }

    if headline in existing_headlines:
        return

    scores[key]["score"] += value
    scores[key]["signals"].append({
        "source": source,
        "headline": headline,
        "impact": impact,
        "value": value,
        "date": signal_date,
        "base_value": base_value,
        "weight": weight,
    })

def calculate_player_scores():
    scores = defaultdict(lambda: {"score": 0.0, "signals": []})

    for item in load_news():
        _add_signal(scores, item, "News")

    for item in load_injuries():
        _add_signal(scores, item, "Injury")

    for item in load_roster_moves():
        _add_signal(scores, item, "Roster")

    return scores


def build_draft_watch_report() -> str:
    scores = calculate_player_scores()

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1]["score"],
        reverse=True,
    )

    risers = [(key, data) for key, data in ranked if data["score"] > 0]
    fallers = [(key, data) for key, data in ranked if data["score"] < 0]

    lines = []
    lines.append("📈 DRAFT WATCH")
    lines.append("")

    lines.append("🔥 Biggest Risers")
    if risers:
        for (player, team), data in risers[:10]:
            rating = recommendation_from_score(data["score"])

            confidence = confidence_from_signals(data["signals"])
            
            lines.append(
                f"{player} ({team}) — "
                f"Score: {data['score']:+.1f} "
                f"[{rating}; {confidence}%]"
            )

            for signal in data["signals"][:3]:
                if signal["value"] > 0:
                    lines.append(f"+ {signal['headline']} [{signal['source']}]")
            lines.append("")
    else:
        lines.append("- No risers found.")
        lines.append("")

    lines.append("⚠ Biggest Concerns")
    if fallers:
        for (player, team), data in fallers[:10]:
            lines.append(f"{player} ({team}) — Score: {data['score']:+.1f}")
            for signal in data["signals"][:3]:
                if signal["value"] < 0:
                    lines.append(f"- {signal['headline']} [{signal['source']}]")
            lines.append("")
    else:
        lines.append("- No concerns found.")

    return "\n".join(lines).strip()

def build_player_scorecard(player_name: str) -> str:
    scores = calculate_player_scores()

    matched_key = None
    matched_data = None

    for (player, team), data in scores.items():
        if player_name.lower() in player.lower():
            matched_key = (player, team)
            matched_data = data
            break

    if not matched_key or not matched_data:
        return f"No scorecard found for {player_name}."

    player, team = matched_key
    score = matched_data["score"]
    signals = matched_data["signals"]

    recommendation = recommendation_from_score(score)

    lines = []
    lines.append(f"🏈 {player} Scorecard")
    lines.append("")
    lines.append(f"Team: {team}")
    confidence = confidence_from_signals(data["signals"])

    lines.append(f"Current Score: {score:+.1f}")
    lines.append(f"Recommendation: {recommendation}")
    lines.append(f"Confidence: {confidence}%")

    lines.append("")
    lines.append("Signals")

    for signal in sorted(signals, key=lambda s: s["value"], reverse=True):
        value = signal["value"]
        prefix = "+" if value > 0 else ""
        lines.append(
            f"{prefix}{value:.2f}  {signal['headline']} "
            f"[{signal['source']}; Impact: {signal['impact']}; "
            f"Weight: {signal.get('weight', 1.0):.2f}]"
        )

    return "\n".join(lines)

def build_signal_rankings(
    limit: int = 25,
    team_filter: str | None = None,
    position_filter: str | None = None,
    recommendation_filter: str | None = None,
) -> str:
    scores = calculate_player_scores()

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1]["score"],
        reverse=True,
    )

    ranked = [
        ((player, team), data)
        for (player, team), data in ranked
        if data["score"] != 0
    ]

    if team_filter:
        team_filter = team_filter.upper()
        ranked = [
            ((player, team), data)
            for (player, team), data in ranked
            if team.upper() == team_filter
        ]

    if position_filter:
        position_filter = position_filter.upper()
        positions = _position_lookup()
        ranked = [
            ((player, team), data)
            for (player, team), data in ranked
            if positions.get(player, "UNK").upper() == position_filter
        ]

    lines = []

    title = "🏆 SIGNAL RANKINGS"

    if team_filter:
        title += f" — {team_filter}"

    if position_filter:
        title += f" — {position_filter}"

    if recommendation_filter:
        recommendation_filter = recommendation_filter.upper()
        title += f" — {recommendation_filter}"

        ranked = [
            ((player, team), data)
            for (player, team), data in ranked
            if recommendation_from_score(data["score"]) == recommendation_filter
        ]

    lines.append(title)

    if not ranked:
        lines.append("- No scored players found.")
        return "\n".join(lines)

    for idx, ((player, team), data) in enumerate(ranked[:limit], start=1):
        rating = recommendation_from_score(data["score"])
        confidence = confidence_from_signals(data["signals"])

        lines.append(
            f"{idx}. {player} ({team}) — "
            f"Score: {data['score']:+.1f} "
            f"[{rating}; {confidence}%]"
        )

    return "\n".join(lines)

def adjusted_score_for_player(player: str, score: float) -> tuple[float, list]:
    impact_report = generate_signal_impacts(player, score)

    return (
        impact_report["total_system_impact"],
        impact_report["propagated_impacts"],
    )

def build_recommendations_report(limit: int = 10) -> str:
    scores = calculate_player_scores()

    buckets = {
        "BUY": [],
        "WATCH": [],
        "HOLD": [],
        "MONITOR": [],
        "SELL": [],
    }

    for (player, team), data in scores.items():
        score = data["score"]

        if score == 0:
            continue

        adjusted_score, propagated_impacts = adjusted_score_for_player(
            player,
            score,
        )

        data["base_score"] = score
        data["adjusted_score"] = adjusted_score
        data["propagated_impacts"] = propagated_impacts

        recommendation = recommendation_from_score(adjusted_score)
        buckets[recommendation].append(((player, team), data))

    for recommendation in buckets:
        buckets[recommendation].sort(
            key=lambda item: item[1].get("adjusted_score", item[1]["score"]),
            reverse=True,
        )

    lines = []
    lines.append("🎯 FANTASY RECOMMENDATIONS")
    lines.append("")

    sections = [
        ("🟢 BUY", "BUY"),
        ("🟡 WATCH", "WATCH"),
        ("⚪ HOLD", "HOLD"),
        ("🟠 MONITOR", "MONITOR"),
        ("🔴 SELL", "SELL"),
    ]

    for title, key in sections:
        lines.append(title)

        players = buckets[key][:limit]

        if players:
            for (player, team), data in players:
                confidence = confidence_from_signals(data["signals"])

                base_score = data.get("base_score", data["score"])
                adjusted_score = data.get("adjusted_score", data["score"])
                propagated_count = len(data.get("propagated_impacts", []))

                if propagated_count:
                    lines.append(
                        f"- {player} ({team}) — "
                        f"Score: {adjusted_score:+.1f} "
                        f"(base {base_score:+.1f}, "
                        f"{propagated_count} related impacts, "
                        f"{confidence}%)"
                    )
                else:
                    lines.append(
                        f"- {player} ({team}) — "
                        f"Score: {adjusted_score:+.1f} "
                        f"({confidence}%)"
                    )
        else:
            lines.append("- None")

        lines.append("")

    return "\n".join(lines).strip()
