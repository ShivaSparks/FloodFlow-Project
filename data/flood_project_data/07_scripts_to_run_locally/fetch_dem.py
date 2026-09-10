"""
fetch_dem.py
------------
Downloads a REAL, free, high(er)-resolution DEM for the Velachery-
Pallikaranai-Medavakkam belt from OpenTopography's public API.

WHY YOU NEED TO RUN THIS YOURSELF:
This sandbox cannot reach portal.opentopography.org (network is locked to
code-repository domains only). Get a free API key (instant, no approval
wait) at https://portal.opentopography.org/myopentopo then run this.

Usage:
    pip install requests
    python fetch_dem.py YOUR_API_KEY

Output:
    dem_velachery_pallikaranai_medavakkam.tif   (Copernicus GLO-30, 30m)

To get a sharper DEM instead, change DEM_TYPE to "SRTMGL1" (SRTM 30m) or
if you have opentopography access to the finer NASADEM, use "NASADEM".
"""
import sys
import requests

BBOX = dict(south=12.90, north=13.00, west=80.18, east=80.245)
DEM_TYPE = "COP30"  # Copernicus GLO-30, generally sharper than SRTM over flat urban terrain

def fetch(api_key):
    url = "https://portal.opentopography.org/API/globaldem"
    params = {
        "demtype": DEM_TYPE,
        "south": BBOX["south"],
        "north": BBOX["north"],
        "west": BBOX["west"],
        "east": BBOX["east"],
        "outputFormat": "GTiff",
        "API_Key": api_key,
    }
    print("Requesting DEM tile for bbox:", BBOX)
    resp = requests.get(url, params=params, timeout=120)
    resp.raise_for_status()

    out_path = "dem_velachery_pallikaranai_medavakkam.tif"
    with open(out_path, "wb") as f:
        f.write(resp.content)
    print(f"Saved DEM to {out_path} ({len(resp.content)/1024:.0f} KB)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetch_dem.py YOUR_API_KEY")
        print("Get a free key at https://portal.opentopography.org/myopentopo")
        sys.exit(1)
    fetch(sys.argv[1])
