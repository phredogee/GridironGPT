from __future__ import annotations

from dataclasses import dataclass

from gridiron_cortex.models.player_scorecard import PlayerScorecard
from gridiron_gpt.draft.fantasy_ranking_score import FantasyRankingInputs
from gridiron_gpt.football_state.models.player_state import CanonicalPlayerState
from gridiron_gpt.football_state.services.player_availability_classifier import (
    PlayerAvailability,
    PlayerAvailabilityClassifier,
)


@dataclass(frozen=True)
class FantasyRankingSourceValues:
    """Raw source values used to assemble normalized fantasy-ranking inputs."""

    historical_points: float | None = None
    historical_max_points: float | None = None
    adp: float | None = None
    draft_pool_size: int | None = None
    role_score: float | None = None
    role_provenance: str | None = None
    projection_score: float | None = None


class FantasyRankingInputAdapter:
    """Translate project data into normalized FantasyRankingInputs.

    The adapter intentionally preserves missing values as None. It does not
    fabricate neutral data for sources that are not yet available.
    """

    AVAILABILITY_SCORES = {
        PlayerAvailability.AVAILABLE: 100.0,
        PlayerAvailability.RESERVE: 35.0,
        PlayerAvailability.UNAVAILABLE: 10.0,
        PlayerAvailability.RETIRED: 0.0,
        PlayerAvailability.RELEASED: 0.0,
        PlayerAvailability.EXEMPT: 25.0,
    }

    def build(
        self,
        player_state: CanonicalPlayerState,
        *,
        source_values: FantasyRankingSourceValues | None = None,
        cortex_scorecard: PlayerScorecard | None = None,
    ) -> FantasyRankingInputs:
        source_values = source_values or FantasyRankingSourceValues()

        baseline_score = self._baseline_score(
            source_values.historical_points,
            source_values.historical_max_points,
        )
        market_score = self._market_score(
            source_values.adp,
            source_values.draft_pool_size,
        )
        role_score = self._clamp_optional(source_values.role_score)
        projection_score = self._clamp_optional(source_values.projection_score)
        cortex_score = (
            self._clamp_optional(cortex_scorecard.overall_score)
            if cortex_scorecard is not None
            else None
        )

        availability = PlayerAvailabilityClassifier.classify(player_state)
        availability_score = self.AVAILABILITY_SCORES.get(availability)

        provenance: dict[str, str] = {}
        if baseline_score is not None:
            provenance["baseline"] = "weighted historical fantasy production"
        if market_score is not None:
            provenance["market"] = "ADP normalized across configured draft pool"
        if role_score is not None:
            provenance["role"] = source_values.role_provenance or "explicit roster/depth role assessment"
        if cortex_score is not None:
            provenance["cortex"] = "latest Cortex player scorecard overall_score"
        if availability_score is not None:
            provenance["availability"] = f"canonical football state: {availability.value}"
        if projection_score is not None:
            provenance["projection"] = "position-normalized projected fantasy production"

        return FantasyRankingInputs(
            player_id=player_state.player_id,
            player_name=player_state.player_name,
            team=player_state.team,
            position=player_state.position,
            baseline_score=baseline_score,
            market_score=market_score,
            role_score=role_score,
            cortex_score=cortex_score,
            availability_score=availability_score,
            projection_score=projection_score,
            provenance=provenance,
        )

    @staticmethod
    def _baseline_score(
        historical_points: float | None,
        historical_max_points: float | None,
    ) -> float | None:
        if historical_points is None or historical_max_points is None:
            return None
        if historical_max_points <= 0:
            return None
        return FantasyRankingInputAdapter._clamp_optional(
            (historical_points / historical_max_points) * 100.0
        )

    @staticmethod
    def _market_score(
        adp: float | None,
        draft_pool_size: int | None,
    ) -> float | None:
        if adp is None or draft_pool_size is None or draft_pool_size <= 0:
            return None
        if adp <= 0:
            return 100.0
        score = ((draft_pool_size - adp + 1) / draft_pool_size) * 100.0
        return FantasyRankingInputAdapter._clamp_optional(score)

    @staticmethod
    def _clamp_optional(value: float | None) -> float | None:
        if value is None:
            return None
        return max(0.0, min(100.0, float(value)))
