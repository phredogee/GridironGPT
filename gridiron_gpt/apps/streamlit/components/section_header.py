from __future__ import annotations

from html import escape

import streamlit as st


def inject_section_header_styles() -> None:
    """Apply shared section-header styles."""

    st.markdown(
        """
        <style>
        .cortex-section-header {
            margin-top: 1.25rem;
            margin-bottom: 0.85rem;
        }

        .cortex-section-eyebrow {
            color: #4ade80;
            font-size: 0.72rem;
            font-weight: 750;
            letter-spacing: 0.12em;
            line-height: 1.2;
            text-transform: uppercase;
        }

        .cortex-section-title {
            color: rgba(250, 250, 250, 0.96);
            font-size: 1.35rem;
            font-weight: 750;
            line-height: 1.25;
            margin-top: 0.2rem;
        }

        .cortex-section-description {
            color: rgba(250, 250, 250, 0.60);
            font-size: 0.86rem;
            line-height: 1.5;
            margin-top: 0.25rem;
            max-width: 58rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(
    *,
    label: str,
    title: str,
    description: str | None = None,
) -> None:
    """
    Render a reusable Cortex section heading.

    Args:
        label: Small uppercase eyebrow text.
        title: Main section title.
        description: Optional supporting text.
    """

    safe_label = escape(label)
    safe_title = escape(title)

    description_html = ""

    if description:
        description_html = (
            '<div class="cortex-section-description">'
            f"{escape(description)}"
            "</div>"
        )

    st.markdown(
        f"""
        <div class="cortex-section-header">
            <div class="cortex-section-eyebrow">
                {safe_label}
            </div>

            <div class="cortex-section-title">
                {safe_title}
            </div>

            {description_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
