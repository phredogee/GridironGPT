from datetime import datetime, timedelta, timezone

import pytest

from gridiron_gpt.calibration.evaluator import OutcomeDirectionService, PredictionEvaluator
from gridiron_gpt.calibration.models import OutcomeDirection, OutcomeRecord, PredictionRecord
from gridiron_gpt.calibration.replay import HistoricalReplayRunner
from gridiron_gpt.calibration.repository import JsonlCalibrationRepository


NOW = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)


def prediction(identifier="p1", direction=OutcomeDirection.POSITIVE, confidence=0.8, **overrides):
    values = {
        "prediction_id": identifier,
        "player_id": "bijan",
        "player_name": "Bijan Robinson",
        "predicted_at": NOW,
        "horizon": "next_game",
        "direction": direction,
        "confidence": confidence,
        "signal_type": "usage_trend",
        "sources": ("nflverse",),
        "relationship_types": ("backs_up",),
    }
    values.update(overrides)
    return PredictionRecord(**values)


def outcome(identifier="p1", direction=OutcomeDirection.POSITIVE):
    return OutcomeRecord(identifier, NOW + timedelta(days=7), direction, value=5.0)


def test_prediction_round_trips():
    original = prediction()
    assert PredictionRecord.from_dict(original.to_dict()) == original


def test_repository_persists_and_pairs_records(tmp_path):
    repo = JsonlCalibrationRepository(tmp_path)
    assert repo.save_prediction(prediction()) is True
    assert repo.save_outcome(outcome()) is True
    assert len(repo.paired()) == 1


def test_repository_suppresses_duplicate_ids(tmp_path):
    repo = JsonlCalibrationRepository(tmp_path)
    assert repo.save_prediction(prediction()) is True
    assert repo.save_prediction(prediction()) is False
    assert repo.save_outcome(outcome()) is True
    assert repo.save_outcome(outcome(direction=OutcomeDirection.NEGATIVE)) is False


def test_correct_prediction_has_low_brier_score():
    result = PredictionEvaluator().evaluate(prediction(confidence=0.9), outcome())
    assert result.correct is True
    assert result.brier_score == pytest.approx(0.01)


def test_incorrect_confident_prediction_is_penalized():
    result = PredictionEvaluator().evaluate(
        prediction(confidence=0.9), outcome(direction=OutcomeDirection.NEGATIVE)
    )
    assert result.correct is False
    assert result.brier_score == pytest.approx(0.81)


def test_report_calculates_accuracy_and_confidence_bins():
    pairs = [
        (prediction("p1", confidence=0.8), outcome("p1")),
        (prediction("p2", confidence=0.8), outcome("p2", OutcomeDirection.NEGATIVE)),
    ]
    report = PredictionEvaluator().report(pairs, bins=5)
    assert report.count == 2
    assert report.accuracy == 0.5
    assert report.bins[0].count == 2
    assert report.bins[0].calibration_error == pytest.approx(0.3)


def test_report_measures_signal_source_and_relationship_quality():
    report = PredictionEvaluator().report([(prediction(), outcome())])
    assert report.by_signal_type["usage_trend"]["accuracy"] == 1.0
    assert report.by_source["nflverse"]["count"] == 1
    assert report.by_relationship_type["backs_up"]["count"] == 1


def test_empty_report_is_valid():
    report = PredictionEvaluator().report([])
    assert report.count == 0
    assert report.bins == ()


def test_outcome_direction_uses_neutral_band():
    service = OutcomeDirectionService()
    assert service.classify(0.2, 0.1) == OutcomeDirection.POSITIVE
    assert service.classify(-0.2, 0.1) == OutcomeDirection.NEGATIVE
    assert service.classify(0.05, 0.1) == OutcomeDirection.NEUTRAL


def test_replay_never_exposes_future_evidence():
    evidence = [
        {"at": NOW + timedelta(days=2), "value": 3},
        {"at": NOW, "value": 1},
        {"at": NOW + timedelta(days=1), "value": 2},
    ]
    histories = []

    def predict(item, history):
        histories.append([prior["value"] for prior in history])
        return [item["value"]]

    result = HistoricalReplayRunner().run(
        evidence, timestamp=lambda item: item["at"], predict=predict
    )
    assert histories == [[], [1], [1, 2]]
    assert result.predictions == (1, 2, 3)


def test_naive_replay_timestamp_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        HistoricalReplayRunner().run(
            [{"at": datetime(2026, 1, 1)}],
            timestamp=lambda item: item["at"],
            predict=lambda item, history: [],
        )


def test_invalid_confidence_is_rejected():
    with pytest.raises(ValueError, match="confidence"):
        prediction(confidence=1.1)
