from gridiron_gpt.data_ingest.player_scores import calculate_player_scores


def build_risers_report() -> str:
    scores = calculate_player_scores()

    risers = sorted(
        [
            ((player, team), data)
            for (player, team), data in scores.items()
            if data["score"] > 0
        ],
        key=lambda item: item[1]["score"],
        reverse=True,
    )

    lines = []
    lines.append("⬆ CAMP RISERS")
    lines.append("")

    if not risers:
        lines.append("- No camp risers found.")
        return "\n".join(lines)

    for (player, team), data in risers[:10]:
        lines.append(f"{player} ({team}) — Score: {data['score']:+.1f}")

        positive_signals = [
            signal for signal in data["signals"]
            if signal["value"] > 0
        ]

        for signal in positive_signals[:3]:
            lines.append(f"+ {signal['headline']} [{signal['source']}]")

        lines.append("Draft Outlook: Trending up. Monitor for repeated positive reports.")
        lines.append("")

    return "\n".join(lines).strip()
