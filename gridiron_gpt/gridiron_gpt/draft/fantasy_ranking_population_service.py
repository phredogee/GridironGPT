from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from gridiron_gpt.draft.fantasy_ranking_input_adapter import (
    FantasyRankingInputAdapter,
    FantasyRankingSourceValues,
)
from gridiron_gpt.draft.fantasy_ranking_score import (
    FantasyRankingScore,
    FantasyRankingScorer,
)
from gridiron_gpt.football_state.services.player_availability_classifier import (
    PlayerAvailability,
    PlayerAvailabilityClassifier,
)


@dataclass(frozen=True)
class FantasyRankingPopulation:
    overall: list[FantasyRankingScore]
    by_position: dict[str, list[FantasyRankingScore]]


class FantasyRankingPopulationService:
    """Build ranked fantasy populations from current project state."""

    DRAFTABLE_POSITIONS = {"QB", "RB", "WR", "TE"}
    EXCLUDED_AVAILABILITY = {
        PlayerAvailability.RETIRED,
        PlayerAvailability.RELEASED,
    }

    def __init__(
        self,
        player_repository,
        scorecard_repository,
        *,
        adapter: FantasyRankingInputAdapter | None = None,
        scorer: FantasyRankingScorer | None = None,
    ) -> None:
        self.player_repository = player_repository
        self.scorecard_repository = scorecard_repository
        self.adapter = adapter or FantasyRankingInputAdapter()
        self.scorer = scorer or FantasyRankingScorer()

    def build(
        self,
        *,
        historical_points_by_name: dict[str, float] | None = None,
        adp_by_name: dict[str, float] | None = None,
        role_scores_by_player_id: dict[str, float] | None = None,
        role_provenance_by_player_id: dict[str, str] | None = None,
        draft_pool_size: int | None = None,
        limit: int | None = None,
    ) -> FantasyRankingPopulation:
        historical_points_by_name = historical_points_by_name or {}
        adp_by_name = adp_by_name or {}
        role_scores_by_player_id = role_scores_by_player_id or {}
        role_provenance_by_player_id = role_provenance_by_player_id or {}

        historical_by_key = self._normalized_source_map(historical_points_by_name)
        adp_by_key = self._normalized_source_map(adp_by_name)

        players = [
            player
            for player in self.player_repository.all_latest()
            if self._is_draftable(player)
        ]

        historical_max = max(
            (
                historical_by_key[self._name_key(player.player_name)]
                for player in players
                if self._name_key(player.player_name) in historical_by_key
            ),
            default=None,
        )

        scores: list[FantasyRankingScore] = []
        for player in players:
            player_key = self._name_key(player.player_name)
            source_values = FantasyRankingSourceValues(
                historical_points=historical_by_key.get(player_key),
                historical_max_points=historical_max,
                adp=adp_by_key.get(player_key),
                draft_pool_size=draft_pool_size,
                role_score=role_scores_by_player_id.get(player.player_id),
                role_provenance=role_provenance_by_player_id.get(player.player_id),
            )
            scorecard = self.scorecard_repository.get_latest(player.player_id)
            inputs = self.adapter.build(
                player,
                source_values=source_values,
                cortex_scorecard=scorecard,
            )

            try:
                scores.append(self.scorer.score(inputs))
            except ValueError:
                # A player with no primary ranking evidence should not appear
                # merely because they exist in the roster dataset.
                continue

        scores.sort(
            key=lambda row: (
                -row.ranking_score,
                row.player_name.casefold(),
            )
        )

        if limit is not None:
            scores = scores[: max(0, limit)]

        by_position = {
            position: [row for row in scores if row.position == position]
            for position in sorted(self.DRAFTABLE_POSITIONS)
        }

        return FantasyRankingPopulation(
            overall=scores,
            by_position=by_position,
        )

    @staticmethod
    def _name_key(name: str) -> str:
        """Return a conservative cross-source key for a player's display name."""
        value = unicodedata.normalize("NFKD", str(name))
        value = "".join(char for char in value if not unicodedata.combining(char))
        return re.sub(r"[^a-z0-9]", "", value.casefold())

    @classmethod
    def _normalized_source_map(cls, values: dict[str, float]) -> dict[str, float]:
        normalized: dict[str, float] = {}
        for name, value in values.items():
            key = cls._name_key(name)
            if key and key not in normalized:
                normalized[key] = value
        return normalized

    def _is_draftable(self, player) -> bool:
        position = (player.position or "").upper()
        if position not in self.DRAFTABLE_POSITIONS:
            return False

        availability = PlayerAvailabilityClassifier.classify(player)
        return availability not in self.EXCLUDED_AVAILABILITY
