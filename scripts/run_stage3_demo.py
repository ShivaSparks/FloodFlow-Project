from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.model.drainage_graph import DrainageGraph
from backend.app.model.flood_prediction import BaselineFloodModel
from backend.app.model.simulator import FloodSimulator


def main() -> int:
    processed = ROOT / "data" / "processed"
    drainage = DrainageGraph.from_csv(
        processed / "02_drainage_network" / "drainage_nodes_SYNTHETIC.clean.csv",
        processed / "02_drainage_network" / "drainage_edges_SYNTHETIC.clean.csv",
    )
    model = BaselineFloodModel(
        processed / "03_elevation_dem" / "synthetic_dem_100m.tif",
        processed / "05_roads_boundaries" / "synthetic_roads.geojson",
        drainage,
    )
    simulator = FloodSimulator(
        model,
        processed / "04_rainfall" / "synthetic_nowcast_3h.csv",
    )
    outputs = []
    while not simulator.finished:
        outputs.append(simulator.advance())
    target = ROOT / "data" / "generated" / "stage3_demo_predictions.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(outputs, indent=2), encoding="utf-8")
    print(f"Generated {len(outputs)} simulation steps")
    print(f"Output: {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
