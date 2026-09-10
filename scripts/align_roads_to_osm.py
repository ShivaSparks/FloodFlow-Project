"""Generate OSM-aligned prototype road geometry for the flood overlay.

The simulator keeps its stable synthetic road IDs, while each line is routed
between the same endpoints through the real OSM road network using OSRM.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "processed" / "05_roads_boundaries" / "synthetic_roads.geojson"
TARGET = ROOT / "frontend" / "public" / "data" / "osm_aligned_roads.geojson"
OSRM = "https://router.project-osrm.org/route/v1/driving"


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    features: list[dict] = []
    with httpx.Client(timeout=30) as client:
        for feature in source["features"]:
            coordinates = feature["geometry"]["coordinates"]
            start, end = coordinates[0], coordinates[-1]
            url = f"{OSRM}/{start[0]},{start[1]};{end[0]},{end[1]}"
            response = client.get(url, params={"overview": "full", "geometries": "geojson"})
            response.raise_for_status()
            route = response.json()["routes"][0]
            features.append({
                "type": "Feature",
                "properties": {
                    **feature["properties"],
                    "source": "OSM via OSRM",
                    "osm_distance_m": route["distance"],
                },
                "geometry": route["geometry"],
            })
    TARGET.write_text(json.dumps({"type": "FeatureCollection", "name": "osm_aligned_flood_roads", "features": features}), encoding="utf-8")
    print(f"Wrote {len(features)} OSM-aligned roads to {TARGET}")


if __name__ == "__main__":
    try:
        main()
    except (httpx.HTTPError, KeyError, IndexError) as exc:
        print(f"OSM alignment failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
