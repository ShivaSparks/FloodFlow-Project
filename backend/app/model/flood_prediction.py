from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import pandas as pd
import rasterio

from .drainage_graph import DrainageEdgeState, DrainageGraph
from .runoff import calculate_runoff, risk_from_depth
from .surface_flow import route_surface_runoff, sample_grid


@dataclass(frozen=True)
class RoadPrediction:
    road_id: str
    predicted_depth_cm: float
    risk_level: str
    drainage_utilization: float
    confidence: float
    forecast_minutes: int


class BaselineFloodModel:
    def __init__(
        self,
        dem_path: Path,
        roads_path: Path,
        drainage: DrainageGraph,
        runoff_coefficient: float = 0.9,
    ):
        self.dem_path = dem_path
        self.roads = gpd.read_file(roads_path).to_crs("EPSG:4326")
        self.drainage = drainage
        self.runoff_coefficient = runoff_coefficient
        with rasterio.open(dem_path) as dataset:
            self.dem = dataset.read(1).astype(float)
            self.transform = dataset.transform
            self.cell_area_m2 = abs(dataset.transform.a * dataset.transform.e) * (
                111_000**2
            )

    def _road_cell(self, lon: float, lat: float) -> tuple[int, int]:
        col, row = ~self.transform * (lon, lat)
        return round(row), round(col)

    def predict_step(
        self, rainfall_mm: float, lead_minutes: int, rainfall_confidence: float = 0.7
    ) -> list[RoadPrediction]:
        runoff = calculate_runoff(
            rainfall_mm, self.cell_area_m2, self.runoff_coefficient
        )
        surface = route_surface_runoff(self.dem, runoff.runoff_depth_mm)
        total_capacity = (
            sum(
                float(data["capacity_cumecs"])
                for _, _, data in self.drainage.graph.edges(data=True)
            )
            or 1.0
        )
        total_inflow = runoff.runoff_volume_m3 / 900.0
        graph_states: list[DrainageEdgeState] = self.drainage.update(
            {
                node: total_inflow / max(len(self.drainage.graph.nodes), 1)
                for node in self.drainage.graph.nodes
            }
        )
        # Report demand against nominal capacity, including the graph's
        # rolling storage state. Keep the prototype state bounded at 150% so
        # this remains a capacity-utilization metric, not an exploding score.
        max_utilization = min(
            1.5,
            max(
                (max(state.utilization, state.storage_fraction) for state in graph_states),
                default=total_inflow / total_capacity,
            ),
        )
        predictions: list[RoadPrediction] = []
        for _, road in self.roads.iterrows():
            row, col = self._road_cell(
                float(road.geometry.centroid.x), float(road.geometry.centroid.y)
            )
            accumulated_mm = sample_grid(surface.accumulation_mm, row, col)
            depth_cm = max(
                0.0, accumulated_mm / 10.0 * (1.0 + max(0.0, max_utilization - 1.0))
            )
            confidence = max(
                0.1,
                min(
                    0.99, rainfall_confidence * (0.9 if self.dem.size < 1000 else 0.75)
                ),
            )
            predictions.append(
                RoadPrediction(
                    str(road["road_id"]),
                    round(depth_cm, 2),
                    risk_from_depth(depth_cm),
                    round(max_utilization, 3),
                    round(confidence, 3),
                    lead_minutes,
                )
            )
        return predictions


def load_rainfall_forecast(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    frame["valid_time"] = pd.to_datetime(frame["valid_time"], utc=True)
    frame["forecast_mm_15min"] = pd.to_numeric(
        frame["forecast_mm_15min"], errors="raise"
    )
    return frame.sort_values(["lead_minutes", "zone_id"]).reset_index(drop=True)
