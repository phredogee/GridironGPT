from gridiron_gpt.data_ingest.player_scores import calculate_player_scores


def build_fallers_report() -> str:
    scores = calculate_player_scores()

    fallers = sorted(
        [
            ((player, team), data)
            for (player, team), data in scores.items()
            if data["score"] < 0
        ],
        key=lambda item: item[1]["score"],
    )

    lines = []
    lines.append("⬇ CAMP FALLERS")
    lines.append("")

    if not fallers:
        lines.append("- No camp fallers found.")
        return "\n".join(lines)

    for (player, team), data in fallers[:10]:
        lines.append(f"{player} ({team}) — Score: {data['score']:+.1f}")

        negative_signals = [
            signal for signal in data["signals"]
            if signal["value"] < 0
        ]

        for signal in negative_signals[:3]:
            lines.append(f"- {signal['headline']} [{signal['source']}]")

        lines.append("Draft Outlook: Risk increasing. Monitor closely before moving up draft boards.")
        lines.append("")

    return "\n".join(lines).strip()
