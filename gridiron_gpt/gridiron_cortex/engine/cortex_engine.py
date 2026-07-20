from gridiron_cortex.models.engine_result import EngineResult
from gridiron_cortex.transforms.player_intelligence_builder import (
    PlayerIntelligenceBuilder,
)

class CortexEngine:
    def __init__(
        self,
        entity_resolver,
        signal_processor,
        relationship_engine,
        score_engine,
        recommendation_engine,
        player_snapshot_factory,
        explanation_engine,
        event_repository=None,
        prediction_engine=None,
    ):
        self.entity_resolver = entity_resolver
        self.signal_processor = signal_processor
        self.relationship_engine = relationship_engine
        self.score_engine = score_engine
        self.recommendation_engine = recommendation_engine
        self.explanation_engine = explanation_engine
        self.event_repository = event_repository
        self.prediction_engine = prediction_engine
        self.player_intelligence_builder = PlayerIntelligenceBuilder() 
        self.player_snapshot_factory = player_snapshot_factory

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

        entities = self.entity_resolver.resolve(event)
        signal = self.signal_processor.process(event, entities)
        impacts = self.relationship_engine.propagate(signal)

        (
            score_updates,
            player_scorecards,
            scorecard_history,
        ) = self.score_engine.apply(
            signal,
            impacts,
        )

        predictions = []

        if self.prediction_engine is not None:
            predictions = [
                self.prediction_engine.predict(scorecard)
                for scorecard in player_scorecards
            ]

        recommendations = self.recommendation_engine.generate(
            score_updates,
            predictions=predictions,
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
            impacts,
            recommendations,
            predictions=predictions,
        )

        evidence_chains = (
            self.explanation_engine.build_evidence_chains(
                signal=signal,
                impacts=impacts,
                predictions=predictions,
                recommendations=recommendations,
            )
        )

        evidence_graphs = (
            self.explanation_engine.build_evidence_graphs(
                signal=signal,
                impacts=impacts,
                predictions=predictions,
                recommendations=recommendations,
            )
        )

        return EngineResult(
            event=event,
            entities=entities,
            signal=signal,
            impacts=impacts,
            score_updates=score_updates,

            player_scorecards=player_scorecards,
            player_snapshots=player_snapshots,
            scorecard_history=scorecard_history,

            predictions=predictions,
            recommendations=recommendations,

            evidence_chains=evidence_chains,
            evidence_graphs=evidence_graphs,

            explanation=explanation,
        )
