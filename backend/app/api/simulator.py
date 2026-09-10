from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from ..model.drainage_graph import DrainageGraph
from ..model.flood_prediction import BaselineFloodModel
from ..model.simulator import FloodSimulator
from .dependencies import require_operator

router = APIRouter(prefix="/simulator", tags=["simulator"])
ROOT = Path(__file__).resolve().parents[3]
_simulator: FloodSimulator | None = None


def _data_file(processed_relative: str, source_relative: str) -> Path:
    """Use generated local data when present, otherwise tracked source data.

    Processed data is intentionally ignored by Git, so a clean deployment
    must be able to initialise from the tracked prototype dataset too.
    """
    processed = ROOT / "data" / "processed" / processed_relative
    if processed.exists():
        return processed
    return ROOT / "data" / "flood_project_data" / source_relative


def get_simulator() -> FloodSimulator:
    global _simulator
    if _simulator is None:
        drainage = DrainageGraph.from_csv(
            _data_file(
                "02_drainage_network/drainage_nodes_SYNTHETIC.clean.csv",
                "02_drainage_network/drainage_nodes_SYNTHETIC.csv",
            ),
            _data_file(
                "02_drainage_network/drainage_edges_SYNTHETIC.clean.csv",
                "02_drainage_network/drainage_edges_SYNTHETIC.csv",
            ),
        )
        model = BaselineFloodModel(
            _data_file(
                "03_elevation_dem/synthetic_dem_100m.tif",
                "03_elevation_dem/synthetic_dem_100m.asc",
            ),
            _data_file(
                "05_roads_boundaries/synthetic_roads.geojson",
                "05_roads_boundaries/synthetic_roads.geojson",
            ),
            drainage,
        )
        _simulator = FloodSimulator(
            model,
            _data_file(
                "04_rainfall/synthetic_nowcast_3h.csv",
                "04_rainfall/synthetic_nowcast_3h.csv",
            ),
        )
    return _simulator


@router.get("/status")
def status() -> dict:
    return get_simulator().snapshot()


@router.post("/start")
def start(_: object = Depends(require_operator)) -> dict:
    return get_simulator().start()


@router.post("/pause")
def pause(_: object = Depends(require_operator)) -> dict:
    return get_simulator().pause()


@router.post("/reset")
def reset(_: object = Depends(require_operator)) -> dict:
    return get_simulator().reset()


@router.post("/advance")
def advance(_: object = Depends(require_operator)) -> dict:
    simulator = get_simulator()
    if simulator.finished:
        raise HTTPException(status_code=409, detail="Simulation is complete; reset it first")
    return simulator.advance()
