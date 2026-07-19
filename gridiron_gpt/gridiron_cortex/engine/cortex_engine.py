from gridiron_cortex.models.engine_result import EngineResult


class CortexEngine:
    def __init__(
        self,
        entity_resolver,
        signal_processor,
        relationship_engine,
        score_engine,
        recommendation_engine,
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
            scorecard_history=scorecard_history,
            predictions=predictions,
            recommendations=recommendations,
            evidence_chains=evidence_chains,
            evidence_graphs=evidence_graphs,
            explanation=explanation,
        )
