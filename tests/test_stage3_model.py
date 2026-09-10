from pathlib import Path

import numpy as np

from backend.app.model.drainage_graph import DrainageGraph
from backend.app.model.runoff import calculate_runoff, risk_from_depth
from backend.app.model.surface_flow import route_surface_runoff

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def test_runoff_converts_depth_to_volume():
    result = calculate_runoff(10, 1000, 0.9)
    assert result.runoff_depth_mm == 9
    assert result.runoff_volume_m3 == 9


def test_risk_thresholds_are_stable():
    assert risk_from_depth(0) == "safe"
    assert risk_from_depth(10) == "watch"
    assert risk_from_depth(30) == "dangerous"
    assert risk_from_depth(50) == "blocked"


def test_surface_flow_accumulates_toward_low_point():
    dem = np.array([[3.0, 2.0], [2.0, 1.0]])
    result = route_surface_runoff(dem, 10)
    assert result.low_point == (1, 1)
    assert result.accumulation_mm[1, 1] > result.accumulation_mm[0, 0]


def test_drainage_graph_has_clean_edges_and_state():
    graph = DrainageGraph.from_csv(
        PROCESSED / "02_drainage_network" / "drainage_nodes_SYNTHETIC.clean.csv",
        PROCESSED / "02_drainage_network" / "drainage_edges_SYNTHETIC.clean.csv",
    )
    states = graph.update({"N001": 1.0})
    assert len(states) == 18
    assert all(state.edge_id.startswith("E") for state in states)
    assert all(0 <= value <= 1.5 for value in graph.state.values())
