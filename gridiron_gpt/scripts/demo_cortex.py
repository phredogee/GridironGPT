"""
GRIDIRON CORTEX Intelligence Demo

Runs the complete statistical intelligence pipeline and feeds
high-confidence events into Cortex.
"""
from pathlib import Path
import sys
from collections import Counter
from gridiron_cortex.facade import CortexFacade
from gridiron_gpt.data_ingest.nflreadpy_adapter import (
    fetch_nflverse_snapshot,
)
from gridiron_gpt.data_ingest.nflverse_normalizer import (
    normalize_snapshot,
)
from gridiron_gpt.intelligence.nflverse_signal_factory import (
    generate_weekly_signals,
    generate_rolling_baseline_signals,
)
from gridiron_gpt.intelligence.signal_aggregator import (
    aggregate_signals,
)
from gridiron_gpt.intelligence.aggregated_signal_adapter import (
    aggregates_to_events,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def main():

    print("=" * 72)
    print(" GRIDIRON CORTEX")
    print(" Statistical Intelligence Demonstration")
    print("=" * 72)

    snapshot = fetch_nflverse_snapshot(2025)

    normalized = normalize_snapshot(snapshot)

    records = normalized["weekly_player_stats"]

    weekly = generate_weekly_signals(records)

    rolling = generate_rolling_baseline_signals(records)

    aggregates = aggregate_signals(
        weekly,
        rolling,
    )

    print()

    print(f"Weekly signals............. {len(weekly):>6}")
    print(f"Rolling signals............ {len(rolling):>6}")
    print(f"Aggregated trends.......... {len(aggregates):>6}")

    print()

    print(
        Counter(
            trend["trend_classification"]
            for trend in aggregates
        )
    )

    print()

    print("=" * 72)
    print("Top 25 Statistical Trends")
    print("=" * 72)


    def trend_rank(trend):
        classification_weight = {
            "sustained": 1.00,
            "confirmed": 0.90,
            "emerging": 0.50,
            "volatile": 0.20,
        }

        return (
            classification_weight.get(
                trend["trend_classification"],
                0.0,
            )
            * trend["confidence"]
            * abs(trend["impact_score"])
        )

    actionable = [
        trend
        for trend in aggregates
        if trend["trend_classification"]
        in {"confirmed", "sustained"}
        and trend["confidence"] >= 0.85
        and abs(trend["impact_score"]) >= 0.20
    ]

    top = sorted(
        actionable,
        key=trend_rank,
        reverse=True,
    )[:25]

    for trend in top:

        print()

        print(
            f"{trend['player_name']} ({trend['team']})"
        )

        print(
            f"Metric: {trend['metric']}"
        )

        print(
            f"Classification: {trend['trend_classification']}"
        )

        print(
            f"Impact: {trend['impact_score']:+.3f}"
        )

        print(
            f"Confidence: {trend['confidence']:.3f}"
        )

        print(
            f"Evidence: {trend['evidence_count']}"
        )

        for reason in trend["reasons"][:2]:
            print(f" • {reason}")

    print()

    print("=" * 72)
    print("Cortex Processing")
    print("=" * 72)

    events = aggregates_to_events(top)

    demo_directory = Path("data/cortex_nflverse_demo")
    demo_directory.mkdir(parents=True, exist_ok=True)

    cortex = CortexFacade(
        data_directory=demo_directory,
    )

    processed = 0
    duplicates = 0
    errors = []

    for trend, event in zip(top, events):
        try:
            result = cortex.process_event(event)
        except Exception as exc:
            errors.append(
                {
                    "player": trend["player_name"],
                    "metric": trend["metric"],
                    "error": str(exc),
                }
            )
            continue

        if result.explanation == "Duplicate event ignored.":
            duplicates += 1
            continue

        processed += 1

        print()
        print("-" * 72)
        print(
            f"{trend['player_name']} "
            f"({trend.get('team') or 'Unknown'})"
        )
        print("-" * 72)

        print(
            f"Trend: {trend['trend_classification']} "
            f"{trend['signal_type']}"
        )
        print(f"Metric: {trend['metric']}")
        print(f"Direction: {trend['direction']}")
        print(f"Aggregate impact: {trend['impact_score']:+.3f}")
        print(f"Aggregate confidence: {trend['confidence']:.3f}")

        print("\nRawEvent:")
        print(event)

        print("\nCortex Signal:")
        print(result.signal)

        print("\nScore Updates:")
        if result.score_updates:
            for update in result.score_updates:
                print(f"  {update}")
        else:
            print("  None")

        print("\nRecommendations:")
        if result.recommendations:
            for recommendation in result.recommendations:
                print(f"  {recommendation}")
        else:
            print("  None")

        print("\nExplanation:")
        print(result.explanation)

    print()
    print("=" * 72)
    print("Cortex Run Summary")
    print("=" * 72)
    print(f"Events generated:  {len(events)}")
    print(f"Events processed:  {processed}")
    print(f"Duplicates:        {duplicates}")
    print(f"Errors:            {len(errors)}")

    if errors:
        print("\nErrors:")

        for error in errors:
            print(
                f"  {error['player']} / "
                f"{error['metric']}: "
                f"{error['error']}"
            )

if __name__ == "__main__":
    main()
