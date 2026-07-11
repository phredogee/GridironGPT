from gridiron_cortex.facade import CortexFacade

cortex = CortexFacade()

graph = cortex.get_entity_graph(
    entity_id="cj_stroud",
    max_depth=2,
)

print("=" * 60)
print("KNOWLEDGE GRAPH")
print("=" * 60)

print("\nNodes:")
for node in graph.nodes:
    print(node)

print("\nEdges:")
for edge in graph.edges:
    print(edge)

print("\nAffected Entities:")
for node in cortex.get_affected_entities(
    entity_id="cj_stroud",
    max_depth=2,
):
    print(node)

print("\nRelationship Paths:")
paths = cortex.find_relationship_paths(
    source_entity_id="cj_stroud",
    target_entity_id="tank_dell",
    max_depth=3,
)

for path in paths:
    print("-" * 40)
    print(f"Hops: {path.hop_count}")
    print(f"Strength: {path.combined_strength:.4f}")
    print(f"Confidence: {path.combined_confidence:.4f}")

    for relationship in path.relationships:
        print(
            f"{relationship.source_entity_name} "
            f"-> "
            f"{relationship.target_entity_name}"
        )
