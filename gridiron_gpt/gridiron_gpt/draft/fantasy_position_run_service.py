from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class PositionRunResult:
    level: str
    position: str | None
    position_count: int
    window_size: int
    reason: str


class FantasyPositionRunService:
    """Detect short-term positional concentration in recent draft picks."""

    def __init__(self, *, window_size: int = 6) -> None:
        if window_size < 3:
            raise ValueError("window_size must be at least 3")
        self.window_size = int(window_size)

    def evaluate(self, picks: list[object]) -> PositionRunResult:
        recent = list(picks)[-self.window_size :]
        if len(recent) < 3:
            return PositionRunResult(
                level="none",
                position=None,
                position_count=0,
                window_size=len(recent),
                reason="No positional run: insufficient recent draft history.",
            )

        positions = [
            str(getattr(pick, "position", "")).strip().upper()
            for pick in recent
            if str(getattr(pick, "position", "")).strip()
        ]
        if not positions:
            return PositionRunResult(
                level="none",
                position=None,
                position_count=0,
                window_size=len(recent),
                reason="No positional run: recent picks have no usable position data.",
            )

        counts = Counter(positions)
        position, count = counts.most_common(1)[0]
        observed_window = len(recent)

        if count >= 4 and observed_window >= 6:
            level = "active"
        elif count >= 3 and observed_window >= 5:
            level = "developing"
        else:
            return PositionRunResult(
                level="none",
                position=None,
                position_count=count,
                window_size=observed_window,
                reason="No positional run: recent selections remain sufficiently distributed.",
            )

        return PositionRunResult(
            level=level,
            position=position,
            position_count=count,
            window_size=observed_window,
            reason=(
                f"{level.capitalize()} {position} run: {count} of the last "
                f"{observed_window} picks were {position}."
            ),
        )
