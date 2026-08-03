from apps.streamlit.components.app_shell import NAVIGATION_ITEMS
from apps.streamlit.pages.ingestion_status import _format_timestamp, _status_label


def test_ingestion_page_is_in_navigation():
    assert "Ingestion" in NAVIGATION_ITEMS
    assert NAVIGATION_ITEMS["Ingestion"]["label"] == "Ingestion"


def test_provider_health_labels_are_human_readable():
    assert _status_label("healthy") == "Healthy"
    assert _status_label("degraded") == "Degraded"
    assert _status_label("unavailable") == "Unavailable"


def test_ingestion_timestamp_formatting():
    assert (
        _format_timestamp("2026-08-03T15:20:30+00:00")
        == "2026-08-03 15:20:30 UTC"
    )
    assert _format_timestamp(None) == "—"
