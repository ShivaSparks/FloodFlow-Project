"""
fetch_landcover.py
-------------------
Pulls REAL land-use/land-cover and impervious-surface data for the belt
using Google Earth Engine (free for research/education/nonprofit use).

WHY YOU NEED TO RUN THIS YOURSELF:
Requires a free Earth Engine account (signup: https://earthengine.google.com/signup)
and this sandbox cannot reach Earth Engine's servers.

Usage:
    pip install earthengine-api
    earthengine authenticate      # one-time browser login
    python fetch_landcover.py

Output:
    Exports a GeoTIFF to your Google Drive:
    "chennai_belt_esa_worldcover_10m.tif"

Data source: ESA WorldCover 10m v200 (2021) - global land cover including
built-up/impervious, water, wetland, cropland classes at 10m resolution -
sharp enough to distinguish Pallikaranai marsh boundary from encroaching
built-up area, which is the exact land-use-change story documented in the
Pallikaranai research literature.
"""
import ee

def main():
    ee.Initialize()

    # Bounding box for the belt
    region = ee.Geometry.Rectangle([80.18, 12.90, 80.245, 13.00])

    # ESA WorldCover 10m (2021) - Map band has land cover classes:
    # 10=Tree cover, 20=Shrubland, 30=Grassland, 40=Cropland,
    # 50=Built-up, 60=Bare/sparse veg, 70=Snow/ice, 80=Water,
    # 90=Herbaceous wetland (this is your marsh class!), 95=Mangroves, 100=Moss/lichen
    worldcover = ee.ImageCollection("ESA/WorldCover/v200").first().clip(region)

    task = ee.batch.Export.image.toDrive(
        image=worldcover.select("Map"),
        description="chennai_belt_esa_worldcover_10m",
        folder="flood_project_data",
        fileNamePrefix="chennai_belt_esa_worldcover_10m",
        region=region,
        scale=10,
        crs="EPSG:4326",
    )
    task.start()
    print("Export task started. Check the Earth Engine Tasks tab or your Google Drive.")
    print("Class 50 = built-up/impervious, Class 90 = herbaceous wetland (marsh).")

if __name__ == "__main__":
    main()
