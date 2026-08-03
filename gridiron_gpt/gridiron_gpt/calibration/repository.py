from __future__ import annotations

import json
from pathlib import Path

from gridiron_gpt.calibration.models import OutcomeRecord, PredictionRecord


class JsonlCalibrationRepository:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.predictions_path = self.root / "predictions.jsonl"
        self.outcomes_path = self.root / "outcomes.jsonl"

    def save_prediction(self, prediction: PredictionRecord) -> bool:
        if self.get_prediction(prediction.prediction_id) is not None:
            return False
        self._append(self.predictions_path, prediction.to_dict())
        return True

    def save_outcome(self, outcome: OutcomeRecord) -> bool:
        if self.get_outcome(outcome.prediction_id) is not None:
            return False
        self._append(self.outcomes_path, outcome.to_dict())
        return True

    def predictions(self) -> list[PredictionRecord]:
        return [PredictionRecord.from_dict(item) for item in self._read(self.predictions_path)]

    def outcomes(self) -> list[OutcomeRecord]:
        return [OutcomeRecord.from_dict(item) for item in self._read(self.outcomes_path)]

    def get_prediction(self, prediction_id: str) -> PredictionRecord | None:
        return next((item for item in self.predictions() if item.prediction_id == prediction_id), None)

    def get_outcome(self, prediction_id: str) -> OutcomeRecord | None:
        return next((item for item in self.outcomes() if item.prediction_id == prediction_id), None)

    def paired(self) -> list[tuple[PredictionRecord, OutcomeRecord]]:
        outcomes = {item.prediction_id: item for item in self.outcomes()}
        return [
            (prediction, outcomes[prediction.prediction_id])
            for prediction in self.predictions()
            if prediction.prediction_id in outcomes
        ]

    @staticmethod
    def _append(path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")

    @staticmethod
    def _read(path: Path) -> list[dict]:
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
