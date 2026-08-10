import pytest

from gridiron_cortex.confidence.confidence_calibrator import (
    ConfidenceCalibrator,
)


def test_balanced_confidence():
    calibrator = ConfidenceCalibrator()

    result = calibrator.calibrate(
        classifier_confidence=0.90,
        evidence_confidence=0.90,
    )

    assert result.final_confidence == pytest.approx(0.90)


def test_signal_weighted_higher_than_evidence():
    calibrator = ConfidenceCalibrator()

    result = calibrator.calibrate(
        classifier_confidence=0.90,
        evidence_confidence=0.40,
    )

    assert result.final_confidence == pytest.approx(0.70)


def test_evidence_improves_low_classifier_confidence():
    calibrator = ConfidenceCalibrator()

    result = calibrator.calibrate(
        classifier_confidence=0.40,
        evidence_confidence=0.90,
    )

    assert result.final_confidence == pytest.approx(0.60)


def test_clamps_high_values():
    calibrator = ConfidenceCalibrator()

    result = calibrator.calibrate(
        classifier_confidence=1.5,
        evidence_confidence=1.2,
    )

    assert result.final_confidence == 1.0


def test_clamps_negative_values():
    calibrator = ConfidenceCalibrator()

    result = calibrator.calibrate(
        classifier_confidence=-0.5,
        evidence_confidence=-0.3,
    )

    assert result.final_confidence == 0.0
