import streamlit as st


def render_confidence_panel(result):
    """Render evidence quality and calibrated confidence metrics."""

    st.markdown("### Evidence & Confidence")

    assessment = result.evidence_assessment
    calibration = result.confidence_result
    canonical_event = result.canonical_event

    if assessment is None and calibration is None:
        st.info("No evidence assessment or confidence calibration available.")
        return

    if calibration is not None:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Classifier Confidence",
                f"{calibration.classifier_confidence:.1%}",
            )

        with col2:
            st.metric(
                "Evidence Trust",
                f"{calibration.evidence_confidence:.1%}",
            )

        with col3:
            st.metric(
                "Calibrated Confidence",
                f"{calibration.final_confidence:.1%}",
            )

        st.caption(calibration.explanation)

    if assessment is not None:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Consensus",
                assessment.consensus_level
                .replace("_", " ")
                .title(),
            )

        with col2:
            st.metric(
                "Agreement",
                f"{assessment.agreement_score:.1%}",
            )

        with col3:
            st.metric(
                "Conflict",
                f"{assessment.conflict_score:.1%}",
            )

        with col4:
            st.metric(
                "Independent Sources",
                assessment.independent_source_count,
            )

        story_status = (
            "Developing"
            if assessment.developing_story
            else "Established"
        )

        st.write(f"**Story Status:** {story_status}")

    if canonical_event is not None and canonical_event.evidence:
        with st.expander("Supporting Sources", expanded=False):
            for evidence in canonical_event.evidence:
                st.markdown(
                    f"**{evidence.source}** — {evidence.headline}"
                )

                details = []

                if evidence.category:
                    details.append(
                        evidence.category.replace("_", " ").title()
                    )

                if evidence.subtype:
                    details.append(
                        evidence.subtype.replace("_", " ").title()
                    )

                if evidence.confidence is not None:
                    details.append(
                        f"{evidence.confidence:.1%} confidence"
                    )

                if details:
                    st.caption(" · ".join(details))

                if evidence.url:
                    st.markdown(f"[View source]({evidence.url})")
