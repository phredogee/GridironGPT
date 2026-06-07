from gridiron_gpt.data_ingest.player_scores import calculate_player_scores


def _find_player(scores, player_name: str):
    for (player, team), data in scores.items():
        if player_name.lower() in player.lower():
            return player, team, data

    return None, None, None


def _top_signals(data, positive=True, limit=3):
    if not data:
        return []

    if positive:
        signals = [s for s in data["signals"] if s["value"] > 0]
        return sorted(signals, key=lambda s: s["value"], reverse=True)[:limit]

    signals = [s for s in data["signals"] if s["value"] < 0]
    return sorted(signals, key=lambda s: s["value"])[:limit]


def build_player_comparison(player1_name: str, player2_name: str) -> str:
    scores = calculate_player_scores()

    p1, t1, d1 = _find_player(scores, player1_name)
    p2, t2, d2 = _find_player(scores, player2_name)

    if not d1 and not d2:
        return f"No comparison data found for {player1_name} or {player2_name}."

    if not d1:
        return f"No comparison data found for {player1_name}."

    if not d2:
        return f"No comparison data found for {player2_name}."

    s1 = d1["score"]
    s2 = d2["score"]

    if s1 > s2:
        edge = f"{p1} ({t1})"
        recommendation = f"Prefer {p1} based on current camp/news signals."
    elif s2 > s1:
        edge = f"{p2} ({t2})"
        recommendation = f"Prefer {p2} based on current camp/news signals."
    else:
        edge = "Even"
        recommendation = "No clear edge based on current signals."

    lines = []
    lines.append("🏈 Player Comparison")
    lines.append("")
    lines.append(f"{p1} ({t1})")
    lines.append(f"Score: {s1:+.1f}")
    lines.append("")
    lines.append(f"{p2} ({t2})")
    lines.append(f"Score: {s2:+.1f}")
    lines.append("")
    lines.append(f"Edge: {edge}")
    lines.append(f"Recommendation: {recommendation}")
    lines.append("")

    lines.append(f"Why {p1}:")
    p1_positive = _top_signals(d1, positive=True)
    p1_negative = _top_signals(d1, positive=False)

    if p1_positive:
        for signal in p1_positive:
            lines.append(f"+ {signal['headline']} [{signal['source']}]")
    if p1_negative:
        for signal in p1_negative:
            lines.append(f"- {signal['headline']} [{signal['source']}]")
    if not p1_positive and not p1_negative:
        lines.append("- No strong signals found.")

    lines.append("")
    lines.append(f"Why {p2}:")
    p2_positive = _top_signals(d2, positive=True)
    p2_negative = _top_signals(d2, positive=False)

    if p2_positive:
        for signal in p2_positive:
            lines.append(f"+ {signal['headline']} [{signal['source']}]")
    if p2_negative:
        for signal in p2_negative:
            lines.append(f"- {signal['headline']} [{signal['source']}]")
    if not p2_positive and not p2_negative:
        lines.append("- No strong signals found.")

    return "\n".join(lines)
