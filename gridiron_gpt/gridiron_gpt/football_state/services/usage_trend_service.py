from __future__ import annotations

from statistics import mean

from gridiron_gpt.football_state.models.usage_state import CanonicalUsageState
from gridiron_gpt.football_state.models.usage_trend import (
    UsageMetricDelta,
    UsageTrendDirection,
    UsageTrendResult,
)


class UsageTrendService:
    """Compare current usage with a recent per-player workload baseline."""

    METRICS = (
        "snap_share",
        "route_participation",
        "carry_share",
        "target_share",
        "carries",
        "targets",
        "red_zone_opportunities",
    )

    SHARE_THRESHOLD = 0.05
    COUNT_THRESHOLDS = {
        "carries": 3.0,
        "targets": 2.0,
        "red_zone_opportunities": 2.0,
    }

    def analyze(
        self,
        current: CanonicalUsageState,
        history: list[CanonicalUsageState],
        *,
        baseline_games: int = 3,
    ) -> UsageTrendResult:
        if baseline_games <= 0:
            raise ValueError("baseline_games must be positive")

        eligible = [
            state
            for state in history
            if state.player_id == current.player_id
            and (state.season, state.week) < (current.season, current.week)
        ]
        eligible.sort(key=lambda state: (state.season, state.week), reverse=True)
        baseline_states = eligible[:baseline_games]

        if not baseline_states:
            return UsageTrendResult(
                player_id=current.player_id,
                player_name=current.player_name,
                direction=UsageTrendDirection.UNKNOWN,
                current=current,
                prior_games=0,
                reason="no prior usage baseline",
            )

        deltas: dict[str, UsageMetricDelta] = {}
        signals: list[int] = []

        for metric in self.METRICS:
            current_value = getattr(current, metric)
            prior_values = [
                getattr(state, metric)
                for state in baseline_states
                if getattr(state, metric) is not None
            ]
            if current_value is None or not prior_values:
                continue

            baseline = mean(prior_values)
            delta = float(current_value) - baseline
            deltas[metric] = UsageMetricDelta(
                metric=metric,
                baseline=baseline,
                current=float(current_value),
                delta=delta,
            )

            threshold = self.COUNT_THRESHOLDS.get(metric, self.SHARE_THRESHOLD)
            if delta >= threshold:
                signals.append(1)
            elif delta <= -threshold:
                signals.append(-1)
            else:
                signals.append(0)

        direction = self._classify(signals)
        return UsageTrendResult(
            player_id=current.player_id,
            player_name=current.player_name,
            direction=direction,
            current=current,
            prior_games=len(baseline_states),
            deltas=deltas,
            reason=self._reason(direction, deltas),
        )

    @staticmethod
    def _classify(signals: list[int]) -> UsageTrendDirection:
        meaningful = [signal for signal in signals if signal != 0]
        if not signals:
            return UsageTrendDirection.UNKNOWN
        if not meaningful:
            return UsageTrendDirection.STABLE
        if all(signal > 0 for signal in meaningful):
            return UsageTrendDirection.RISING
        if all(signal < 0 for signal in meaningful):
            return UsageTrendDirection.FALLING
        return UsageTrendDirection.MIXED

    @staticmethod
    def _reason(direction: UsageTrendDirection, deltas: dict[str, UsageMetricDelta]) -> str:
        if not deltas:
            return "no comparable usage metrics"
        changed = sorted(
            deltas.values(),
            key=lambda item: abs(item.delta),
            reverse=True,
        )[:3]
        details = ", ".join(
            f"{item.metric} {item.delta:+.3f} vs baseline"
            for item in changed
        )
        return f"usage trend {direction.value}: {details}"
