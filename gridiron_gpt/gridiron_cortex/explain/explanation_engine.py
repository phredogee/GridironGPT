from uuid import uuid4

from gridiron_cortex.models.evidence_graph import (
    EvidenceGraph,
    EvidenceNode,
)

from gridiron_cortex.models.evidence_chain import (
    EvidenceChain,
    EvidenceStep,
)


class ExplanationEngine:
    """Convert Cortex output into human-readable and structured explanations."""

    def explain(
        self,
        signal,
        impacts,
        recommendations,
        predictions=None,
        football_context=None,
    ):
        if not recommendations:
            return "No recommendation was generated for this event."

        lines = [
            f"Signal analyzed: {signal.headline}",
            f"Signal sentiment: {signal.sentiment}.",
            f"Signal impact: {signal.impact_score:+.3f}.",
        ]

        evidence = signal.evidence or {}

        evidence_count = int(evidence.get("evidence_count") or 0)
        sources = evidence.get("sources") or []
        methods = evidence.get("methods") or []
        classification = evidence.get("classification")
        reasons = evidence.get("reasons") or []

        if evidence_count:
            lines.append(f"Evidence count: {evidence_count}.")

        if sources:
            lines.append("Sources: " + ", ".join(str(source) for source in sources) + ".")

        if methods:
            lines.append("Methods: " + ", ".join(str(method) for method in methods) + ".")

        if classification:
            lines.append(f"Trend classification: {classification}.")

        for reason in reasons[:3]:
            lines.append(f"Evidence: {reason}")

        predictions_by_name = {
            prediction.entity_name.strip().casefold(): prediction
            for prediction in predictions or []
        }

        for rec in recommendations:
            lines.append(
                f"{rec.entity_name} is a {rec.action} "
                f"with {rec.confidence}% confidence. "
                f"Score movement: {rec.score_delta:+.3f}."
            )

            prediction = predictions_by_name.get(rec.entity_name.strip().casefold())

            if prediction is not None:
                lines.append(
                    f"Forecast: {prediction.projected_trend} "
                    f"over {prediction.horizon_days} days, "
                    f"projected score movement {prediction.score_delta:+.2f}."
                )

        lines.extend(self._football_context_lines(football_context))
        return " ".join(lines)

    @staticmethod
    def _football_context_lines(football_context) -> list[str]:
        if not football_context:
            return []

        lines = []
        for context in football_context.values():
            player = context.player
            availability = context.availability.value
            lines.append(
                f"Football context: {player.player_name} is {availability}."
            )

            if context.next_game is not None:
                location = (context.location or "").lower()
                location_text = f" {location}" if location else ""
                lines.append(
                    f"Next game: Week {context.next_game.week} vs "
                    f"{context.opponent or 'unknown opponent'}{location_text}."
                )

            if context.bye_week is not None:
                lines.append(f"Bye week: {context.bye_week}.")

        return lines

    def build_evidence_chains(self, signal, impacts, predictions, recommendations) -> list[EvidenceChain]:
        impacts_by_name: dict[str, list] = {}
        for impact in impacts:
            key = impact.entity_name.strip().casefold()
            impacts_by_name.setdefault(key, []).append(impact)
        predictions_by_name = {prediction.entity_name.strip().casefold(): prediction for prediction in predictions or []}
        chains = []
        for recommendation in recommendations:
            key = recommendation.entity_name.strip().casefold()
            steps = [EvidenceStep(faculty="Observe", step_type="event", summary=signal.headline, value=signal.impact_score, reasons=self._signal_reasons(signal)), EvidenceStep(faculty="Understand", step_type="signal", summary=f"Classified as {signal.sentiment} {signal.signal_type} signal", value=signal.confidence, reasons=self._signal_reasons(signal))]
            for impact in impacts_by_name.get(key, []):
                steps.append(EvidenceStep(faculty="Reason", step_type=impact.impact_type, summary=self._impact_summary(impact), entity_name=impact.entity_name, value=impact.impact_score, reasons=[impact.reason] if impact.reason else []))
            steps.append(EvidenceStep(faculty="Evaluate", step_type="score_change", summary=f"Score changed by {recommendation.score_delta:+.3f}", entity_name=recommendation.entity_name, value=recommendation.score_delta, reasons=[reason for reason in recommendation.reasons if "forecast:" not in reason.casefold()]))
            prediction = predictions_by_name.get(key)
            if prediction is not None:
                steps.append(EvidenceStep(faculty="Predict", step_type="forecast", summary=f"{prediction.horizon_days}-day outlook: {prediction.projected_trend}", entity_name=prediction.entity_name, value=prediction.projected_score, reasons=prediction.reasons))
            steps.append(EvidenceStep(faculty="Decide", step_type="recommendation", summary=f"{recommendation.action} with {recommendation.confidence}% confidence", entity_name=recommendation.entity_name, value=recommendation.confidence, reasons=recommendation.reasons))
            chains.append(EvidenceChain(entity_name=recommendation.entity_name, action=recommendation.action, confidence=recommendation.confidence, steps=steps))
        return chains

    def build_evidence_graphs(self, signal, impacts, predictions, recommendations) -> list[EvidenceGraph]:
        impacts_by_name: dict[str, list] = {}
        for impact in impacts:
            key = impact.entity_name.strip().casefold()
            impacts_by_name.setdefault(key, []).append(impact)
        predictions_by_name = {prediction.entity_name.strip().casefold(): prediction for prediction in predictions or []}
        graphs = []
        for recommendation in recommendations:
            key = recommendation.entity_name.strip().casefold()
            nodes: list[EvidenceNode] = []
            observe_id = f"observe:{uuid4().hex}"
            understand_id = f"understand:{uuid4().hex}"
            nodes.append(EvidenceNode(node_id=observe_id, faculty="Observe", node_type="event", summary=signal.headline, value=signal.impact_score, reasons=self._signal_reasons(signal), metadata={"sentiment": signal.sentiment, "signal_type": signal.signal_type}))
            nodes.append(EvidenceNode(node_id=understand_id, faculty="Understand", node_type="signal", summary=f"Classified as {signal.sentiment} {signal.signal_type} signal", parents=[observe_id], value=signal.confidence, reasons=self._signal_reasons(signal)))
            parent_ids = [understand_id]
            for impact in impacts_by_name.get(key, []):
                impact_id = f"reason:{uuid4().hex}"
                nodes.append(EvidenceNode(node_id=impact_id, faculty="Reason", node_type=impact.impact_type, summary=self._impact_summary(impact), entity_name=impact.entity_name, parents=[understand_id], value=impact.impact_score, reasons=[impact.reason] if impact.reason else [], metadata={"team": impact.team, "impact_type": impact.impact_type, "hop_count": impact.hop_count, "relationship_strength": impact.relationship_strength, "relationship_confidence": impact.relationship_confidence, "propagation_weight": impact.propagation_weight}))
                parent_ids.append(impact_id)
            evaluate_id = f"evaluate:{uuid4().hex}"
            nodes.append(EvidenceNode(node_id=evaluate_id, faculty="Evaluate", node_type="score_change", summary=f"Score changed by {recommendation.score_delta:+.3f}", entity_name=recommendation.entity_name, parents=parent_ids, value=recommendation.score_delta, reasons=[reason for reason in recommendation.reasons if "forecast:" not in reason.casefold()]))
            decision_parents = [evaluate_id]
            prediction = predictions_by_name.get(key)
            if prediction is not None:
                predict_id = f"predict:{uuid4().hex}"
                nodes.append(EvidenceNode(node_id=predict_id, faculty="Predict", node_type="forecast", summary=f"{prediction.horizon_days}-day outlook: {prediction.projected_trend}", entity_name=prediction.entity_name, parents=[evaluate_id], value=prediction.projected_score, reasons=prediction.reasons, metadata={"current_score": prediction.current_score, "projected_score": prediction.projected_score, "score_delta": prediction.score_delta, "confidence": prediction.confidence}))
                decision_parents.append(predict_id)
            decide_id = f"decide:{uuid4().hex}"
            nodes.append(EvidenceNode(node_id=decide_id, faculty="Decide", node_type="recommendation", summary=f"{recommendation.action} with {recommendation.confidence}% confidence", entity_name=recommendation.entity_name, parents=decision_parents, value=recommendation.confidence, reasons=recommendation.reasons, metadata={"action": recommendation.action, "timeframe": recommendation.timeframe, "recommendation_type": recommendation.recommendation_type}))
            graphs.append(EvidenceGraph(entity_name=recommendation.entity_name, action=recommendation.action, confidence=recommendation.confidence, root_node_ids=[observe_id], terminal_node_ids=[decide_id], nodes=nodes))
        return graphs

    @staticmethod
    def _signal_reasons(signal) -> list[str]:
        evidence = signal.evidence or {}
        reasons = list(evidence.get("reasons") or [])
        reasons.extend(f"Positive indicator: {hit}" for hit in signal.positive_hits)
        reasons.extend(f"Negative indicator: {hit}" for hit in signal.negative_hits)
        return list(dict.fromkeys(reasons))

    @staticmethod
    def _impact_summary(impact) -> str:
        if impact.impact_type != "propagated":
            return f"{impact.entity_name} received a {impact.impact_type} impact"
        details = []
        if impact.hop_count is not None:
            details.append(f"{impact.hop_count}-hop propagation")
        if impact.propagation_weight is not None:
            details.append(f"weight {impact.propagation_weight:+.3f}")
        suffix = ""
        if details:
            suffix = " (" + ", ".join(details) + ")"
        return f"{impact.entity_name} received a propagated impact{suffix}"
