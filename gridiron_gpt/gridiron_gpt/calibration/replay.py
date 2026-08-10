from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Iterable, TypeVar


T = TypeVar("T")
P = TypeVar("P")


@dataclass(frozen=True)
class ReplayFrame:
    as_of: datetime
    evidence_count: int
    prediction_count: int


@dataclass(frozen=True)
class ReplayResult:
    frames: tuple[ReplayFrame, ...]
    predictions: tuple[object, ...]


class HistoricalReplayRunner:
    """Replay timestamped evidence without exposing future records to the predictor."""

    def run(
        self,
        evidence: Iterable[T],
        *,
        timestamp: Callable[[T], datetime],
        predict: Callable[[T, tuple[T, ...]], Iterable[P]],
    ) -> ReplayResult:
        ordered = sorted(evidence, key=timestamp)
        visible: list[T] = []
        predictions: list[P] = []
        frames: list[ReplayFrame] = []

        for item in ordered:
            current_time = timestamp(item)
            if current_time.tzinfo is None:
                raise ValueError("replay timestamps must be timezone-aware")
            history = tuple(visible)
            generated = tuple(predict(item, history))
            predictions.extend(generated)
            visible.append(item)
            frames.append(
                ReplayFrame(
                    as_of=current_time,
                    evidence_count=len(visible),
                    prediction_count=len(generated),
                )
            )

        return ReplayResult(tuple(frames), tuple(predictions))
