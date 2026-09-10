from __future__ import annotations

import json
import math
from pathlib import Path

import httpx

from ..schemas import RouteRequest
from ..api.simulator import get_simulator

OSRM_URL = "https://router.project-osrm.org/route/v1"
ROOT = Path(__file__).resolve().parents[3]
ROAD_FILE = ROOT / "frontend" / "public" / "data" / "osm_aligned_roads.geojson"
HOTSPOTS = ((80.2181, 12.9815), (80.199, 12.937), (80.201, 12.944))


def _distance_m(a: list[float], b: list[float]) -> float:
    lat_m = 111_000
    lon_m = 111_000 * max(math.cos(math.radians((a[1] + b[1]) / 2)), 0.2)
    return math.hypot((a[0] - b[0]) * lon_m, (a[1] - b[1]) * lat_m)


def _road_features() -> list[dict]:
    try:
        return json.loads(ROAD_FILE.read_text(encoding="utf-8")).get("features", [])
    except (OSError, json.JSONDecodeError):
        return []


def _route_risk(route: dict, payload: RouteRequest) -> tuple[float, list[str], int]:
    """Score an OSRM route using the selected synthetic forecast layer."""
    simulator = get_simulator()
    selected = min(simulator.preview_timeline(), key=lambda step: abs(step["simulation_time_minutes"] - payload.forecast_lead_minutes))
    risk_by_road = {item["road_id"]: item for item in selected.get("predictions", [])}
    max_depth = max((float(item.get("predicted_depth_cm", 0)) for item in risk_by_road.values()), default=0)
    # Keep this consistent with MapView's animated flood-water polygons.
    hazard_radius_m = (0.0018 + min(max_depth / 500.0, 0.009)) * 111_000
    coordinates = route.get("geometry", {}).get("coordinates", [])
    sampled_route = coordinates[::max(1, len(coordinates) // 80)]
    hazard_hits = sum(1 for point in sampled_route if any(_distance_m(list(point), list(center)) < hazard_radius_m for center in HOTSPOTS))
    affected: list[str] = []
    road_score = 0.0
    for feature in _road_features():
        road_id = str(feature.get("properties", {}).get("road_id", ""))
        prediction = risk_by_road.get(road_id)
        if not prediction:
            continue
        risk = prediction.get("final_risk_level") or prediction.get("risk_level", "safe")
        if risk == "safe":
            continue
        road_points = feature.get("geometry", {}).get("coordinates", [])
        sampled_road = road_points[::max(1, len(road_points) // 80)]
        near_route = any(_distance_m(list(route_point), list(road_point)) < 35 for route_point in sampled_route for road_point in sampled_road)
        if near_route:
            affected.append(road_id)
            road_score += {"watch": 20, "dangerous": 500, "blocked": 2000}.get(risk, 50)
    return road_score + hazard_hits * 800, sorted(set(affected)), hazard_hits


async def get_safe_route(payload: RouteRequest) -> dict:
    profile = "driving" if payload.transport not in {"walking", "cycling"} else payload.transport
    coordinates = f"{payload.start_longitude},{payload.start_latitude};{payload.end_longitude},{payload.end_latitude}"
    url = f"{OSRM_URL}/{profile}/{coordinates}"
    params = {"overview": "full", "geometries": "geojson", "steps": "true", "alternatives": "true"}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, OSError) as exc:
        raise RuntimeError(f"OSRM request failed: {exc}") from exc
    if not data.get("routes"):
        raise RuntimeError(f"OSRM returned no route ({data.get('code', 'unknown')})")
    routes = list(data["routes"])
    initial_scores = [_route_risk(route, payload)[0] for route in routes]
    # The public OSRM server frequently returns only one shortest route. When
    # that route crosses a forecast flood zone, ask OSRM for real road routes
    # through several points outside the zone and choose the least-risk one.
    if min(initial_scores, default=0) > 0:
        simulator = get_simulator()
        selected = min(simulator.preview_timeline(), key=lambda step: abs(step["simulation_time_minutes"] - payload.forecast_lead_minutes))
        max_depth = max((float(item.get("predicted_depth_cm", 0)) for item in selected.get("predictions", [])), default=0)
        radius_m = (0.0018 + min(max_depth / 500.0, 0.009)) * 111_000 + 350
        async with httpx.AsyncClient(timeout=15) as client:
            for center_lon, center_lat in HOTSPOTS:
                for angle in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
                    waypoint = [center_lon + math.cos(angle) * radius_m / (111_000 * max(math.cos(math.radians(center_lat)), 0.2)), center_lat + math.sin(angle) * radius_m / 111_000]
                    detour_url = f"{OSRM_URL}/{profile}/{payload.start_longitude},{payload.start_latitude};{waypoint[0]},{waypoint[1]};{payload.end_longitude},{payload.end_latitude}"
                    try:
                        detour_response = await client.get(detour_url, params={"overview": "full", "geometries": "geojson", "steps": "true"})
                        detour_response.raise_for_status()
                        routes.extend(detour_response.json().get("routes", []))
                    except (httpx.HTTPError, OSError):
                        continue
    scored = [(_route_risk(route, payload), route) for route in routes]
    (score, affected_roads, hazard_hits), route = min(scored, key=lambda item: item[0][0])
    warnings = [f"Route selected for the {payload.forecast_lead_minutes}-minute forecast using flood-risk scoring."]
    if affected_roads:
        warnings.append(f"Avoided high-risk predicted segments where OSRM alternatives were available: {', '.join(affected_roads)}.")
    if hazard_hits:
        warnings.append("The selected route minimizes intersections with simulated flood zones.")
    if len(routes) == 1 and (affected_roads or hazard_hits):
        warnings.append("Only one OSRM route was returned; this prototype cannot guarantee real-world safety.")
    return {"provider": "OSRM + FloodFlow risk scoring", "data_mode": "live_routing_flood_scored", "distance_m": route["distance"], "duration_s": route["duration"], "forecast_lead_minutes": payload.forecast_lead_minutes, "geometry": route["geometry"], "warnings": warnings, "avoided_road_ids": affected_roads, "flood_zone_intersections": hazard_hits}
