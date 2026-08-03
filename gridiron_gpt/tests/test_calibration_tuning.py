import pytest

from gridiron_gpt.calibration.tuning import GridParameterTuner


def test_tuner_selects_lowest_score_by_default():
    result = GridParameterTuner().tune(
        [{"weight": 0.2}, {"weight": 0.5}, {"weight": 0.8}],
        lambda parameters: abs(parameters["weight"] - 0.5),
    )

    assert result.best_parameters == {"weight": 0.5}
    assert result.best_score == 0.0
    assert len(result.trials) == 3


def test_tuner_can_maximize_metric():
    result = GridParameterTuner().tune(
        [{"threshold": 0.1}, {"threshold": 0.3}],
        lambda parameters: parameters["threshold"],
        minimize=False,
    )

    assert result.best_parameters == {"threshold": 0.3}


def test_tuner_does_not_mutate_input_candidates():
    candidates = [{"weight": 0.4}]

    result = GridParameterTuner().tune(
        candidates,
        lambda parameters: parameters.update(weight=0.9) or 1.0,
    )

    assert candidates == [{"weight": 0.4}]
    assert result.trials[0].parameters == {"weight": 0.4}


def test_empty_candidate_set_is_rejected():
    with pytest.raises(ValueError, match="at least one"):
        GridParameterTuner().tune([], lambda parameters: 0.0)
