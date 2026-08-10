from datetime import datetime, timezone

from gridiron_cortex.models.player_scorecard import PlayerScorecard
from gridiron_cortex.models.score_update import ScoreUpdate
from gridiron_cortex.remember.player_scorecard_repository import (
    PlayerScorecardRepository,
)


class ScoreEngine:
    """
    Applies propagated impacts to persistent player scorecards.

    New players begin at a neutral baseline. Existing players continue
    from their latest stored scorecard.
    """

    BASELINE_SCORE = 50.0
    MIN_SCORE = 0.0
    MAX_SCORE = 100.0
    CATEGORY_PROFILES = {
        "general": {
            "opportunity": 1.00,
            "health": 0.00,
            "hype": 1.00,
            "risk": 0.00,
            "momentum": 1.00,
        },
        "injury": {
            "opportunity": 0.60,
            "health": 1.00,
            "hype": 0.20,
            "risk": -1.00,
            "momentum": 0.50,
        },
        "recovery": {
            "opportunity": 0.25,
            "health": 1.00,
            "hype": 0.50,
            "risk": -0.70,
            "momentum": 0.50,
        },
        "opportunity": {
            "opportunity": 1.00,
            "health": 0.00,
            "hype": 0.30,
            "risk": 0.00,
            "momentum": 0.50,
        },
        "depth_chart": {
            "opportunity": 1.00,
            "health": 0.00,
            "hype": 0.40,
            "risk": 0.00,
            "momentum": 0.60,
        },
        "suspension": {
            "opportunity": 0.80,
            "health": 0.00,
            "hype": 0.30,
            "risk": -0.80,
            "momentum": 0.70,
        },
        "performance": {
            "opportunity": 0.40,
            "health": 0.00,
            "hype": 0.70,
            "risk": 0.00,
            "momentum": 1.00,
        },
        "roster": {
            "opportunity": 0.80,
            "health": 0.00,
            "hype": 0.40,
            "risk": 0.20,
            "momentum": 0.60,
        },
    }

    def __init__(
        self,
        repository: PlayerScorecardRepository | None = None,
    ):
        self.repository = repository

    def apply(self, signal, impacts):
        score_updates = []
        player_scorecards = []
        scorecard_history = {}

        for impact in impacts:
            if impact.entity_type != "player":
                continue

            player_id = self._build_player_id(impact.entity_name)
            previous = self._load_or_create_scorecard(
                player_id=player_id,
                player_name=impact.entity_name,
                team=impact.team,
            )

            category = getattr(
                signal,
                "signal_category",
                "general",
            )

            profile = self.CATEGORY_PROFILES.get(
                category,
                self.CATEGORY_PROFILES["general"],
            )

            score_delta = impact.impact_score

            updated = PlayerScorecard(
                player_id=previous.player_id,
                player_name=previous.player_name,
                team=impact.team or previous.team,
                overall_score=self._clamp(
                    previous.overall_score + score_delta
                ),
                opportunity_score=self._clamp(
                    previous.opportunity_score
                    + (
                        score_delta
                        * profile["opportunity"]
                    )
                ),
                health_score=self._clamp(
                    previous.health_score
                    + (
                        score_delta
                        * profile["health"]
                    )
                ),
                hype_score=self._clamp(
                    previous.hype_score
                    + (
                        score_delta
                        * profile["hype"]
                    )
                ),
                risk_score=self._clamp(
                    previous.risk_score
                    + (
                        score_delta
                        * profile["risk"]
                    )
                ),
                momentum_score=self._clamp(
                    previous.momentum_score
                    + (
                        score_delta
                        * profile["momentum"]
                    )
                ),
                last_updated=datetime.now(timezone.utc).isoformat(),
            )

            score_updates.append(
                ScoreUpdate(
                    entity_type=impact.entity_type,
                    entity_name=impact.entity_name,
                    team=updated.team,
                    previous_score=previous.overall_score,
                    score_delta=score_delta,
                    new_score=updated.overall_score,
                    score_category="overall",
                    reason=impact.reason,
                )
            )

            if self.repository is not None:
                self.repository.save(updated)

                scorecard_history[player_id] = (
                    self.repository.get_history(player_id)
                )
            else:
                scorecard_history[player_id] = [updated]

            player_scorecards.append(updated)

        return (
            score_updates,
            player_scorecards,
            scorecard_history
        )

    def _load_or_create_scorecard(
        self,
        player_id: str,
        player_name: str,
        team: str | None,
    ) -> PlayerScorecard:
        if self.repository is not None:
            existing = self.repository.get_latest(player_id)

            if existing is not None:
                return existing

        return PlayerScorecard(
            player_id=player_id,
            player_name=player_name,
            team=team,
            overall_score=self.BASELINE_SCORE,
            opportunity_score=self.BASELINE_SCORE,
            health_score=self.BASELINE_SCORE,
            hype_score=self.BASELINE_SCORE,
            risk_score=self.BASELINE_SCORE,
            momentum_score=self.BASELINE_SCORE,
            last_updated=None,
        )

    @staticmethod
    def _build_player_id(player_name: str) -> str:
        return player_name.strip().lower().replace(" ", "_")

    def _clamp(self, score: float) -> float:
        return max(self.MIN_SCORE, min(self.MAX_SCORE, score))
