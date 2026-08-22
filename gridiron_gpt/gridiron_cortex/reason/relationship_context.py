from dataclasses import dataclass


@dataclass(frozen=True)
class RelationshipContext:
    """Contextual relationship policy derived from signal evidence.

    The policy controls which relationship types are relevant for propagation.
    It never changes the source signal magnitude, so secondary classifications
    cannot create additional direct scoring contributions.
    """

    allowed_relationship_types: frozenset[str] | None = None

    def allows(self, relationship_type: str | None) -> bool:
        if self.allowed_relationship_types is None:
            return True
        return self.normalize_type(relationship_type) in self.allowed_relationship_types

    @staticmethod
    def normalize_type(relationship_type: str | None) -> str:
        if not relationship_type:
            return ""
        return relationship_type.strip().casefold().replace("-", "_").replace(" ", "_")


class RelationshipContextPolicy:
    """Map structured event classifications to relevant graph relationships."""

    CLASSIFICATION_RELATIONSHIPS = {
        ("depth_chart", "first_team_reps"): {
            "backs_up",
            "competes_with",
            "target_competitor",
            "depth_chart_competitor",
        },
        ("depth_chart", "promoted"): {
            "backs_up",
            "competes_with",
            "target_competitor",
            "depth_chart_competitor",
        },
        ("depth_chart", "demoted"): {
            "backs_up",
            "competes_with",
            "target_competitor",
            "depth_chart_competitor",
        },
        ("injury", "returned_to_practice"): {
            "backs_up",
            "competes_with",
            "depth_chart_competitor",
        },
        ("injury", "full_practice"): {
            "backs_up",
            "competes_with",
            "depth_chart_competitor",
        },
        ("injury", "injured_reserve"): {
            "backs_up",
            "competes_with",
            "depth_chart_competitor",
        },
        ("injury", "placed_on_pup"): {
            "backs_up",
            "competes_with",
            "depth_chart_competitor",
        },
    }

    def from_signal(self, signal) -> RelationshipContext:
        classifications = signal.evidence.get("event_classifications", [])
        if not classifications:
            return RelationshipContext()

        allowed: set[str] = set()
        has_context_rule = False

        for classification in classifications:
            key = (
                str(classification.get("category", "")).casefold(),
                str(classification.get("subtype", "")).casefold(),
            )
            relationship_types = self.CLASSIFICATION_RELATIONSHIPS.get(key)
            if relationship_types is None:
                continue
            has_context_rule = True
            allowed.update(relationship_types)

        if not has_context_rule:
            return RelationshipContext()

        return RelationshipContext(
            allowed_relationship_types=frozenset(allowed)
        )
