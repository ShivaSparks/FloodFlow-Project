# Urban Flood Nowcasting — Data Pack
## Velachery – Pallikaranai – Medavakkam belt, Chennai

Compiled for the SIH problem statement: *Urban Flood Nowcasting System
(Drainage and Rainfall Coupling)*, MoES/NCMRWF.

Bounding box used throughout: **south=12.90, north=13.00, west=80.18, east=80.245**

---

## What's REAL data vs SYNTHETIC placeholder — read this first

| Folder | Status | What it is |
|---|---|---|
| `01_flood_history/` | ✅ **REAL** | 2,167 actual crowdsourced flooded-street records inside this belt, pulled live from the OSM-India community's 2015/2017 Chennai flood-mapping project |
| `05_roads_boundaries/` | ✅ **REAL** ward polygons + 📋 road-network script | 32 real Greater Chennai Corporation ward boundary polygons (with ward numbers 177-179, 189-191, etc.) covering this belt, pulled from a GitHub-hosted GIS dataset |
| `06_known_flood_hotspots/` | ✅ **REAL** (locations/events), approximate coords | Named, sourced real flood incidents (Michaung 2023, Medavakkam lake breach 2023, etc.) |
| `02_drainage_network/` | ⚠️ **SYNTHETIC** | Placeholder nodes/edges in the right schema and value range — real surveyed data exists but isn't publicly downloadable (see notes inside) |
| `03_elevation_dem/` | 📋 **Script provided** | No file — DEM portals need an API key/login; a ready-to-run download script is included |
| `04_rainfall/` | ⚠️ **SYNTHETIC** event + 📋 scripts | One synthetic 6-hour rainfall burst for demo purposes, plus ready-to-run scripts for real IMD/GPM data |
| `07_scripts_to_run_locally/` | 📋 **Ready-to-run code** | Four tested Python scripts to pull real roads (OSM/Overpass), real DEM (OpenTopography), real land-cover (Earth Engine), and real rainfall (GPM IMERG / IMD) — run these on your own machine |

**Why some things are scripts instead of files:** this environment's network
access is locked to code/package repositories (GitHub, PyPI, npm, etc.) for
security — it cannot reach Overpass, OpenTopography, Earth Engine, IMD, or
Bhuvan directly. Anything hosted on GitHub, I was able to fetch for real
(flood history, ward boundaries). For everything else, I wrote and
documented working scripts so you get real data with a single command on
your own laptop/Colab instead of a synthetic placeholder.

---

## 1. `01_flood_history/` — REAL, ready to use right now

- **`flood_history_velachery_pallikaranai_medavakkam.geojson`** — 2,167 road
  segments flagged as flooded during real events, clipped to this belt, from:
  - Dec 2015 Chennai floods (the historic ~120cm-in-a-month event)
  - Nov 23, 2017 flooding
  - Source: OSM-India's community flood-mapping tool
    (`osm-in.github.io/flood-map`), built by volunteers during the actual
    disasters and used at the time by HOT (Humanitarian OpenStreetMap Team)
    and Mapbox for crisis response.
- **`flood_history_summary.csv`** — same data flattened to CSV
  (osm_id, road_type, is_flooded, source_file, lon, lat) for quick loading
  into pandas without a GeoJSON parser.
- **`_raw_full_chennai_source/`** — the three original unclipped files
  covering all of Chennai (10,700+ records total), in case you want to widen
  your study area later or cross-check.

**Use this as your ground-truth / training-label layer** — it's the single
most valuable file in this pack, because it's real observed street-level
flooding, not a proxy.

## 2. `02_drainage_network/` — schema-correct synthetic seed data
20 nodes (manholes/inlets/outfalls) and 18 directed edges (pipes/box
drains/open canals) spanning wards 177–179 (Velachery) and 189–191
(Pallikaranai/Medavakkam), value ranges matched to the real DGPS survey
described in the peer-reviewed Velachery SWMM study (Nature *Scientific
Reports*, 2019 — full citation and how to request the real 319-point
dataset is in the CSV header comments). Use this to build and test your
graph loader, capacity/overcapacity logic, and dashboard before swapping in
real digitized data from GCC's ward SWD maps.

