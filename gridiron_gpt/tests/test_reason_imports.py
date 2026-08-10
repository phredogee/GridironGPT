def test_propagation_planner_imports_without_circular_dependency():
    from gridiron_cortex.propagation.propagation_planner import PropagationPlanner

    assert PropagationPlanner is not None


def test_relationship_engine_remains_available_from_reason_package():
    from gridiron_cortex.reason import RelationshipEngine

    assert RelationshipEngine is not None
