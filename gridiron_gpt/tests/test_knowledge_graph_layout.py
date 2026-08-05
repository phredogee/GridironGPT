import math

from apps.streamlit.components.knowledge_graph import (
    _GRAPH_HEIGHT,
    _GRAPH_WIDTH,
    _curve_control_point,
    _node_positions,
    _ring_radius,
)
from gridiron_gpt.intelligence.explorer_graph import ExplorerGraph, ExplorerGraphNode


def _graph():
    return ExplorerGraph(
        root_id="root",
        nodes=(
            ExplorerGraphNode("root", "Seed", "DET", True, depth=0),
            ExplorerGraphNode("a", "Alpha", "DET", False, depth=1),
            ExplorerGraphNode("b", "Beta", "DET", False, depth=1),
            ExplorerGraphNode("c", "Gamma", "DET", False, depth=2),
            ExplorerGraphNode("d", "Delta", "DET", False, depth=2),
        ),
        edges=(),
        max_depth=2,
    )


def test_radial_layout_centers_seed_and_separates_hop_rings():
    positions = _node_positions(_graph())
    center = (_GRAPH_WIDTH / 2, _GRAPH_HEIGHT / 2)
    assert positions["root"] == center

    inner = math.hypot(positions["a"][0] - center[0], positions["a"][1] - center[1])
    outer = math.hypot(positions["c"][0] - center[0], positions["c"][1] - center[1])
    assert outer > inner


def test_radial_layout_is_deterministic():
    assert _node_positions(_graph()) == _node_positions(_graph())


def test_ring_radius_expands_with_depth():
    hop_one = _ring_radius(1)
    hop_two = _ring_radius(2)
    assert hop_two[0] > hop_one[0]
    assert hop_two[1] > hop_one[1]


def test_curve_control_point_moves_off_straight_midpoint():
    control = _curve_control_point(0, 0, 100, 0, direction=1)
    assert control[0] == 50
    assert control[1] > 0
