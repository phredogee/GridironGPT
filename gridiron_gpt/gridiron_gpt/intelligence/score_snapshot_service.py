from gridiron_gpt.data_ingest.player_scores import (
    calculate_player_scores,
    confidence_from_signals,
    recommendation_from_score,
)
from gridiron_gpt.intelligence.signal_impact_api import generate_signal_impacts
from gridiron_gpt.storage.score_snapshot_repository import (
    save_player_score_snapshot,
)


def snapshot_current_player_scores(limit: int | None = None) -> dict:
    scores = calculate_player_scores()

    saved = 0
    skipped = 0

    ranked_scores = sorted(
        scores.items(),
        key=lambda item: item[1]["score"],
        reverse=True,
    )

    if limit is not None:
        ranked_scores = ranked_scores[:limit]

    for (player, team), data in ranked_scores:
        score = data["score"]

        if score == 0:
            skipped += 1
            continue

        impact_report = generate_signal_impacts(player, score)
        adjusted_score = impact_report["total_system_impact"]

        confidence = confidence_from_signals(data["signals"])
        recommendation = recommendation_from_score(adjusted_score)

        save_player_score_snapshot(
            player=player,
            team=team,
            score=score,
            adjusted_score=adjusted_score,
            confidence=confidence,
            recommendation=recommendation,
        )

        saved += 1

    return {
        "saved": saved,
        "skipped": skipped,
    }
