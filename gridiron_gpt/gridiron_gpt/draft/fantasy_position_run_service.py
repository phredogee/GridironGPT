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
            if getattr(pick, "position", None)
            and str(getattr(pick, "position", "")).strip()
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
        leaders = counts.most_common()
        position, count = leaders[0]
        if len(leaders) > 1 and leaders[1][1] == count:
            return PositionRunResult(
                level="none",
                position=None,
                position_count=count,
                window_size=len(recent),
                reason="No positional run: recent position leaders are tied.",
            )

        observed_window = len(recent)
        concentration = count / observed_window

        # A run is about concentration, not an absolute pick count. Four of five
        # is stronger than four of seven, while the original 4-of-6 contract
        # remains an active run.
        if count >= 4 and concentration >= (2 / 3):
            level = "active"
        elif count >= 3 and concentration >= 0.5:
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
