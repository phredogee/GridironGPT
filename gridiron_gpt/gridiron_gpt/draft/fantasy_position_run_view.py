from __future__ import annotations

from dataclasses import dataclass

from gridiron_gpt.draft.fantasy_position_run_service import PositionRunResult


@dataclass(frozen=True)
class PositionRunDisplay:
    level: str
    headline: str
    detail: str
    guidance: str


def build_position_run_display(
    result: PositionRunResult,
) -> PositionRunDisplay | None:
    """Build advisory-only copy for a meaningful positional run."""

    if result.level not in {"active", "developing"} or not result.position:
        return None

    guidance = (
        f"Market momentum is increasing pressure at {result.position}."
        if result.level == "active"
        else "A positional run may be forming."
    )
    return PositionRunDisplay(
        level=result.level,
        headline=f"{result.level.upper()} {result.position} RUN",
        detail=(
            f"{result.position_count} of the last {result.window_size} picks "
            f"were {result.position}."
        ),
        guidance=guidance,
    )
