from datetime import datetime, timezone

from gridiron_gpt.ingestion.models.provider_health import ProviderHealthStatus
from gridiron_gpt.ingestion.models.provider_ingestion_result import ProviderIngestionResult
from gridiron_gpt.ingestion.services.provider_health_tracker import ProviderHealthTracker


NOW = datetime(2026, 8, 2, 18, 0, tzinfo=timezone.utc)


def tracker():
    return ProviderHealthTracker(clock=lambda: NOW, unavailable_after_failures=3)


def test_first_attempt_success_is_healthy():
    health = tracker().record(ProviderIngestionResult(
        source_name="ESPN NFL", success=True, attempts=1, records_received=31
    ))

    assert health.status == ProviderHealthStatus.HEALTHY
    assert health.total_successes == 1
    assert health.consecutive_failures == 0
    assert health.last_success == NOW
    assert health.last_records_received == 31


def test_recovered_provider_is_degraded():
    health = tracker().record(ProviderIngestionResult(
        source_name="RotoWire NFL", success=True, attempts=2, records_received=5
    ))

    assert health.status == ProviderHealthStatus.DEGRADED
    assert health.total_successes == 1
    assert health.last_attempts == 2


def test_failures_progress_from_degraded_to_unavailable():
    health_tracker = tracker()
    failure = ProviderIngestionResult(
        source_name="RotoWire NFL",
        success=False,
        attempts=3,
        error_type="ProviderTimeoutError",
        error_message="timed out",
    )

    first = health_tracker.record(failure)
    second = health_tracker.record(failure)
    third = health_tracker.record(failure)

    assert first.status == ProviderHealthStatus.DEGRADED
    assert second.status == ProviderHealthStatus.DEGRADED
    assert third.status == ProviderHealthStatus.UNAVAILABLE
    assert third.consecutive_failures == 3
    assert third.total_failures == 3
    assert third.last_error_type == "ProviderTimeoutError"


def test_success_resets_consecutive_failures():
    health_tracker = tracker()
    failure = ProviderIngestionResult(source_name="ESPN NFL", success=False, error_type="ConnectionError")
    health_tracker.record(failure)
    health_tracker.record(failure)

    recovered = health_tracker.record(ProviderIngestionResult(
        source_name="ESPN NFL", success=True, attempts=1, records_received=20
    ))

    assert recovered.status == ProviderHealthStatus.HEALTHY
    assert recovered.consecutive_failures == 0
    assert recovered.total_failures == 2
    assert recovered.total_successes == 1
    assert recovered.last_failure == NOW


def test_tracker_exposes_all_provider_states():
    health_tracker = tracker()
    health_tracker.record(ProviderIngestionResult(source_name="ESPN NFL", success=True))
    health_tracker.record(ProviderIngestionResult(source_name="RotoWire NFL", success=False, error_type="ConnectionError"))

    states = {health.source_name: health for health in health_tracker.all()}

    assert states["ESPN NFL"].status == ProviderHealthStatus.HEALTHY
    assert states["RotoWire NFL"].status == ProviderHealthStatus.DEGRADED


def test_invalid_unavailable_threshold_is_rejected():
    try:
        ProviderHealthTracker(unavailable_after_failures=0)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "unavailable_after_failures" in str(exc)
