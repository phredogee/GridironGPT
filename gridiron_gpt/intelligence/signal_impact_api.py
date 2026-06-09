from intelligence.entity_relationships import propagate_impact


def generate_signal_impacts(source_entity: str, signal_score: float) -> dict:
    """
    Public API for converting one source signal into direct and propagated impacts.
    """

    propagated_impacts = propagate_impact(source_entity, signal_score)

    total_propagated_impact = sum(
        impact["propagated_score"] for impact in propagated_impacts
    )

    return {
        "source_entity": source_entity,
        "source_score": signal_score,
        "direct_impact": signal_score,
        "propagated_impacts": propagated_impacts,
        "total_propagated_impact": round(total_propagated_impact, 2),
        "total_system_impact": round(signal_score + total_propagated_impact, 2),
    }


def format_signal_impact_report(source_entity: str, signal_score: float) -> str:
    report = generate_signal_impacts(source_entity, signal_score)

    lines = [
        f"Signal Impact Report: {report['source_entity']}",
        f"Direct Impact: {report['direct_impact']}",
        f"Total Propagated Impact: {report['total_propagated_impact']}",
        f"Total System Impact: {report['total_system_impact']}",
        "",
        "Propagated Impacts:",
    ]

    if not report["propagated_impacts"]:
        lines.append("- No downstream impacts found.")
    else:
        for impact in report["propagated_impacts"]:
            lines.append(
                f"- {impact['target']}: {impact['propagated_score']} "
                f"({impact['relationship_type']})"
            )

    return "\n".join(lines)
