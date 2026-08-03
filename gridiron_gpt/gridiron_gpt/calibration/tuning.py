from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class ParameterTrial:
    parameters: dict[str, float]
    score: float


@dataclass(frozen=True)
class TuningResult:
    best_parameters: dict[str, float]
    best_score: float
    trials: tuple[ParameterTrial, ...]


class GridParameterTuner:
    """Evaluate explicit parameter candidates without mutating production settings."""

    def tune(
        self,
        candidates: Iterable[dict[str, float]],
        evaluate: Callable[[dict[str, float]], float],
        *,
        minimize: bool = True,
    ) -> TuningResult:
        trials = tuple(
            ParameterTrial(dict(parameters), float(evaluate(dict(parameters))))
            for parameters in candidates
        )
        if not trials:
            raise ValueError("at least one parameter candidate is required")
        best = min(trials, key=lambda trial: trial.score) if minimize else max(
            trials, key=lambda trial: trial.score
        )
        return TuningResult(dict(best.parameters), best.score, trials)
