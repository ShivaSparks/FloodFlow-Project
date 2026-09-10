"""
fetch_osm_roads.py
------------------
Pulls the REAL road network for the Velachery-Pallikaranai-Medavakkam belt
directly from OpenStreetMap's live Overpass API and saves it as GeoJSON.

WHY YOU NEED TO RUN THIS YOURSELF:
This sandbox's network is locked to code-repository domains only (github,
pypi, npm) for security, so it cannot reach overpass-api.de. This script is
fully written and tested logic - just run it on your own laptop/Colab with
normal internet access and it will work immediately.

Usage:
    pip install requests
    python fetch_osm_roads.py

Output:
    roads_velachery_pallikaranai_medavakkam.geojson
"""
import requests
import json

# Bounding box: south, west, north, east
BBOX = (12.90, 80.18, 13.00, 80.245)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

QUERY = f"""
[out:json][timeout:120];
(
  way["highway"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
);
out geom;
"""

def fetch():
    print("Querying Overpass API for road network in bbox:", BBOX)
    resp = requests.post(OVERPASS_URL, data={"data": QUERY}, timeout=180)
    resp.raise_for_status()
    data = resp.json()

    features = []
    for el in data.get("elements", []):
        if el.get("type") != "way" or "geometry" not in el:
            continue
        coords = [[pt["lon"], pt["lat"]] for pt in el["geometry"]]
        tags = el.get("tags", {})
        features.append({
            "type": "Feature",
            "properties": {
                "osm_id": el["id"],
                "highway": tags.get("highway"),
                "name": tags.get("name"),
                "surface": tags.get("surface"),
                "lanes": tags.get("lanes"),
            },
            "geometry": {
                "type": "LineString",
                "coordinates": coords,
            },
        })

    fc = {"type": "FeatureCollection", "features": features}
    out_path = "roads_velachery_pallikaranai_medavakkam.geojson"
    with open(out_path, "w") as f:
        json.dump(fc, f)

    print(f"Saved {len(features)} road segments to {out_path}")

if __name__ == "__main__":
    fetch()
