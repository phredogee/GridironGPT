import streamlit as st


def _score(data):
    return data.get("adjusted_score", data.get("score", 0.0))


def render_command_center(
    *,
    ranked_players,
    buy_players,
    watch_players,
    risk_players,
    player_count,
    recommendation_from_score,
    confidence_from_signals,
    passing_tests=13,
):
    
    header_left, header_right = st.columns([4, 1])

    with header_left:
        st.title("🧠 Gridiron Cortex")
        st.markdown("### Football Intelligence Engine")
        st.caption("Running inside GridironGPT")

    with header_right:
        st.metric(
            "Engine Status",
            "ONLINE",
            f"{passing_tests} tests passing",
        )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.success("🧠 Knowledge Graph")

    with c2:
        st.success("🔄 Propagation Planner")

    with c3:
        st.success("⚡ Typed Pipeline")

    st.divider()

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Engine Snapshot")

    m1, m2, m3, m4, m5 = st.columns(5)

    m1.metric(
        "Tracked Players",
        player_count,
        "+0"
    )

    m2.metric(
        "Ranked Players",
        len(ranked_players),
    )

    m3.metric(
        "BUY Signals",
        len(buy_players),
    )

    m4.metric(
        "WATCH Signals",
        len(watch_players),
    )

    m5.metric(
        "Risk Signals",
        len(risk_players),
    )

    st.divider()

    health_col, pipeline_col = st.columns([1, 3])
    
    with health_col:

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Engine Health")

        engines = [
            "Signal Processor",
            "Knowledge Service",
            "Knowledge Graph",
            "Propagation Planner",
            "Relationship Engine",
            "Score Engine",
            "Recommendation Engine",
        ]

        for engine in engines:

            name_col, status_col = st.columns([4,1])

            with name_col:
                st.markdown(f"**{engine}**")

            with status_col:
                st.markdown(
                    "<span style='color:#42d392;'>●</span>",
                    unsafe_allow_html=True,
                )

    with pipeline_col:

        st.subheader("Data Preprocessing")

        pipeline_stages = [
            "Fetch",
            "Clean",
            "Normalize",
            "Entity Resolve",
            "RawEvent",
        ]

        for index, stage in enumerate(pipeline_stages):
            st.markdown(
              f"""
            <div style="
                padding:12px;
                border-radius:10px;
                border:1px solid #2f3948;
                background:#16212d;
                text-align:center;
                font-weight:600;
            ">
            {stage}
            </div>
            """,
                unsafe_allow_html=True,
            )

            if index < len(pipeline_stages) - 1:
                st.markdown(
                    "<div style='text-align:center;color:#7f8c99;font-size:24px;'>↓</div>",
                    unsafe_allow_html=True,
                )

    st.caption(
        "Incoming data is fetched, cleaned, normalized, "
        "entity-resolved, and converted into a RawEvent before "
        "entering the Cortex intelligence engine." 
    )

    st.divider()

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Latest Intelligence")

    if ranked_players:

        for rank, ((player, team), data) in enumerate(
            ranked_players[:6],
            start=1,
        ):

            score = _score(data)
            recommendation = recommendation_from_score(score)
            confidence = confidence_from_signals(
                data.get("signals", [])
            )

            signals = data.get("signals", [])

            if signals:
                latest_signal = signals[-1]

                if isinstance(latest_signal, dict):
                    headline = (
                        latest_signal.get("headline")
                        or latest_signal.get("reason")
                        or latest_signal.get("signal")
                        or "Recent football intelligence update."
                    )
                else:
                    headline = str(latest_signal)
            else:
                headline = "No recent signal details available."

            with st.container(border=True):
                header_col, action_col = st.columns([4, 1])

                with header_col:
                    st.markdown(
                        f"### {rank}. {player} ({team})"
                    )
                    st.caption(headline)

                with action_col:
                    if recommendation == "BUY":
                        st.success(recommendation)
                    elif recommendation == "WATCH":
                        st.warning(recommendation)
                    elif recommendation in {"SELL", "MONITOR"}:
                        st.error(recommendation)
                    else:
                        st.info(recommendation)

                metric_col1, metric_col2, metric_col3 = st.columns(3)

                metric_col1.metric(
                    "Adjusted Score",
                    f"{score:+.1f}",
                )

                metric_col2.metric(
                    "Confidence",
                    f"{confidence}%",
                )

                metric_col3.metric(
                    "Signals",
                    len(signals),
                )

                propagated_impacts = data.get(
                    "propagated_impacts",
                    [],
                )

                if propagated_impacts:
                    with st.expander(
                        "Propagation details",
                        expanded=False,
                    ):
                        for impact in propagated_impacts[:5]:
                            if isinstance(impact, dict):
                                entity_name = (
                                    impact.get("entity_name")
                                    or impact.get("player")
                                    or impact.get("target")
                                    or "Related entity"
                                )

                                impact_score = (
                                    impact.get("impact_score")
                                    or impact.get("score_delta")
                                    or impact.get("impact")
                                )

                                reason = impact.get(
                                    "reason",
                                    "Relationship-based propagation.",
                                )

                                if isinstance(impact_score, (int, float)):
                                    st.write(
                                        f"**{entity_name}** "
                                        f"`{impact_score:+.2f}`"
                                    )
                                else:
                                    st.write(f"**{entity_name}**")

                                st.caption(reason)
                            else:
                                st.write(str(impact))
    else:
        st.info("No ranked player intelligence is currently available.")

        st.divider()

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Future Intelligence")

    a, b, c = st.columns(3)

    with a:
        st.markdown("### 🤖 Roster Advisor")
        st.write(
            "Ask natural language questions about your roster."
        )

    with b:
        st.markdown("### 📈 Three Week Forecast")
        st.write(
            "Find the best waiver pickups over the next three weeks."
        )

    with c:
        st.markdown("### 🌐 Knowledge Graph Explorer")
        st.write(
            "Visualize player relationships across the NFL."
        )
