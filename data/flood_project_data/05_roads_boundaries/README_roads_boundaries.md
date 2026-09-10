# Roads, ward boundaries, and drainage maps

Could not pull these directly (they live on portals outside this
environment's allowed network list), but all are free and quick to grab
yourself:

## Road network (for your 2D surface routing + navigation/reroute API)
- **OpenStreetMap via Geofabrik**: https://download.geofabrik.de/asia/india.html
  → download the Southern Zone extract (`southern-zone-latest-free.shp.zip`),
  then clip to this belt's bounding box (south=12.90, north=13.00,
  west=80.18, east=80.245) in QGIS (Vector → Geoprocessing → Clip) or with
  `osmium extract` / `ogr2ogr -clipsrc`.
- Alternative: query the **Overpass API** directly for just this bbox —
  no download needed, e.g. via `overpass-turbo.eu` with a query like
  `way["highway"](12.90,80.18,13.00,80.245); out geom;`

## Ward boundaries (Zone 14/15 wards covering this belt: ~177-179, 189-191)
- **OpenCity Urban Data Portal**: https://data.opencity.in/dataset/gcc-ward-information
  — GCC Ward/Zone maps (2022), KML format.
- **GCC's own ArcGIS REST server**: `https://gis.chennaicorporation.gov.in/server/rest/services/`
  — Greater Chennai Corporation publishes boundary + flooding layers here.
  Browse it in a normal web browser or load the REST endpoint directly into
  QGIS as an ArcGIS Map Service layer.

## Stormwater drain (SWD) maps — for digitizing your real drainage graph
- **OpenCity**: https://data.opencity.in/dataset/chennai-stormwater-drain-swd-maps
  — GCC's ward-wise SWD maps (published for 114 of 200 wards as PDF/KML).
  Look specifically for **wards 177, 178, 179 (Velachery)** and **189, 190, 191
  (Pallikaranai)** — these cover your belt. These are scanned/vector maps,
  not attributed graph data, so you'll need to manually trace manhole
  points and pipe segments in QGIS to build a real nodes/edges table (use
  `02_drainage_network/drainage_nodes_SYNTHETIC.csv` as your target schema).

## Building footprints / impervious surface (optional, for runoff coefficient)
- **Microsoft Building Footprints (India)**: https://github.com/microsoft/GlobalMLBuildingFootprints
  (directly cloneable/downloadable via GitHub — this one IS reachable from
  this environment if you want me to pull the India tile index next)
- **ESA WorldCover 10m** (land cover / impervious surface classification):
  https://esa-worldcover.org/en
