from entity_relationships import propagate_impact

impacts = propagate_impact("Joe Burrow", -10)

for impact in impacts:
    print(
        f"{impact['source']} -> {impact['target']}: "
        f"{impact['propagated_score']} "
        f"({impact['relationship_type']})"
    )
