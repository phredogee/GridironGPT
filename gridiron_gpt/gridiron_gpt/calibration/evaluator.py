from __future__ import annotations

from collections import defaultdict
from statistics import mean

from gridiron_gpt.calibration.models import (
    CalibrationBin,
    EvaluationRecord,
    OutcomeDirection,
    OutcomeRecord,
    PredictionRecord,
    QualityReport,
)


class PredictionEvaluator:
    def evaluate(self, prediction: PredictionRecord, outcome: OutcomeRecord) -> EvaluationRecord:
        if prediction.prediction_id != outcome.prediction_id:
            raise ValueError("prediction and outcome IDs must match")
        correct = prediction.direction == outcome.direction
        probability_correct = prediction.confidence
        brier = (probability_correct - (1.0 if correct else 0.0)) ** 2
        return EvaluationRecord(prediction, outcome, correct, brier)

    def report(self, pairs: list[tuple[PredictionRecord, OutcomeRecord]], bins: int = 10) -> QualityReport:
        if bins <= 0:
            raise ValueError("bins must be positive")
        evaluations = [self.evaluate(prediction, outcome) for prediction, outcome in pairs]
        if not evaluations:
            return QualityReport(0, 0.0, 0.0, (), {}, {}, {})
        return QualityReport(
            count=len(evaluations),
            accuracy=mean(float(item.correct) for item in evaluations),
            mean_brier_score=mean(item.brier_score for item in evaluations),
            bins=self._bins(evaluations, bins),
            by_signal_type=self._group(evaluations, lambda item: (item.prediction.signal_type,)),
            by_source=self._group(evaluations, lambda item: item.prediction.sources),
            by_relationship_type=self._group(
                evaluations, lambda item: item.prediction.relationship_types
            ),
        )

    @staticmethod
    def _bins(evaluations: list[EvaluationRecord], bins: int) -> tuple[CalibrationBin, ...]:
        grouped: list[list[EvaluationRecord]] = [[] for _ in range(bins)]
        for item in evaluations:
            index = min(bins - 1, int(item.prediction.confidence * bins))
            grouped[index].append(item)
        output = []
        for index, items in enumerate(grouped):
            if not items:
                continue
            confidence = mean(item.prediction.confidence for item in items)
            accuracy = mean(float(item.correct) for item in items)
            output.append(
                CalibrationBin(
                    lower=index / bins,
                    upper=(index + 1) / bins,
                    count=len(items),
                    mean_confidence=confidence,
                    accuracy=accuracy,
                    calibration_error=abs(confidence - accuracy),
                )
            )
        return tuple(output)

    @staticmethod
    def _group(evaluations, keys):
        grouped = defaultdict(list)
        for item in evaluations:
            for key in keys(item):
                if key:
                    grouped[key].append(item)
        return {
            key: {
                "count": len(items),
                "accuracy": mean(float(item.correct) for item in items),
                "mean_brier_score": mean(item.brier_score for item in items),
            }
            for key, items in sorted(grouped.items())
        }


class OutcomeDirectionService:
    """Convert a measured change into a stable directional outcome."""

    def classify(self, delta: float, neutral_band: float = 0.0) -> OutcomeDirection:
        if neutral_band < 0:
            raise ValueError("neutral_band must be non-negative")
        if delta > neutral_band:
            return OutcomeDirection.POSITIVE
        if delta < -neutral_band:
            return OutcomeDirection.NEGATIVE
        return OutcomeDirection.NEUTRAL
