from gridiron_cortex.understand.event_taxonomy import EVENT_RULES


def test_every_event_rule_has_required_fields() -> None:
    required = {
        "category",
        "subtype",
        "polarity",
        "impact",
        "confidence",
        "phrases",
    }

    for rule in EVENT_RULES:
        missing = required.difference(rule)
        assert not missing, (
            f"{rule.get('category', '<missing>')}."
            f"{rule.get('subtype', '<missing>')} missing fields: "
            f"{sorted(missing)}"
        )


def test_every_event_rule_has_at_least_one_phrase() -> None:
    for rule in EVENT_RULES:
        assert rule["phrases"], (
            f"{rule['category']}.{rule['subtype']} must define at least one phrase"
        )
