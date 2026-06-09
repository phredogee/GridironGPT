import json
from pathlib import Path

REQUIRED_FIELDS = {
    "target",
    "relationship_type",
    "multiplier"
}


def validate_relationships(data):
    for source_player, relationships in data.items():

        if not isinstance(relationships, list):
            raise ValueError(
                f"{source_player} relationships must be a list"
            )

        for relationship in relationships:

            missing = REQUIRED_FIELDS - relationship.keys()

            if missing:
                raise ValueError(
                    f"{source_player}: missing fields {missing}"
                )

            if not isinstance(
                relationship["multiplier"],
                (int, float)
            ):
                raise ValueError(
                    f"{source_player}: multiplier must be numeric"
                )

def load_relationships():

    data_file = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "relationships.json"
    )

    with open(data_file, "r") as f:
        data = json.load(f)

    validate_relationships(data)

    return data
