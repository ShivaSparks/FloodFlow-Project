from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SurfaceFlowResult:
    accumulation_mm: np.ndarray
    downstream: dict[tuple[int, int], tuple[int, int] | None]
    low_point: tuple[int, int]


def _lowest_neighbor(dem: np.ndarray, row: int, col: int) -> tuple[int, int] | None:
    rows, cols = dem.shape
    candidates: list[tuple[float, int, int]] = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = row + dr, col + dc
            if 0 <= nr < rows and 0 <= nc < cols and dem[nr, nc] < dem[row, col]:
                candidates.append((float(dem[nr, nc]), nr, nc))
    if not candidates:
        return None
    _, nr, nc = min(candidates)
    return nr, nc


def route_surface_runoff(dem: np.ndarray, runoff_depth_mm: float) -> SurfaceFlowResult:
    if dem.ndim != 2:
        raise ValueError("DEM must be a two-dimensional array")
    if not np.isfinite(dem).all():
        raise ValueError("DEM contains non-finite values")
    if runoff_depth_mm < 0:
        raise ValueError("runoff_depth_mm must be non-negative")

    downstream: dict[tuple[int, int], tuple[int, int] | None] = {}
    accumulation = np.full(dem.shape, runoff_depth_mm, dtype=float)
    cells = sorted(
        (
            (float(dem[row, col]), row, col)
            for row in range(dem.shape[0])
            for col in range(dem.shape[1])
        ),
        reverse=True,
    )
    for _, row, col in cells:
        target = _lowest_neighbor(dem, row, col)
        downstream[(row, col)] = target
        if target is not None:
            accumulation[target] += accumulation[row, col]
    low_point = tuple(
        int(value) for value in np.unravel_index(np.argmin(dem), dem.shape)
    )
    return SurfaceFlowResult(
        accumulation_mm=accumulation, downstream=downstream, low_point=low_point
    )


def sample_grid(array: np.ndarray, row: int, col: int) -> float:
    row = max(0, min(array.shape[0] - 1, row))
    col = max(0, min(array.shape[1] - 1, col))
    return float(array[row, col])
