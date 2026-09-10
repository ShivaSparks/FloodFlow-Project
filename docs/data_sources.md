# FloodFlow Stage 1 data sources

The source pack is kept under `data/flood_project_data/` and is never modified
by the preparation scripts.

## Real data

- `01_flood_history/`: historical flooded-street records.
- `05_roads_boundaries/`: GCC ward boundary polygons.
- `06_known_flood_hotspots/`: named, approximate historical incidents.

## Synthetic data

- `02_drainage_network/`: illustrative drainage nodes and edges.
- `03_elevation_dem/synthetic_dem_100m.asc`: artificial basin DEM.
- `04_rainfall/`: synthetic rainfall event and synthetic nowcast.
- `05_roads_boundaries/synthetic_roads.geojson`: representative road lines.
- `05_roads_boundaries/synthetic_landcover_runoff.csv`: illustrative runoff coefficients.

## Stage 1 output policy

Validation reports, cleaned CSVs, normalized GeoJSON, and normalized rasters
are written to `data/processed/`. Original data remains unchanged. Processed
outputs are local build artifacts and are ignored by Git.
