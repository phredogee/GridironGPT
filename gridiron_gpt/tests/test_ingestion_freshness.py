from datetime import datetime, timedelta, timezone

import pytest

from gridiron_gpt.ingestion.freshness import evaluate_ingestion_freshness


NOW = datetime(2026, 8, 22, 15, 0, tzinfo=timezone.utc)


def _run(completed_at, *, success=True):
    return {"completed_at": completed_at, "success": success}


def test_no_history_is_reported_as_missing():
    result = evaluate_ingestion_freshness([], now=NOW)

    assert result.status == "missing"
    assert result.label == "No ingestion history"
    assert result.completed_at is None


def test_successful_daily_run_is_fresh_for_scheduler_drift_window():
    result = evaluate_ingestion_freshness(
        [_run("2026-08-21T14:30:00+00:00")],
        now=NOW,
    )

    assert result.is_fresh is True
    assert result.label == "Updated today"
    assert result.age == timedelta(hours=24, minutes=30)


def test_successful_run_older_than_daily_window_is_stale():
    result = evaluate_ingestion_freshness(
        [_run("2026-08-21T12:00:00+00:00")],
        now=NOW,
    )

    assert result.status == "stale"
    assert result.is_fresh is False


def test_failed_latest_run_requires_attention_even_when_recent():
    result = evaluate_ingestion_freshness(
        [_run("2026-08-22T14:45:00+00:00", success=False)],
        now=NOW,
    )

    assert result.status == "failed"
    assert result.label == "Latest ingestion needs attention"
    assert result.run_success is False


def test_latest_run_is_selected_by_completion_time_not_input_order():
    result = evaluate_ingestion_freshness(
        [
            _run("2026-08-22T14:00:00+00:00", success=True),
            _run("2026-08-20T14:00:00+00:00", success=False),
        ],
        now=NOW,
    )

    assert result.status == "fresh"
    assert result.completed_at == datetime(2026, 8, 22, 14, 0, tzinfo=timezone.utc)


def test_naive_timestamp_is_interpreted_as_utc():
    result = evaluate_ingestion_freshness(
        [_run("2026-08-22T14:00:00")],
        now=NOW,
    )

    assert result.status == "fresh"
    assert result.completed_at.tzinfo == timezone.utc


def test_invalid_timestamp_is_ignored():
    result = evaluate_ingestion_freshness(
        [_run("not-a-date")],
        now=NOW,
    )

    assert result.status == "missing"


def test_non_positive_freshness_window_is_rejected():
    with pytest.raises(ValueError, match="fresh_for must be positive"):
        evaluate_ingestion_freshness([], now=NOW, fresh_for=timedelta(0))
