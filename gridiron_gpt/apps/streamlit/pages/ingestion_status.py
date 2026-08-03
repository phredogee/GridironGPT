from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from gridiron_gpt.ingestion.services.ingestion_run_repository import (
    JsonlIngestionRunRepository,
)


def _format_timestamp(value: str | None) -> str:
    if not value:
        return "—"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.strftime("%Y-%m-%d %H:%M:%S UTC")
    except ValueError:
        return value


def _status_label(status: str | None) -> str:
    normalized = (status or "unknown").lower()
    return {
        "healthy": "Healthy",
        "degraded": "Degraded",
        "unavailable": "Unavailable",
    }.get(normalized, normalized.title())


def _render_provider_diagnostic(item: dict[str, Any]) -> None:
    source = item.get("source_name") or "Unknown provider"
    status = _status_label(item.get("status"))
    attempts = item.get("attempts", 0)
    records = item.get("records_received", 0)
    events = item.get("events_created", 0)

    st.markdown(f"#### {source}")
    cols = st.columns(4)
    cols[0].metric("Health", status)
    cols[1].metric("Attempts", attempts)
    cols[2].metric("Records", records)
    cols[3].metric("Events", events)

    error_type = item.get("error_type")
    error_message = item.get("error_message")
    if error_type or error_message:
        st.warning(
            f"{error_type or 'Provider error'}: "
            f"{error_message or 'No additional details.'}"
        )


def render_ingestion_status(
    repository: JsonlIngestionRunRepository | None = None,
) -> None:
    """Render persisted Phase C ingestion observability information."""

    repository = repository or JsonlIngestionRunRepository()
    runs = repository.load_all()

    st.markdown("### Ingestion Operations")
    st.caption(
        "Phase C provider health, reliability, and persisted ingestion-run history."
    )

    if not runs:
        st.info(
            "No persisted ingestion runs are available yet. "
            "Run the unified ingestion service to populate operational history."
        )
        return

    latest = runs[-1]
    success = bool(latest.get("success", False))

    st.markdown("### Latest Run")

    status_col, providers_col, records_col, events_col, duration_col = st.columns(5)
    status_col.metric("Run Status", "Healthy" if success else "Attention")
    providers_col.metric(
        "Providers",
        latest.get("providers_attempted", 0),
        delta=(
            f"{latest.get('providers_failed', 0)} failed"
            if latest.get("providers_failed", 0)
            else "all successful"
        ),
    )
    records_col.metric("Records", latest.get("records_received", 0))
    events_col.metric("Events", latest.get("events_created", 0))
    duration_col.metric(
        "Duration",
        f"{float(latest.get('duration_seconds', 0.0)):.2f}s",
    )

    st.caption(
        f"Run ID: `{latest.get('run_id', 'unknown')}` · "
        f"Started: {_format_timestamp(latest.get('started_at'))} · "
        f"Completed: {_format_timestamp(latest.get('completed_at'))}"
    )

    st.divider()
    st.markdown("### Provider Diagnostics")

    diagnostics = latest.get("diagnostics") or []
    if diagnostics:
        for item in diagnostics:
            _render_provider_diagnostic(item)
            st.divider()
    else:
        st.info("No provider diagnostics were recorded for the latest run.")

    st.markdown("### Recent Run History")
    recent = list(reversed(runs[-10:]))
    rows = []
    for run in recent:
        rows.append(
            {
                "Started": _format_timestamp(run.get("started_at")),
                "Status": "Healthy" if run.get("success") else "Attention",
                "Providers": run.get("providers_attempted", 0),
                "Failed": run.get("providers_failed", 0),
                "Records": run.get("records_received", 0),
                "Events": run.get("events_created", 0),
                "Duration (s)": round(float(run.get("duration_seconds", 0.0)), 3),
            }
        )

    st.dataframe(rows, use_container_width=True, hide_index=True)