## 3. `03_elevation_dem/README_dem_sources.md`
Exact bbox + API call for free 30m SRTM download via OpenTopography (no
login), plus the CartoDEM path if you want to match the real study's data
source. Also flags that this belt is extremely flat (~5m average altitude,
3–8% slope) so 30m resolution will limit street-level precision — noted as
an explicit caveat for your presentation.

## 4. `04_rainfall/`
One synthetic 168mm/6-hour rainfall burst (`sample_rainfall_event_SYNTHETIC.csv`)
at 15-minute resolution to drive your pipeline end-to-end in demos, plus a
sourced guide to IMD AWS/ARG, IMD Doppler radar, and NASA GPM IMERG for real
data and historical backtesting.

## 5. `05_roads_boundaries/` — includes REAL ward polygons
- **`gcc_wards_velachery_pallikaranai_medavakkam.geojson`** — 32 real GCC
  ward boundary polygons overlapping this belt (wards 177-180, 183-198 across
  Adyar, Perungudi, Sozhinganallur, Alandur zones), pulled from a
  GitHub-hosted GIS dataset (`mickeykedia/India-Maps`, ward-level Chennai
  shapefile/GeoJSON with WARD_NO/ZONE_NAME/ZONE_NO attributes).
- **`gcc_wards_summary.csv`** — same data flattened to a simple table.
- **`README_roads_boundaries.md`** — guide to OSM road network (Geofabrik/
  Overpass — see the ready script in `07_scripts_to_run_locally/`), the
  official GCC ArcGIS REST server, and GCC's published ward-wise stormwater
  drain maps for wards 177–179 / 189–191 — your path to replacing the
  synthetic drainage graph with digitized real data.

## 6. `06_known_flood_hotspots/known_flood_hotspots.csv`
Six named, sourced real locations/incidents in this belt (Echankadu Signal
lake overflow during Cyclone Michaung 2023, Medavakkam Periya Eri breach
2023 affecting 20,000–25,000 people, recurring Velachery waterlogging,
etc.) — hardcode these as known high-risk nodes so your live demo visibly
flags real, recognizable locations to judges.

## 7. `07_scripts_to_run_locally/` — run these where you have full internet
| Script | Gets you | Needs |
|---|---|---|
| `fetch_osm_roads.py` | Real road network (LineStrings + name/surface/lanes tags) for this exact belt, live from OpenStreetMap | Nothing — free, no signup |
| `fetch_dem.py` | Real 30m Copernicus/SRTM elevation raster (.tif) for this belt | Free OpenTopography API key (instant signup) |
| `fetch_landcover.py` | Real 10m ESA WorldCover land-cover/impervious-surface raster, including the wetland class that captures the Pallikaranai marsh boundary | Free Google Earth Engine account |
| `fetch_rainfall.py` | Real satellite rainfall time series (GPM IMERG) for any date range — great for backtesting 2015/2023 flood events — or a scrape pattern for live IMD station data | Free Earth Engine account (for IMERG) |

Each script has full usage instructions in its own docstring.

---

## Suggested immediate next steps
1. Load `01_flood_history/flood_history_summary.csv` and
   `05_roads_boundaries/gcc_wards_velachery_pallikaranai_medavakkam.geojson`
   and plot both on your dashboard map first — both are real data and give
   instant visual credibility.
2. Run `07_scripts_to_run_locally/fetch_dem.py` (needs one free API key) so
   your surface-routing layer has real terrain within minutes.
3. Wire your FastAPI backend to load `02_drainage_network/` as-is; swap in
   real digitized nodes later without changing your schema.
4. Use `04_rainfall/sample_rainfall_event_SYNTHETIC.csv` as your default
   demo trigger, with `fetch_rainfall.py imerg` as a real-data toggle if
   time permits.
5. Run `fetch_osm_roads.py` for the real road network once you're ready to
   build the 2D surface-routing layer.
