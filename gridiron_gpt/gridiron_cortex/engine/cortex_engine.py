from gridiron_cortex.models.engine_context import EngineContext
from gridiron_cortex.models.engine_result import EngineResult
from gridiron_cortex.evidence.evidence_analyzer import (
    EvidenceAnalyzer,
)
from gridiron_cortex.confidence.confidence_calibrator import (
    ConfidenceCalibrator,
)

class CortexEngine:
    def __init__(
        self,
        entity_resolver,
        player_enrichment,
        signal_processor,
        relationship_engine,
        score_engine,
        recommendation_engine,
        player_snapshot_factory,
        player_intelligence_builder,
        explanation_engine,
        event_repository=None,
        evidence_aggregator=None,
        evidence_analyzer: EvidenceAnalyzer | None = None,
        confidence_calibrator: ConfidenceCalibrator | None = None,
        intelligence_engine=None,
        prediction_engine=None,
        trend_analyzer=None,
        football_context_service=None,
    ):
        self.entity_resolver = entity_resolver
        self.player_enrichment = player_enrichment
        self.signal_processor = signal_processor
        self.relationship_engine = relationship_engine
        self.score_engine = score_engine
        self.recommendation_engine = recommendation_engine
        self.explanation_engine = explanation_engine
        self.event_repository = event_repository
        self.evidence_aggregator = evidence_aggregator
        self.evidence_analyzer = evidence_analyzer
        self.confidence_calibrator = confidence_calibrator
        self.intelligence_engine = intelligence_engine
        self.prediction_engine = prediction_engine
        self.player_intelligence_builder = player_intelligence_builder
        self.player_snapshot_factory = player_snapshot_factory
        self.trend_analyzer = trend_analyzer
        self.football_context_service = football_context_service

    def process_event(self, event):
        if self.event_repository is not None:
            fingerprint = event.fingerprint()

            if self.event_repository.contains(fingerprint):
                print(
                    f"[CORTEX] Duplicate event ignored: "
                    f"{fingerprint[:10]}..."
                )

                return EngineResult(
                    event=event,
                    explanation="Duplicate event ignored.",
                )

            self.event_repository.save(event)

        enriched_event = self.player_enrichment.enrich(event)

        context = EngineContext(
            raw_event=enriched_event,
        )

        if self.evidence_aggregator is not None:
            context.canonical_event = self.evidence_aggregator.add(
                context.raw_event
            )

        context.entities = self.entity_resolver.resolve(
            context.raw_event
        )

        if self.football_context_service is not None:
            for entity in context.entities:
                if entity.entity_type != "player" or not entity.player_id:
                    continue
                football_context = self.football_context_service.for_player(
                    entity.player_id
                )
                if football_context is not None:
                    context.football_context[entity.player_id] = football_context

        signal = self.signal_processor.process(
            context.raw_event,
            context.entities,
            canonical_event=context.canonical_event,
        )

        context.signals.append(signal)

        if (
            self.confidence_calibrator is not None
            and context.evidence_assessment is not None
        ):
            context.confidence_result = (
                self.confidence_calibrator.calibrate(
                    classifier_confidence=signal.confidence,
                    evidence_confidence=(
                        context.evidence_assessment.trust_score
                    ),
                )
            )

            signal.confidence = (
                context.confidence_result.final_confidence
            )

        context.impacts = self.relationship_engine.propagate(
            signal
        )

        (
            context.score_updates,
            player_scorecards,
            scorecard_history,
        ) = self.score_engine.apply(
            signal,
            context.impacts,
        )

        predictions = []

        if self.prediction_engine is not None:
            predictions = [
                self.prediction_engine.predict(scorecard)
                for scorecard in player_scorecards
            ]

        intelligence = None

        if self.intelligence_engine is not None:
            intelligence = self.intelligence_engine.evaluate(context)

        recommendations = self.recommendation_engine.generate(
            context.score_updates,
            predictions=predictions,
            intelligence=intelligence,
        )

        predictions_by_name = {
            prediction.entity_name.strip().casefold(): prediction
            for prediction in predictions
        }

        recommendations_by_name = {
            recommendation.entity_name.strip().casefold(): recommendation
            for recommendation in recommendations
        }

        player_intelligence = [
            self.player_intelligence_builder.build(
                scorecard=scorecard,
                prediction=predictions_by_name.get(
                    scorecard.player_name.strip().casefold()
                ),
                recommendation=recommendations_by_name.get(
                    scorecard.player_name.strip().casefold()
                ),
            )
            for scorecard in player_scorecards
        ]

        player_snapshots = [
            self.player_snapshot_factory.from_intelligence(
                intelligence
            )
            for intelligence in player_intelligence
        ]

        explanation = self.explanation_engine.explain(
            signal,
            context.impacts,
            recommendations,
            predictions=predictions,
        )

        evidence_chains = (
            self.explanation_engine.build_evidence_chains(
                signal=signal,
                impacts=context.impacts,
                predictions=predictions,
                recommendations=recommendations,
            )
        )

        evidence_graphs = (
            self.explanation_engine.build_evidence_graphs(
                signal=signal,
                impacts=context.impacts,
                predictions=predictions,
                recommendations=recommendations,
            )
        )

        return EngineResult(
            event=context.raw_event,
            entities=context.entities,
            signal=signal,
            impacts=context.impacts,
            score_updates=context.score_updates,
            player_scorecards=player_scorecards,
            player_snapshots=player_snapshots,
            scorecard_history=scorecard_history,
            predictions=predictions,
            intelligence=intelligence,
            recommendations=recommendations,
            evidence_chains=evidence_chains,
            evidence_graphs=evidence_graphs,
            evidence_assessment=context.evidence_assessment,
            confidence_result=context.confidence_result,
            canonical_event=context.canonical_event,
            explanation=explanation,
        )
