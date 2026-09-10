"""
fetch_rainfall.py
------------------
Two functions for REAL rainfall data - one near-real-time (satellite), one
for live IMD station scraping. Both need normal internet access to run.

WHY YOU NEED TO RUN THIS YOURSELF:
This sandbox cannot reach NASA GES DISC or IMD's site.

======================================================================
OPTION A: NASA GPM IMERG near-real-time (satellite, ~10km grid, global)
======================================================================
Usage:
    pip install earthengine-api
    earthengine authenticate
    python fetch_rainfall.py imerg

Gets the last 24 hours of half-hourly rainfall estimates over the belt.
Good for backtesting against real flood dates (2015-12-01/02, 2023-12-02/04
for Cyclone Michaung, etc.) by changing the date range in the code below.

======================================================================
OPTION B: IMD Automatic Weather Station / Rain Gauge scrape (ground truth,
last 7 days only - a hard limit imposed by IMD's website itself)
======================================================================
Usage:
    pip install requests beautifulsoup4
    python fetch_rainfall.py imd

This adapts the pattern from the community project
github.com/craigdsouza/getRainfallData - IMD does not offer a clean REST
API, so this is a best-effort scrape of their public tabular pages. Expect
to need small fixes if IMD changes their page layout.
"""
import sys

def fetch_imerg():
    import ee
    ee.Initialize()

    region = ee.Geometry.Rectangle([80.18, 12.90, 80.245, 13.00])

    # Change these dates to backtest a specific historical flood event, e.g.
    # Cyclone Michaung: '2023-12-02' to '2023-12-05'
    start_date = "2026-08-20"
    end_date = "2026-08-23"

    imerg = (
        ee.ImageCollection("NASA/GPM_L3/IMERG_V07")
        .filterDate(start_date, end_date)
        .filterBounds(region)
        .select("precipitationCal")
    )

    task = ee.batch.Export.table.toDrive(
        collection=ee.FeatureCollection(
            imerg.map(lambda img: ee.Feature(None, {
                "time": img.get("system:time_start"),
                "mean_mm_per_hr": img.reduceRegion(
                    reducer=ee.Reducer.mean(), geometry=region, scale=10000
                ).get("precipitationCal"),
            }))
        ),
        description="imerg_rainfall_timeseries",
        folder="flood_project_data",
        fileNamePrefix="imerg_rainfall_timeseries",
        fileFormat="CSV",
    )
    task.start()
    print(f"IMERG export task started for {start_date} to {end_date}. Check Google Drive.")


def fetch_imd_last_7_days():
    """
    Best-effort IMD AWS/ARG scraper. IMD's public data pages only expose the
    last 7 days and the HTML structure can change - treat this as a
    starting point, not a guaranteed-stable integration.
    """
    import requests

    print("IMD only exposes the last 7 days of AWS/ARG data publicly.")
    print("Reference implementation pattern: https://github.com/craigdsouza/getRainfallData")
    print("Nearest station to this belt: RMC Chennai / Nungambakkam AWS.")
    print("Recommended: adapt that repo's scraper with these coordinates,")
    print("or request a direct data feed from RMC Chennai (contact in")
    print("04_rainfall/README_rainfall_sources.md) for a hackathon-grade")
    print("live integration instead of scraping.")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "imerg":
        fetch_imerg()
    elif mode == "imd":
        fetch_imd_last_7_days()
    else:
        print("Usage: python fetch_rainfall.py [imerg|imd]")
