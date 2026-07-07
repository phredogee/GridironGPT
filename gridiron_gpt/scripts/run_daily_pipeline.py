from pathlib import Path
from dotenv import load_dotenv

from gridiron_gpt.data_ingest.rss_news_fetcher import fetch_and_persist_from_env
from gridiron_gpt.intelligence.score_snapshot_service import snapshot_current_player_scores
from gridiron_gpt.intelligence.trend_report import build_trend_report
from gridiron_gpt.intelligence.momentum_engine import format_momentum_report
from gridiron_gpt.data_ingest.injury_loader import load_injuries
from gridiron_gpt.data_ingest.injury_persistence import persist_injury_items

def main() -> None:
    load_dotenv(Path(".env"))

    print("🏈 Running GridironGPT daily pipeline...")
    print()

    ingestion_result = fetch_and_persist_from_env()
    print("RSS Ingestion:")
    print(ingestion_result)
    print()

    injury_items = load_injuries()
    injury_result = persist_injury_items(injury_items)

    print("Injury Persistence:")
    print({
        "injuries_loaded": len(injury_items),
        **injury_result,
    })
    print()

    snapshot_result = snapshot_current_player_scores()
    print("Score Snapshots:")
    print(snapshot_result)
    print()

    print(build_trend_report(limit=10))
    print()
    print(format_momentum_report(limit=10))

if __name__ == "__main__":
    main()
