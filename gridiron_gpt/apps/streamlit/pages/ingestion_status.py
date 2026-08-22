from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from gridiron_gpt.ingestion.freshness import evaluate_ingestion_freshness
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


def _format_age(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    minutes = max(0, int(seconds // 60))
    if minutes < 60:
        return f"{minutes}m ago"
    hours, remainder = divmod(minutes, 60)
    if hours < 48:
        return f"{hours}h {remainder}m ago"
    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h ago"


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

    st.markdown(f"#### {source}")
    cols = st.columns(4)
    cols[0].metric("Health", status)
    cols[1].metric("Attempts", item.get("attempts", 0))
    cols[2].metric("Records", item.get("records_received", 0))
    cols[3].metric("Normalized", item.get("events_created", 0))

    cortex_cols = st.columns(3)
    cortex_cols[0].metric("New Cortex Events", item.get("cortex_events_accepted", 0))
    cortex_cols[1].metric("Duplicates Ignored", item.get("cortex_duplicates_ignored", 0))
    cortex_cols[2].metric("Processor Failures", item.get("processor_failures", 0))

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
    """Render persisted ingestion, freshness, and Cortex-boundary observability."""

    repository = repository or JsonlIngestionRunRepository()
    runs = repository.load_all()
    freshness = evaluate_ingestion_freshness(runs)

    st.markdown("### Ingestion Operations")
    st.caption(
        "Provider health, daily data freshness, persisted run history, and Cortex processing outcomes."
    )

    freshness_cols = st.columns(3)
    freshness_cols[0].metric("Data Freshness", freshness.label)
    freshness_cols[1].metric(
        "Last Updated",
        _format_timestamp(freshness.completed_at.isoformat() if freshness.completed_at else None),
    )
    freshness_cols[2].metric(
        "Update Age",
        _format_age(freshness.age.total_seconds() if freshness.age is not None else None),
    )

    if freshness.status == "stale":
        st.warning("The latest successful ingestion run is older than the daily freshness window.")
    elif freshness.status == "failed":
        st.error("The most recent ingestion run failed or completed with provider failures.")
    elif freshness.status == "missing":
        st.info(
            "No persisted ingestion runs are available yet. "
            "Run the unified ingestion service to populate operational history."
        )
        return

    latest = max(
        runs,
        key=lambda run: str(run.get("completed_at") or ""),
    )
    success = bool(latest.get("success", False))

    st.markdown("### Latest Run")
    status_col, providers_col, duration_col = st.columns(3)
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
    duration_col.metric("Duration", f"{float(latest.get('duration_seconds', 0.0)):.2f}s")

    flow_cols = st.columns(5)
    flow_cols[0].metric("Records Received", latest.get("records_received", 0))
    flow_cols[1].metric("Events Normalized", latest.get("events_created", 0))
    flow_cols[2].metric("New Cortex Events", latest.get("cortex_events_accepted", 0))
    flow_cols[3].metric("Duplicates Ignored", latest.get("cortex_duplicates_ignored", 0))
    flow_cols[4].metric("Processor Failures", latest.get("processor_failures", 0))

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
    recent = sorted(
        runs,
        key=lambda run: str(run.get("completed_at") or ""),
        reverse=True,
    )[:10]
    rows = []
    for run in recent:
        rows.append(
            {
                "Started": _format_timestamp(run.get("started_at")),
                "Status": "Healthy" if run.get("success") else "Attention",
                "Providers": run.get("providers_attempted", 0),
                "Failed": run.get("providers_failed", 0),
                "Records": run.get("records_received", 0),
                "Normalized": run.get("events_created", 0),
                "New Cortex": run.get("cortex_events_accepted", 0),
                "Duplicates": run.get("cortex_duplicates_ignored", 0),
                "Processor Failures": run.get("processor_failures", 0),
                "Duration (s)": round(float(run.get("duration_seconds", 0.0)), 3),
            }
        )

    st.dataframe(rows, use_container_width=True, hide_index=True)
