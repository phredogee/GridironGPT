from dataclasses import dataclass


@dataclass(frozen=True)
class RelationshipSemantic:
    """Propagation behavior for one relationship type.

    Multipliers describe how a positive or negative source signal affects
    the relationship target.

    A negative multiplier reverses the signal direction. For example, a
    positive signal about one competitor may negatively affect another.
    """

    relationship_type: str
    positive_multiplier: float = 1.0
    negative_multiplier: float = 1.0
    description: str = ""

    def multiplier_for(self, impact_score: float) -> float:
        if impact_score > 0:
            return self.positive_multiplier

        if impact_score < 0:
            return self.negative_multiplier

        return 0.0


class RelationshipSemantics:
    """Registry of semantic propagation rules.

    Unknown relationship types use neutral multipliers so existing
    relationship data retains its current behavior.
    """

    DEFAULT = RelationshipSemantic(
        relationship_type="default",
        positive_multiplier=1.0,
        negative_multiplier=1.0,
        description="Preserve the relationship's configured strength.",
    )

    def __init__(
        self,
        semantics: dict[str, RelationshipSemantic] | None = None,
    ) -> None:
        self._semantics = self._default_semantics()

        if semantics:
            for relationship_type, semantic in semantics.items():
                self.register(
                    relationship_type=relationship_type,
                    semantic=semantic,
                )

    def get(
        self,
        relationship_type: str | None,
    ) -> RelationshipSemantic:
        key = self.normalize_type(relationship_type)

        return self._semantics.get(key, self.DEFAULT)

    def register(
        self,
        relationship_type: str,
        semantic: RelationshipSemantic,
    ) -> None:
        key = self.normalize_type(relationship_type)

        if not key:
            raise ValueError("relationship_type cannot be empty")

        self._semantics[key] = semantic

    def calculate_multiplier(
        self,
        relationship_type: str | None,
        impact_score: float,
    ) -> float:
        semantic = self.get(relationship_type)

        return semantic.multiplier_for(impact_score)

    @staticmethod
    def normalize_type(
        relationship_type: str | None,
    ) -> str:
        if not relationship_type:
            return ""

        return (
            relationship_type
            .strip()
            .casefold()
            .replace("-", "_")
            .replace(" ", "_")
        )

    @staticmethod
    def _default_semantics() -> dict[str, RelationshipSemantic]:
        return {
            "passes_to": RelationshipSemantic(
                relationship_type="passes_to",
                positive_multiplier=1.00,
                negative_multiplier=0.85,
                description=(
                    "Quarterback performance generally moves receivers "
                    "in the same direction."
                ),
            ),
            "throws_to": RelationshipSemantic(
                relationship_type="throws_to",
                positive_multiplier=1.00,
                negative_multiplier=0.85,
                description=(
                    "Passing performance generally moves receiving "
                    "options in the same direction."
                ),
            ),
            "hands_off_to": RelationshipSemantic(
                relationship_type="hands_off_to",
                positive_multiplier=0.70,
                negative_multiplier=0.60,
                description=(
                    "Quarterback and offensive context influence rushing "
                    "opportunity with moderate strength."
                ),
            ),
            "teammate": RelationshipSemantic(
                relationship_type="teammate",
                positive_multiplier=0.35,
                negative_multiplier=0.35,
                description=(
                    "General teammate effects are weaker than direct "
                    "role relationships."
                ),
            ),
            "plays_for": RelationshipSemantic(
                relationship_type="plays_for",
                positive_multiplier=0.45,
                negative_multiplier=0.45,
                description=(
                    "Team-level changes moderately affect individual "
                    "players."
                ),
            ),
            "coached_by": RelationshipSemantic(
                relationship_type="coached_by",
                positive_multiplier=0.50,
                negative_multiplier=0.55,
                description=(
                    "Coaching changes can alter usage, efficiency, and "
                    "role stability."
                ),
            ),
            "backs_up": RelationshipSemantic(
                relationship_type="backs_up",
                positive_multiplier=-0.25,
                negative_multiplier=-0.65,
                description=(
                    "A starter's improvement reduces backup opportunity, "
                    "while starter decline can increase it."
                ),
            ),
            "competes_with": RelationshipSemantic(
                relationship_type="competes_with",
                positive_multiplier=-0.45,
                negative_multiplier=-0.45,
                description=(
                    "Competitors usually move in opposite opportunity "
                    "directions."
                ),
            ),
            "target_competitor": RelationshipSemantic(
                relationship_type="target_competitor",
                positive_multiplier=-0.40,
                negative_multiplier=-0.40,
                description=(
                    "Additional target share for one receiver often "
                    "reduces opportunity for another."
                ),
            ),
            "depth_chart_competitor": RelationshipSemantic(
                relationship_type="depth_chart_competitor",
                positive_multiplier=-0.50,
                negative_multiplier=-0.50,
                description=(
                    "Depth-chart competitors generally have opposing "
                    "opportunity effects."
                ),
            ),
        }
