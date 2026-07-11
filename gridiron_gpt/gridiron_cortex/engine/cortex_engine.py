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
    ):
        self.entity_resolver = entity_resolver
        self.signal_processor = signal_processor
        self.relationship_engine = relationship_engine
        self.score_engine = score_engine
        self.recommendation_engine = recommendation_engine
        self.explanation_engine = explanation_engine
        self.event_repository = event_repository

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

        recommendations = self.recommendation_engine.generate(
            score_updates
        )

        explanation = self.explanation_engine.explain(
            signal,
            impacts,
            recommendations,
        )

        return EngineResult(
            event=event,
            entities=entities,
            signal=signal,
            impacts=impacts,
            score_updates=score_updates,
            player_scorecards=player_scorecards,
            scorecard_history=scorecard_history,    
            recommendations=recommendations,
            explanation=explanation,
        )
