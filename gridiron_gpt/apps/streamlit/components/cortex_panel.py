from contextlib import contextmanager

import streamlit as st


@contextmanager
def cortex_panel(
    title: str,
    subtitle: str | None = None,
    *,
    panel_class: str = "",
):
    """
    Render a reusable Cortex-styled panel.

    Usage:

        with cortex_panel(
            "Input Event",
            "Analyze a football event through Cortex.",
        ):
            st.text_input(...)
    """

    classes = "cortex-ui-panel"

    if panel_class:
        classes = f"{classes} {panel_class}"

    st.html(
        f"""
        <div class="{classes}">
            <div class="cortex-ui-panel-header">
                <div>
                    <div class="cortex-ui-panel-title">
                        {title}
                    </div>
                    {
                        f'''
                        <div class="cortex-ui-panel-subtitle">
                            {subtitle}
                        </div>
                        '''
                        if subtitle
                        else ""
                    }
                </div>
            </div>
        </div>
        """
    )

    with st.container():
        yield
