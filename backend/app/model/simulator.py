from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .flood_prediction import BaselineFloodModel, load_rainfall_forecast


@dataclass
class SimulationState:
    cursor: int = 0
    paused: bool = True
    simulation_minutes: int = 0
    cumulative_rainfall_mm: float = 0.0


class FloodSimulator:
    def __init__(self, model: BaselineFloodModel, rainfall_path: Path):
        rainfall = load_rainfall_forecast(rainfall_path)
        # Each lead time can contain multiple spatial zones. Use the spatial
        # mean as the city-level interval input instead of silently selecting
        # whichever zone happens to appear first in the CSV.
        self.rainfall = (
            rainfall.groupby("lead_minutes", as_index=False)
            .agg(
                valid_time=("valid_time", "first"),
                forecast_mm_15min=("forecast_mm_15min", "mean"),
                confidence=("confidence", "mean"),
            )
            .sort_values("lead_minutes")
            .reset_index(drop=True)
        )
        self.model = model
        self.state = SimulationState()

    @property
    def finished(self) -> bool:
        return self.state.cursor >= len(self.rainfall)

    def reset(self) -> dict:
        self.model.drainage.state = {
            edge_id: 0.0 for edge_id in self.model.drainage.edge_by_id
        }
        self.state = SimulationState()
        return self.snapshot()

    def start(self) -> dict:
        self.state.paused = False
        return self.snapshot()

    def pause(self) -> dict:
        self.state.paused = True
        return self.snapshot()

    def advance(self) -> dict:
        if self.finished:
            return self.snapshot()
        row = self.rainfall.iloc[self.state.cursor]
        current_rainfall = float(row["forecast_mm_15min"])
        self.state.cumulative_rainfall_mm += current_rainfall
        predictions = self.model.predict_step(
            current_rainfall,
            int(row["lead_minutes"]),
            float(row["confidence"]),
        )
        self.state.cursor += 1
        self.state.simulation_minutes = int(row["lead_minutes"])
        return {
            **self.snapshot(),
            "rainfall_mm_15min": current_rainfall,
            "cumulative_rainfall_mm": round(self.state.cumulative_rainfall_mm, 2),
            "predictions": [asdict(prediction) for prediction in predictions],
        }

    def preview_timeline(self) -> list[dict]:
        """Run the configured synthetic nowcast without changing live state."""
        saved_state = SimulationState(**vars(self.state))
        saved_drainage = dict(self.model.drainage.state)
        try:
            self.reset()
            preview: list[dict] = []
            while not self.finished:
                preview.append(self.advance())
            return preview
        finally:
            self.state = saved_state
            self.model.drainage.state = saved_drainage

    def snapshot(self) -> dict:
        return {
            "simulation_time_minutes": self.state.simulation_minutes,
            "cursor": self.state.cursor,
            "paused": self.state.paused,
            "finished": self.finished,
            "data_mode": "synthetic",
            "is_simulation": True,
        }
