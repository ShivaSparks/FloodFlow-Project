from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RunoffResult:
    rainfall_mm: float
    runoff_coefficient: float
    runoff_depth_mm: float
    runoff_volume_m3: float


def calculate_runoff(
    rainfall_mm: float,
    area_m2: float,
    runoff_coefficient: float,
) -> RunoffResult:
    if rainfall_mm < 0:
        raise ValueError("rainfall_mm must be non-negative")
    if area_m2 <= 0:
        raise ValueError("area_m2 must be positive")
    if not 0 <= runoff_coefficient <= 1:
        raise ValueError("runoff_coefficient must be between 0 and 1")
    runoff_depth_mm = rainfall_mm * runoff_coefficient
    runoff_volume_m3 = runoff_depth_mm / 1000.0 * area_m2
    return RunoffResult(
        rainfall_mm=rainfall_mm,
        runoff_coefficient=runoff_coefficient,
        runoff_depth_mm=runoff_depth_mm,
        runoff_volume_m3=runoff_volume_m3,
    )


def risk_from_depth(depth_cm: float) -> str:
    if depth_cm < 10:
        return "safe"
    if depth_cm < 30:
        return "watch"
    if depth_cm < 50:
        return "dangerous"
    return "blocked"
